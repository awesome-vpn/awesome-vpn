#!/usr/bin/env python3
"""SingBox Node Crawler for awesome-vpn."""

import argparse
import base64
import concurrent.futures
import json
import logging
import os
import sys
import urllib.parse
from datetime import datetime

import yaml
from dotenv import load_dotenv

# Load secrets: .secrets takes priority, .env as fallback
load_dotenv(".secrets")
load_dotenv()

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir, "core", "parsers"))

from core.binary_manager import BinaryManager
from core.converters.clash import to_clash_proxies
from core.deduplicator import Deduplicator, ensure_unique_tags
from core.geo_utils import GeoUtils
from core.spider import Spider
from core.validator import Validator

try:
    import hysteria2
    import ss
    import trojan
    import tuic
    import vless
    import vmess
except ImportError:
    from core.parsers import hysteria2, ss, trojan, tuic, vless, vmess

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

PROTOCOL_PARSERS = {
    "vmess": vmess,
    "vless": vless,
    "ss": ss,
    "trojan": trojan,
    "hysteria2": hysteria2,
    "hy2": hysteria2,
    "tuic": tuic,
}


def get_parser(protocol):
    return PROTOCOL_PARSERS.get(protocol)


def parse_source_params(param_str):
    options = {}
    if not param_str:
        return options
    try:
        params = urllib.parse.parse_qs(param_str, keep_blank_values=True)
        if "max" in params and params["max"]:
            try:
                options["max_nodes"] = int(params["max"][0])
            except (ValueError, TypeError):
                pass
        if "ignore" in params and params["ignore"]:
            ignore = [p.strip() for p in params["ignore"][0].split(",") if p.strip()]
            if ignore:
                options["ignore_protocols"] = ignore
    except Exception:
        pass
    return options


def apply_source_filters(links, options):
    if not links:
        return []
    ignore = set([p.lower() for p in options.get("ignore_protocols", [])])
    if ignore:
        filtered = []
        for link in links:
            protocol = link.split("://")[0].lower() if "://" in link else ""
            if protocol and protocol in ignore:
                continue
            filtered.append(link)
        links = filtered
    max_nodes = options.get("max_nodes")
    if isinstance(max_nodes, int) and max_nodes > 0:
        links = links[:max_nodes]
    return links


def resolve_date_url(url):
    try:
        return datetime.now().strftime(url)
    except Exception:
        return url


def format_source_label(source_url: str) -> str:
    """生成短来源标签，避免 clash 名称过长导致测速 error（特殊字符/超长）。"""
    if not source_url:
        return "Unknown"
    s = source_url.strip()
    # Telegram -> TG:channel 短标签
    if "t.me" in s:
        try:
            channel = s.split("t.me/")[-1].split("/")[0].lstrip("@").split("?")[0]
            if channel and channel != "s":
                return f"TG:{channel[:18]}"
        except Exception:
            pass
        return "TG"
    if s.startswith("@"):
        return f"TG:{s.lstrip('@')[:18]}"
    # GitHub -> GH
    if "github" in s.lower() or "raw.githubusercontent" in s.lower():
        # 保留仓库名区分不同源，避免全叫 GitHub 无法区分
        try:
            from urllib.parse import urlparse

            path = urlparse(s).path.strip("/")
            parts = path.split("/")
            if len(parts) >= 2:
                repo = f"{parts[0]}/{parts[1]}"[:24]
                return f"GH:{repo}"
        except Exception:
            pass
        return "GH"
    # 其他 -> 域名短标签
    try:
        from urllib.parse import urlparse

        host = urlparse(s).hostname or ""
        if host.startswith("www."):
            host = host[4:]
        return host[:24] if host else s[:16]
    except Exception:
        return s[:16]


def expand_sources_list(list_path, spider):
    entries = []
    allow_blocked = os.getenv("ALLOW_BLOCKED_SOURCES") == "1"
    if not os.path.exists(list_path):
        return entries
    with open(list_path) as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if line == "EOF":
                break
            blocked = False
            if line.startswith("!"):
                blocked = True
                line = line[1:].strip()
            if blocked and not allow_blocked:
                continue
            is_date = False
            if line.startswith("+date"):
                is_date = True
                line = line[len("+date") :].strip()
            is_list = False
            if line.startswith("*"):
                is_list = True
                line = line[1:].strip()
            param_str = ""
            if "#" in line:
                line, param_str = line.split("#", 1)
            url = line.strip()
            if not url:
                continue
            if is_date:
                url = resolve_date_url(url)
            options = parse_source_params(param_str)
            if is_list:
                try:
                    content = spider.fetch_url(url)
                    if content:
                        for item in content.splitlines():
                            item = item.strip()
                            if not item or item.startswith("#"):
                                continue
                            item_url = item.split("#")[0].strip()
                            if item_url.startswith("http"):
                                entries.append((item_url, options))
                except Exception as e:
                    logger.debug(f"Error fetching list {url}: {e}")
            else:
                entries.append((url, options))
    return entries


def save_singbox(output_dir, nodes):
    """Write sing-box.json with standardized English groups."""
    outbounds = list(nodes)
    tags = [n.get("tag") for n in outbounds if n.get("tag")]

    if tags:
        outbounds.append(
            {
                "type": "urltest",
                "tag": "Auto",
                "outbounds": tags,
                "url": "https://www.google.com/generate_204",
                "interval": "5m",
                "tolerance": 50,
                "interrupt_exist_connections": False,
            }
        )
        outbounds.append(
            {
                "type": "selector",
                "tag": "PROXY",
                "outbounds": ["Auto", "direct"],
                "default": "Auto",
                "interrupt_exist_connections": False,
            }
        )
        if not any(o.get("tag") == "direct" for o in outbounds):
            outbounds.append({"type": "direct", "tag": "direct"})

    path = os.path.join(output_dir, "sing-box.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"outbounds": outbounds}, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved: {path} ({len(outbounds)} outbounds inc. auto/proxy)")
    return path


def save_all(output_dir, nodes, source_links):
    """Write base64-encoded `all` file, preserving original link with updated tag."""
    links_output = []
    for node in nodes:
        tag = node.get("tag", "")
        original_link = source_links.get(id(node), "")
        if original_link:
            base_link = original_link.rsplit("#", 1)[0] if "#" in original_link else original_link
            links_output.append(f"{base_link}#{tag}")
        else:
            server = node.get("server", "")
            port = node.get("server_port") or node.get("port", "")
            ntype = node.get("type", "")
            links_output.append(f"{ntype}://{tag}@{server}:{port}")
    encoded = base64.b64encode("\n".join(links_output).encode()).decode()
    path = os.path.join(output_dir, "all")
    with open(path, "w", encoding="utf-8") as f:
        f.write(encoded)
    logger.info(f"Saved: {path}")
    return path


def save_clash(output_dir, nodes):
    """Write clash.yaml with ideal dler.io-like format: emoji+udp, auto+manual."""
    proxies = to_clash_proxies(nodes)
    proxy_names = [p.get("name") for p in proxies if p.get("name")]

    # 理想格式：带完整 Clash 基础配置 + 双组（手动 PROXY + 自动 Auto） + 基础规则
    proxy_groups = []
    if proxy_names:
        proxy_groups = [
            {
                "name": "PROXY",
                "type": "select",
                "proxies": ["Auto", "DIRECT"] + proxy_names,
            },
            {
                "name": "Auto",
                "type": "url-test",
                "proxies": proxy_names,
                "url": "https://www.google.com/generate_204",
                "interval": 300,
                "tolerance": 50,
            },
        ]

    data = {
        "port": 7890,
        "socks-port": 7891,
        "allow-lan": True,
        "mode": "Rule",
        "log-level": "info",
        "external-controller": "127.0.0.1:9090",
        "proxies": proxies,
    }
    if proxy_groups:
        data["proxy-groups"] = proxy_groups
        data["rules"] = [
            "DOMAIN-SUFFIX,local,DIRECT",
            "IP-CIDR,192.168.0.0/16,DIRECT,no-resolve",
            "IP-CIDR,10.0.0.0/8,DIRECT,no-resolve",
            "IP-CIDR,172.16.0.0/12,DIRECT,no-resolve",
            "IP-CIDR,127.0.0.0/8,DIRECT,no-resolve",
            "GEOIP,LAN,DIRECT,no-resolve",
            "MATCH,PROXY",
        ]

    path = os.path.join(output_dir, "clash.yaml")
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    logger.info(
        f"Saved: {path} ({len(proxies)} proxies, auto group {'yes' if proxy_groups else 'no'})"
    )
    return path


def main():
    parser = argparse.ArgumentParser(description="SingBox Node Crawler")
    parser.add_argument("--validate", action="store_true", help="Validate nodes")
    parser.add_argument("--output", type=str, default="output", help="Output directory")
    parser.add_argument("--workers", type=int, default=10, help="Number of fetch workers")
    parser.add_argument(
        "--validate-workers",
        type=int,
        default=30,
        help="Number of validation workers (default 30, lowered to avoid CI FD exhaustion)",
    )
    parser.add_argument(
        "--local",
        action="store_true",
        help="Local mode: skip direct TCP checks that fail behind GFW",
    )
    args = parser.parse_args()

    # Auto-detect environment: GITHUB_ACTIONS=true is set automatically in GitHub Actions.
    # In local mode, direct TCP connections to overseas servers are blocked by GFW,
    # so we skip quick_tcp_prescreen and tcp_ping (sing-box validation still runs).
    is_ci = os.getenv("GITHUB_ACTIONS") == "true"
    local_mode = args.local or not is_ci
    if local_mode:
        logger.info("Mode: LOCAL (direct TCP checks disabled — GFW environment)")
    else:
        logger.info("Mode: CI (full validation including direct TCP checks)")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = args.output if os.path.isabs(args.output) else os.path.join(base_dir, args.output)

    os.makedirs(output_dir, exist_ok=True)

    logger.info("=" * 60)
    logger.info("SingBox Node Crawler - Starting...")
    logger.info("=" * 60)

    spider = Spider(max_workers=args.workers)
    deduplicator = Deduplicator()

    mmdb_path = os.path.join(base_dir, "config", "GeoLite2-City.mmdb")
    geo_utils = GeoUtils(mmdb_path)

    all_links: list[str] = []
    link_to_source: dict[str, str] = {}  # proxy link -> subscription URL / TG channel

    logger.info("\n[1/5] Loading sources from config...")

    # Load sources from env var or default config file
    sources_json_env = os.getenv("SOURCES_JSON", "")
    temp_config_file = None
    if sources_json_env:
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write(sources_json_env)
            config_path = f.name
            temp_config_file = config_path
        logger.info("      Using SOURCES_JSON from environment")
    else:
        config_path = os.path.join(base_dir, "config", "sources.json")
        logger.info("      Using default config/sources.json")
    try:
        with open(config_path) as f:
            sources = json.load(f)
    except FileNotFoundError:
        logger.warning(
            f"Config not found at {config_path}, using empty sources (set SOURCES_JSON or create config/sources.json)"
        )
        sources = {"urls": []}
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {config_path}: {e}, using empty sources")
        sources = {"urls": []}

    # Clean up temp file if created from SOURCES_JSON
    if temp_config_file and os.path.exists(temp_config_file):
        try:
            os.remove(temp_config_file)
        except OSError:
            pass

    # Load secrets from environment
    tg_secret = os.getenv("TELEGRAM_CHANNELS", "")
    telegram_channels = [c.strip() for c in tg_secret.split(",") if c.strip()]
    extra_urls = [u.strip() for u in os.getenv("EXTRA_URLS", "").splitlines() if u.strip()]

    logger.info(f"      Found {len(sources.get('urls', []))} URL sources")
    logger.info(f"      Found {len(telegram_channels)} Telegram channels (from Secrets)")
    logger.info(f"      Found {len(extra_urls)} extra URLs (from Secrets)")

    logger.info("\n[2/5] Fetching URLs...")
    url_sources = sources.get("urls", [])
    urls_to_fetch = []
    url_options = {}

    for url in extra_urls:
        urls_to_fetch.append(url)
        url_options[url] = {}

    for entry in url_sources:
        options = {}
        if isinstance(entry, dict):
            if entry.get("enabled") is False:
                continue
            url = entry.get("url")
            if not url:
                continue
            if entry.get("update_method") == "change_date":
                url = resolve_date_url(url)
            if entry.get("max_nodes"):
                options["max_nodes"] = entry.get("max_nodes")
            if entry.get("ignore_protocols"):
                options["ignore_protocols"] = entry.get("ignore_protocols")
        else:
            url = entry
        urls_to_fetch.append(url)
        url_options[url] = options

    results = spider.fetch_urls_parallel(urls_to_fetch)

    for url, content in results.items():
        if content:
            links = spider.parse_subscription(content)
            links = apply_source_filters(links, url_options.get(url, {}))
            logger.info(f"      {url}: {len(links)} links")
            for link in links:
                if link not in link_to_source:
                    link_to_source[link] = url
            all_links.extend(links)

    logger.info("\n[3/5] Fetching Telegram channels...")

    def _fetch_channel(channel):
        links, _ = spider.fetch_telegram(channel)
        return channel, links

    # Telegram: 24 concurrent workers (half of 48 channels)
    tg_workers = min(24, len(telegram_channels)) if telegram_channels else 1
    with concurrent.futures.ThreadPoolExecutor(max_workers=tg_workers) as executor:
        for channel, links in executor.map(_fetch_channel, telegram_channels):
            logger.info(f"      @{channel}: {len(links)} links")
            src = f"https://t.me/s/{channel}"
            for link in links:
                if link not in link_to_source:
                    link_to_source[link] = src
            all_links.extend(links)

    logger.info("\n[4/5] Processing sources.list...")
    list_path = os.path.join(base_dir, "config", "sources.list")
    for url, options in expand_sources_list(list_path, spider):
        try:
            if url.startswith("http"):
                content = spider.fetch_url(url)
                links = spider.parse_subscription(content)
            else:
                links = [url]
            links = apply_source_filters(links, options)
            logger.info(f"      {url}: {len(links)} links")
            for link in links:
                if link not in link_to_source:
                    link_to_source[link] = url
            all_links.extend(links)
        except Exception as e:
            logger.debug(f"      Failed to process {url}: {e}")

    unique_links = list(set(all_links))
    logger.info(f"\n[5/5] Total unique links: {len(unique_links)}")

    logger.info("\n" + "=" * 60)
    logger.info("Parsing links to Sing-box format...")
    logger.info("=" * 60)

    # Phase 1: Parse all links concurrently (no dedup - Deduplicator is not thread-safe)
    raw_parsed_nodes = []
    parse_errors = 0

    def parse_link_simple(link):
        try:
            protocol = link.split("://")[0].lower()
            parser = get_parser(protocol)
            if parser:
                return parser.parse(link), link
        except Exception:
            pass
        return None, link

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        future_to_link = {executor.submit(parse_link_simple, link): link for link in unique_links}
        for future in concurrent.futures.as_completed(future_to_link):
            try:
                node, link = future.result()
                if node:
                    raw_parsed_nodes.append((node, link))
            except Exception:
                parse_errors += 1

    logger.info(f"Raw parsed: {len(raw_parsed_nodes)} nodes")
    logger.info(f"Parse errors: {parse_errors}")

    # Phase 2: Single-threaded deduplication
    logger.info("Deduplicating nodes...")
    sing_box_outbounds: list[dict] = []
    source_links: dict[int, str] = {}
    node_source_map: dict[int, str] = {}  # 节点 -> 订阅源 URL（用于中文来源标注）
    duplicates = 0

    for node, link in raw_parsed_nodes:
        # ss.py returns (node, node_tls) tuple for shadow-tls links
        nodes_to_add = list(node) if isinstance(node, tuple) else [node]
        for n in nodes_to_add:
            if deduplicator.is_duplicate(n) or deduplicator.is_redundant_server(n):
                duplicates += 1
                continue
            sing_box_outbounds.append(n)
            source_links[id(n)] = link
            node_source_map[id(n)] = link_to_source.get(link, "未知来源")

    logger.info(f"Successfully parsed: {len(sing_box_outbounds)} nodes")
    logger.info(f"Duplicates filtered: {duplicates}")

    valid_nodes = sing_box_outbounds

    if args.validate and len(valid_nodes) > 0:
        logger.info("\n" + "=" * 60)
        logger.info("Pre-screening nodes with quick TCP check...")
        logger.info("=" * 60)

        if local_mode:
            logger.info("Skipping TCP pre-screen in local mode (direct TCP blocked behind GFW)")
        else:
            # P1: Fast TCP pre-screening to reduce validation time
            from core.validator import quick_tcp_prescreen

            prescreened = quick_tcp_prescreen(valid_nodes, max_workers=60, timeout=2)
            filtered_out = len(valid_nodes) - len(prescreened)
            logger.info(
                f"TCP pre-screen: {len(prescreened)}/{len(valid_nodes)} passed ({filtered_out} filtered)"
            )
            valid_nodes = prescreened

    if args.validate and len(valid_nodes) > 0:
        logger.info("\n" + "=" * 60)
        logger.info("Validating nodes with sing-box...")
        logger.info("=" * 60)
        bm = BinaryManager(base_dir)
        sing_box_path = bm.get_singbox_path()
        validator = Validator(sing_box_path, local_mode=local_mode)
        valid_nodes = validator.validate_nodes_parallel(
            valid_nodes, timeout=5, max_workers=args.validate_workers
        )
        logger.info(f"Valid nodes (before ranking): {len(valid_nodes)}")

        # --- 严格质量管控（大陆友好） ---
        # GitHub 能连 ≠ 大陆能连：GFW 对直连 `server:port` 的 TCP 阻断是主因。
        # 此处用本地可算的抗封锁分 + 实测延迟做 Top-N 优选，宁缺毋滥。
        try:
            max_nodes = int(os.getenv("MAX_NODES", "80"))
        except (ValueError, TypeError):
            max_nodes = 80
        # CHINA_CHECK_URL 可选：若提供大陆侧探活接口（如自建杭州/深圳探针），
        # 可在此对 valid_nodes 再做一轮 `server:port` 可达性校验（当前仅启发式）
        china_check_url = os.getenv("CHINA_CHECK_URL", "").strip()
        if china_check_url:
            logger.info(f"China check enabled: {china_check_url} (external probe)")

        # 统一评分 + 排序（无论是否截断，都让优质节点在前）
        if valid_nodes:
            from core.quality import filter_by_china_probe, filter_timeout_outliers, quality_score

            for n in valid_nodes:
                n["_quality"] = quality_score(n, n.get("_latency_ms"))

            valid_nodes.sort(key=lambda x: x.get("_quality", 0), reverse=True)

            # 科学剔除 timeout：500ms 硬阈值（大陆体感），无墙环境下验证有墙可用性
            before_timeout = len(valid_nodes)
            valid_nodes = filter_timeout_outliers(valid_nodes, "_latency_ms", max_latency_ms=500)
            if len(valid_nodes) < before_timeout:
                logger.info(
                    f"Timeout filter: {len(valid_nodes)}/{before_timeout} kept (500ms hard)"
                )

            # 可选：大陆侧探活二次过滤（需外网探针）
            if china_check_url:
                before = len(valid_nodes)
                valid_nodes = filter_by_china_probe(valid_nodes, china_check_url)
                logger.info(f"China probe: {len(valid_nodes)}/{before} reachable from mainland")

            # 严格截断：宁缺毋滥
            if max_nodes > 0 and len(valid_nodes) > max_nodes:
                dropped = len(valid_nodes) - max_nodes
                logger.info(
                    f"Quality ranking: keep Top {max_nodes}/{len(valid_nodes)} (drop {dropped} low-quality)"
                )
                for n in valid_nodes[max_nodes : max_nodes + 3]:
                    logger.debug(
                        f"  dropped example: {n.get('type')} {n.get('server')}:{n.get('server_port')} q={n.get('_quality'):.1f}"
                    )
                valid_nodes = valid_nodes[:max_nodes]
            else:
                logger.info(
                    f"Quality ranking: {len(valid_nodes)} <= {max_nodes}, keep all (sorted)"
                )

            for n in valid_nodes:
                n.pop("_quality", None)
                n.pop("_latency_ms", None)

        logger.info(f"Valid nodes (after ranking): {len(valid_nodes)}")

        logger.info("\nUpdating node names with geo information (parallel)...")
        # Pre-collect data before parallelizing; geo_utils is thread-safe (cached)
        # 短来源标签： Japan/Tokyo [TG:xxx] / Germany [GH:repo]，避免全 URL 过长导致 clash error
        node_data = [
            (node, node.get("tag", ""), node_source_map.get(id(node), "未知来源"))
            for node in valid_nodes
        ]

        def resolve_geo(item):
            node, original_tag, source_url = item
            server = node.get("server", "")
            geo_name = geo_utils.format_node_name(server) if server else original_tag
            source_label = format_source_label(source_url)
            node_name = f"{geo_name} [{source_label}]"
            return node, node_name

        geo_workers = min(30, len(valid_nodes)) if valid_nodes else 1
        with concurrent.futures.ThreadPoolExecutor(max_workers=geo_workers) as executor:
            geo_results = list(executor.map(resolve_geo, node_data))

        for node, node_name in geo_results:
            node["tag"] = node_name

    renamed_tags = ensure_unique_tags(valid_nodes)
    logger.info(f"Renamed duplicate tags: {renamed_tags}")

    logger.info("\n" + "=" * 60)
    logger.info("Saving output...")
    logger.info("=" * 60)

    save_singbox(output_dir, valid_nodes)
    save_all(output_dir, valid_nodes, source_links)
    save_clash(output_dir, valid_nodes)

    logger.info("\n" + "=" * 60)
    logger.info("Summary:")
    logger.info(f"  Total nodes: {len(valid_nodes)}")
    logger.info(f"  Output directory: {output_dir}")
    logger.info("=" * 60)
    logger.info("Done!")

    geo_utils.close()


if __name__ == "__main__":
    main()
