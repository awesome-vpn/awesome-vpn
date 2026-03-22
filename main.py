#!/usr/bin/env python3
"""SingBox Node Crawler for awesome-vpn."""

import json
import os
import sys
import argparse
import base64
from datetime import datetime
import urllib.parse
import concurrent.futures
import logging

import yaml
from dotenv import load_dotenv
load_dotenv()

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir, 'core', 'parsers'))

from core.spider import Spider
from core.deduplicator import Deduplicator
from core.validator import Validator
from core.binary_manager import BinaryManager
from core.geo_utils import GeoUtils
from core.converters.clash import to_clash_proxies

try:
    import vmess
    import vless
    import ss
    import trojan
    import hysteria2
    import tuic
except ImportError:
    from core.parsers import vmess, vless, ss, trojan, hysteria2, tuic

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

PROTOCOL_PARSERS = {
    'vmess': vmess,
    'vless': vless,
    'ss': ss,
    'trojan': trojan,
    'hysteria2': hysteria2,
    'hy2': hysteria2,
    'tuic': tuic
}


def get_parser(protocol):
    return PROTOCOL_PARSERS.get(protocol)


def parse_source_params(param_str):
    options = {}
    if not param_str:
        return options
    try:
        params = urllib.parse.parse_qs(param_str, keep_blank_values=True)
        if 'max' in params and params['max']:
            try:
                options['max_nodes'] = int(params['max'][0])
            except:
                pass
        if 'ignore' in params and params['ignore']:
            ignore = [p.strip() for p in params['ignore'][0].split(',') if p.strip()]
            if ignore:
                options['ignore_protocols'] = ignore
    except:
        pass
    return options


def apply_source_filters(links, options):
    if not links:
        return []
    ignore = set([p.lower() for p in options.get('ignore_protocols', [])])
    if ignore:
        filtered = []
        for link in links:
            protocol = link.split('://')[0].lower() if '://' in link else ''
            if protocol and protocol in ignore:
                continue
            filtered.append(link)
        links = filtered
    max_nodes = options.get('max_nodes')
    if isinstance(max_nodes, int) and max_nodes > 0:
        links = links[:max_nodes]
    return links


def resolve_date_url(url):
    try:
        return datetime.now().strftime(url)
    except:
        return url


def expand_sources_list(list_path, spider):
    entries = []
    allow_blocked = os.getenv('ALLOW_BLOCKED_SOURCES') == '1'
    if not os.path.exists(list_path):
        return entries
    with open(list_path, 'r') as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith('#'):
                continue
            if line == 'EOF':
                break
            blocked = False
            if line.startswith('!'):
                blocked = True
                line = line[1:].strip()
            if blocked and not allow_blocked:
                continue
            is_date = False
            if line.startswith('+date'):
                is_date = True
                line = line[len('+date'):].strip()
            is_list = False
            if line.startswith('*'):
                is_list = True
                line = line[1:].strip()
            param_str = ''
            if '#' in line:
                line, param_str = line.split('#', 1)
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
                            if not item or item.startswith('#'):
                                continue
                            item_url = item.split('#')[0].strip()
                            if item_url.startswith('http'):
                                entries.append((item_url, options))
                except Exception as e:
                    logger.debug(f"Error fetching list {url}: {e}")
            else:
                entries.append((url, options))
    return entries


def main():
    parser = argparse.ArgumentParser(description='SingBox Node Crawler')
    parser.add_argument('--validate', action='store_true', help='Validate nodes')
    parser.add_argument('--output', type=str, default='output', help='Output directory')
    parser.add_argument('--workers', type=int, default=10, help='Number of workers')
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, 'config', 'sources.json')
    output_dir = args.output if os.path.isabs(args.output) else os.path.join(base_dir, args.output)

    os.makedirs(output_dir, exist_ok=True)

    logger.info("=" * 60)
    logger.info("SingBox Node Crawler - Starting...")
    logger.info("=" * 60)

    spider = Spider(max_workers=args.workers)
    deduplicator = Deduplicator()

    mmdb_path = os.path.join(base_dir, 'config', 'GeoLite2-City.mmdb')
    geo_utils = GeoUtils(mmdb_path)

    all_links = []

    logger.info("\n[1/5] Loading sources from config...")
    with open(config_path, 'r') as f:
        sources = json.load(f)

    # Load secrets from environment
    tg_secret = os.getenv('TELEGRAM_CHANNELS', '')
    telegram_channels = [c.strip() for c in tg_secret.split(',') if c.strip()]
    extra_urls = [u.strip() for u in os.getenv('EXTRA_URLS', '').splitlines() if u.strip()]

    logger.info(f"      Found {len(sources.get('urls', []))} URL sources")
    logger.info(f"      Found {len(telegram_channels)} Telegram channels (from Secrets)")
    logger.info(f"      Found {len(extra_urls)} extra URLs (from Secrets)")

    logger.info("\n[2/5] Fetching URLs...")
    url_sources = sources.get('urls', [])
    urls_to_fetch = []
    url_options = {}

    for url in extra_urls:
        urls_to_fetch.append(url)
        url_options[url] = {}

    for entry in url_sources:
        options = {}
        if isinstance(entry, dict):
            if entry.get('enabled') is False:
                continue
            url = entry.get('url')
            if not url:
                continue
            if entry.get('update_method') == 'change_date':
                url = resolve_date_url(url)
            if entry.get('max_nodes'):
                options['max_nodes'] = entry.get('max_nodes')
            if entry.get('ignore_protocols'):
                options['ignore_protocols'] = entry.get('ignore_protocols')
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
            all_links.extend(links)

    logger.info("\n[3/5] Fetching Telegram channels...")
    for channel in telegram_channels:
        links, _ = spider.fetch_telegram(channel)
        logger.info(f"      @{channel}: {len(links)} links")
        all_links.extend(links)

    logger.info("\n[4/5] Processing sources.list...")
    list_path = os.path.join(base_dir, 'config', 'sources.list')
    for url, options in expand_sources_list(list_path, spider):
        try:
            if url.startswith('http'):
                content = spider.fetch_url(url)
                links = spider.parse_subscription(content)
            else:
                links = [url]
            links = apply_source_filters(links, options)
            logger.info(f"      {url}: {len(links)} links")
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
            protocol = link.split('://')[0].lower()
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
    sing_box_outbounds = []
    link_to_node_map = {}
    duplicates = 0

    for node, link in raw_parsed_nodes:
        if deduplicator.is_duplicate(node) or deduplicator.is_redundant_server(node):
            duplicates += 1
            continue
        original_tag = node.get('tag', '')
        sing_box_outbounds.append(node)
        link_to_node_map[original_tag] = link

    logger.info(f"Successfully parsed: {len(sing_box_outbounds)} nodes")
    logger.info(f"Duplicates filtered: {duplicates}")

    valid_nodes = sing_box_outbounds

    if args.validate and len(valid_nodes) > 0:
        logger.info("\n" + "=" * 60)
        logger.info("Validating nodes...")
        logger.info("=" * 60)
        bm = BinaryManager(base_dir)
        sing_box_path = bm.get_singbox_path()
        validator = Validator(sing_box_path)
        valid_nodes = validator.validate_nodes_parallel(valid_nodes, timeout=5, max_workers=5)
        logger.info(f"Valid nodes: {len(valid_nodes)}")

        logger.info("\nUpdating node names with geo information...")
        updated_link_to_node_map = {}
        for node in valid_nodes:
            server = node.get('server', '')
            if server:
                node_name = geo_utils.format_node_name(server)
                original_tag = node.get('tag', '')
                node['tag'] = node_name
                if original_tag in link_to_node_map:
                    original_link = link_to_node_map[original_tag]
                    if '#' in original_link:
                        base_link = original_link.rsplit('#', 1)[0]
                        updated_link = f"{base_link}#{node_name}"
                    else:
                        updated_link = f"{original_link}#{node_name}"
                    updated_link_to_node_map[node_name] = updated_link
        link_to_node_map = updated_link_to_node_map

    logger.info("\n" + "=" * 60)
    logger.info("Saving output...")
    logger.info("=" * 60)

    # Output 1: sing-box.json (outbounds only)
    singbox_path = os.path.join(output_dir, 'sing-box.json')
    with open(singbox_path, 'w') as f:
        json.dump({"outbounds": valid_nodes}, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved: {singbox_path}")

    # Output 2: all (base64-encoded proxy links)
    links_output = []
    for node in valid_nodes:
        tag = node.get('tag', '')
        original_link = link_to_node_map.get(tag, '')
        if original_link:
            links_output.append(original_link)
        else:
            server = node.get('server', '')
            port = node.get('server_port') or node.get('port', '')
            ntype = node.get('type', '')
            links_output.append(f"{ntype}://{tag}@{server}:{port}")

    raw_links = '\n'.join(links_output)
    encoded = base64.b64encode(raw_links.encode()).decode()

    all_path = os.path.join(output_dir, 'all')
    with open(all_path, 'w') as f:
        f.write(encoded)
    logger.info(f"Saved: {all_path}")

    # Output 3: clash.yaml (proxies list)
    clash_proxies = to_clash_proxies(valid_nodes)
    clash_data = {"proxies": clash_proxies}

    clash_path = os.path.join(output_dir, 'clash.yaml')
    with open(clash_path, 'w') as f:
        yaml.dump(clash_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    logger.info(f"Saved: {clash_path}")

    logger.info("\n" + "=" * 60)
    logger.info("Summary:")
    logger.info(f"  Total nodes: {len(valid_nodes)}")
    logger.info(f"  Output directory: {output_dir}")
    logger.info("=" * 60)
    logger.info("Done!")

    geo_utils.close()


if __name__ == "__main__":
    main()
