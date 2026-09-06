"""China-aware quality scoring for proxy nodes.

GitHub Actions connectivity does not guarantee connectivity from mainland China.
GFW blocking on direct outbound server:port connections is the primary difference.
This module uses local heuristic scoring to favor anti-censorship configurations
and combines with validator-measured latency for Top-N selection.

Design Principles:
- REALITY / WS+TLS+CDN > Plain SS / direct
- Standard port 443 > High random ports
- SNI / Fingerprint present > absent
"""

from typing import Any

import requests

# Censorship-resilient ports (Cloudflare / standard HTTPS)
FAVORED_PORTS = {443, 8443, 2053, 2083, 2087, 2096, 2052, 2056, 4430}
# Commonly masqueraded SNI domains for REALITY (mainstream domains resist active probing)
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
    # High random ports face higher probability of QoS / throttling
    if port > 10000:
        return -2
    return 0


def _tls_score(node: dict[str, Any]) -> int:
    tls = node.get("tls") or {}
    if not tls.get("enabled"):
        return -5  # Plain nodes without TLS have low survivability
    score = 0
    if tls.get("server_name"):
        score += 4
        sni = tls["server_name"].lower()
        if any(h in sni for h in POPULAR_SNI_HINTS):
            score += 3
    if tls.get("reality", {}).get("enabled"):
        score += 12  # REALITY provides the strongest anti-censorship capability
    if tls.get("utls", {}).get("enabled"):
        score += 3
    # insecure=True indicates self-signed certificate, subject to interception
    if tls.get("insecure"):
        score -= 2
    return score


def _transport_score(node: dict[str, Any]) -> int:
    tr = node.get("transport") or {}
    t = tr.get("type", "")
    if t == "ws":
        # WS over CDN with wildcards or workers.dev increases inspection cost for DPI
        host = (tr.get("headers") or {}).get("Host", "")
        if host and ("workers.dev" in host or "cdn" in host.lower()):
            return 6
        return 4
    if t == "grpc":
        return 3
    if t == "http":
        return 1
    # Direct VLESS/SS without transport encapsulation is easiest to fingerprint
    return -3


def _protocol_score(node: dict[str, Any]) -> int:
    ntype = node.get("type", "").lower()
    # QUIC-based protocols may face UDP QoS, but offer superior TCP RST resistance
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
    """Calculate 0-30+ score where higher values favor direct China connectivity. Pure local heuristic."""
    port = node.get("server_port") or node.get("port")
    try:
        port = int(port) if port else None
    except Exception:
        port = None
    return _port_score(port) + _tls_score(node) + _transport_score(node) + _protocol_score(node)


def quality_score(
    node: dict[str, Any],
    latency_ms: float | None = None,
    longevity_bonus: float = 0.0,
) -> float:
    """Overall score = Censorship score * 2 - Latency penalty + Longevity bonus."""
    base = china_resistance_score(node) * 2.0
    if latency_ms is not None:
        # Latency <200ms yields full score, >1000ms incurs penalty
        if latency_ms > 1000:
            base -= (latency_ms - 1000) / 100.0
        # Fast node reward
        if latency_ms < 300:
            base += 5
        elif latency_ms < 600:
            base += 2
    return base + longevity_bonus


def filter_timeout_outliers(
    nodes: list[dict[str, Any]], latency_key: str = "_latency_ms", max_latency_ms: int = 500
) -> list[dict[str, Any]]:
    """Filter out latency outliers exceeding max_latency_ms (default 500ms).

    Un-benchmarked nodes (latency None) are retained and ranked by quality score.
    """
    if not nodes:
        return nodes
    return [
        n
        for n in nodes
        if n.get(latency_key) is None or float(n.get(latency_key, 0)) <= max_latency_ms
    ]


def filter_by_china_probe(
    nodes: list[dict[str, Any]], probe_url: str, timeout: int = 4, max_workers: int = 20
) -> list[dict[str, Any]]:
    """Optional China-side probe: POST {server, port} to probe endpoint, keeping only responsive nodes.

    Falls back to original node list if probe is unreachable or unconfigured.
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
                # Compatible with {ok: true} or {reachable: true}
                if data.get("ok") is True or data.get("reachable") is True:
                    return node
                # Fallback on HTTP 200 if response is non-JSON
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
    # If all probe requests fail, return original list to avoid dropping all nodes due to probe outage
    return kept if kept else nodes
