"""China-aware quality scoring for proxy nodes.

GitHub Actions 能连 ≠ 大陆能连。GFW 对直连境外 `server:port` 的
阻断是主要差异。本模块用可本地计算的启发式打分，优选抗封锁形态，
并与 validator 的实测 latency 结合做 Top-N 截断。

设计原则：
- REALITY / WS+TLS+CDN > 裸 SS/直连
- 标准化 443 端口 > 随机高位端口
- 有 SNI/指纹 > 无
"""

from typing import Any

import requests

# GFW 友好端口（Cloudflare/标准 HTTPS）
FAVORED_PORTS = {443, 8443, 2053, 2083, 2087, 2096, 2052, 2056, 4430}
# REALITY 常用伪装域名（越主流越不易被主动探测）
POPULAR_SNI_HINTS = (
    "apple.com",
    "microsoft.com",
    "google.com",
    "yahoo.com",
    "cloudflare.com",
    "www.microsoft.com",
    "www.apple.com",
    "www.cloudflare.com",
)


def _port_score(port: int | None) -> int:
    if not port:
        return 0
    if port == 443:
        return 10
    if port in FAVORED_PORTS:
        return 6
    # 高位随机端口在大陆被限速/QoS 概率更高
    if port > 10000:
        return -2
    return 0


def _tls_score(node: dict[str, Any]) -> int:
    tls = node.get("tls") or {}
    if not tls.get("enabled"):
        return -5  # 无 TLS 的裸节点大陆存活率极低
    score = 0
    if tls.get("server_name"):
        score += 4
        sni = tls["server_name"].lower()
        if any(h in sni for h in POPULAR_SNI_HINTS):
            score += 3
    if tls.get("reality", {}).get("enabled"):
        score += 12  # REALITY 抗封锁最强
    if tls.get("utls", {}).get("enabled"):
        score += 3
    # insecure=True 意味着自签名，大陆部分网络会拦截
    if tls.get("insecure"):
        score -= 2
    return score


def _transport_score(node: dict[str, Any]) -> int:
    tr = node.get("transport") or {}
    t = tr.get("type", "")
    if t == "ws":
        # WS over CDN 若 Host 是泛解析或 workers.dev 等，GFW 识别成本高
        host = (tr.get("headers") or {}).get("Host", "")
        if host and ("workers.dev" in host or "cdn" in host.lower()):
            return 6
        return 4
    if t == "grpc":
        return 3
    if t == "http":
        return 1
    # 无 transport 的直连 VLESS/SS 最易被识别
    return -3


def _protocol_score(node: dict[str, Any]) -> int:
    ntype = node.get("type", "").lower()
    # QUIC 系大陆 QoS 严重，但抗 TCP 阻断有优势，折中
    if ntype in ("hysteria2", "hy2"):
        return 5
    if ntype == "tuic":
        return 4
    if ntype == "vless":
        return 6
    if ntype == "vmess":
        return 2
    if ntype == "trojan":
        return 3
    if ntype == "shadowsocks":
        return -1
    return 0


def china_resistance_score(node: dict[str, Any]) -> int:
    """0-30+ 分，分数越高越适合大陆直连。仅用本地字段，无需网络。"""
    port = node.get("server_port") or node.get("port")
    try:
        port = int(port) if port else None
    except Exception:
        port = None
    return _port_score(port) + _tls_score(node) + _transport_score(node) + _protocol_score(node)


def quality_score(node: dict[str, Any], latency_ms: float | None = None) -> float:
    """综合分 = 抗封锁分*2 - 延迟惩罚。latency_ms 来自 validator 实测。"""
    base = china_resistance_score(node) * 2.0
    if latency_ms is not None:
        # 延迟 <200ms 满分，>1500ms 直接淘汰（validator 已 1.0s 阈值，此处再惩罚）
        if latency_ms > 1000:
            base -= (latency_ms - 1000) / 100.0
        # 快速节点奖励
        if latency_ms < 300:
            base += 5
        elif latency_ms < 600:
            base += 2
    return base


def filter_timeout_outliers(
    nodes: list[dict[str, Any]], latency_key: str = "_latency_ms", max_latency_ms: int = 800
) -> list[dict[str, Any]]:
    """科学剔除 timeout/慢节点：动态阈值 + 统计离群。

    - 硬阈值：> max_latency_ms (默认 800ms，大陆体感) 直接剔除
    - 统计阈值：> P90 且 > 中位数*1.8 的离群点剔除（避免“一刀切”误伤）
    - 无 _latency_ms（未测速）则放行，交由后续 quality 排序
    """
    if not nodes:
        return nodes
    latencies: list[float] = [
        float(n.get(latency_key))  # type: ignore[arg-type]
        for n in nodes
        if isinstance(n.get(latency_key), (int, float))
    ]
    if not latencies:
        return nodes

    # 硬阈值
    hard_filtered: list[dict[str, Any]] = [
        n
        for n in nodes
        if n.get(latency_key) is None or float(n.get(latency_key, 0)) <= max_latency_ms
    ]

    # 统计阈值：P90
    try:
        import statistics

        lat_sorted: list[float] = sorted(float(x) for x in latencies)
        p90_idx = int(len(lat_sorted) * 0.9)
        p90: float = float(lat_sorted[min(p90_idx, len(lat_sorted) - 1)])
        median: float = float(statistics.median(lat_sorted))
        # 离群阈值为 P90 与 median*1.8 取大者，避免在高延迟整体偏高时过度剔除
        outlier_threshold: float = max(p90, median * 1.8, 600.0)
        hard_filtered = [
            n
            for n in hard_filtered
            if n.get(latency_key) is None or float(n.get(latency_key, 0)) <= outlier_threshold
        ]
        # 若统计阈值剔除过多（>30%），说明分布本身分散，回退仅硬阈值
        if len(hard_filtered) < len(nodes) * 0.7:
            return [
                n
                for n in nodes
                if n.get(latency_key) is None or n.get(latency_key, 0) <= max_latency_ms
            ]
    except Exception:
        pass
    return hard_filtered


def filter_by_china_probe(
    nodes: list[dict[str, Any]], probe_url: str, timeout: int = 4, max_workers: int = 20
) -> list[dict[str, Any]]:
    """可选的大陆侧探活：POST {server,port} 到自建探针，仅保留探针返回 ok 的节点。

    探针建议部署在阿里云/腾讯云杭州/深圳轻量，逻辑：`socket.create_connection((server,port), timeout=2)`。
    若探针未配置或失败，返回原列表（不阻断）。
    """
    if not probe_url or not nodes:
        return nodes
    import concurrent.futures

    def _probe(node: dict[str, Any]) -> dict[str, Any] | None:
        server = node.get("server")
        port = node.get("server_port") or node.get("port")
        if not server or not port:
            return None
        try:
            resp = requests.post(
                probe_url, json={"server": server, "port": int(port)}, timeout=timeout
            )
            if resp.status_code == 200:
                data = resp.json() if "json" in resp.headers.get("Content-Type", "") else {}
                # 兼容 {ok:true} 或 {reachable:true}
                if data.get("ok") is True or data.get("reachable") is True:
                    return node
                # 若探针返回非 JSON，按 HTTP 200 视为可达（简化）
                if not data:
                    return node
            return None
        except Exception:
            return None

    kept: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as ex:
        fut2node = {ex.submit(_probe, n): n for n in nodes}
        for fut in concurrent.futures.as_completed(fut2node):
            res = fut.result()
            if res is not None:
                kept.append(res)
    # 探针全失败则回退原列表，避免因探针故障导致 0 节点
    return kept if kept else nodes
