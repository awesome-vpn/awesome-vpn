# SingBox-Crawler Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Merge SingBox-Crawler into awesome-vpn repo, running daily via GitHub Actions to output three subscription formats (base64, sing-box JSON, Clash YAML) with Telegram channels stored in Secrets.

**Architecture:** Flat repository structure with crawler code at root. Secret injection via environment variables (TELEGRAM_CHANNELS, EXTRA_URLS). Three output generators: base64 encoder, sing-box outbounds exporter, and sing-box→Clash converter.

**Tech Stack:** Python 3.11, python-dotenv, pyyaml, GitHub Actions, sing-box binary

---

## File Structure

### Core Crawler (moved from SingBox-Crawler)
- `core/parsers/*.py` - Protocol parsers (vmess, vless, ss, trojan, hysteria2, tuic, etc.)
- `core/spider.py` - URL fetcher and Telegram scraper
- `core/deduplicator.py` - Node deduplication logic
- `core/validator.py` - sing-box validation
- `core/binary_manager.py` - Download/manage sing-box binary
- `core/geo_utils.py` - GeoIP lookup for node naming

### New Files
- `core/converters/__init__.py` - Converter package
- `core/converters/clash.py` - sing-box outbound → Clash proxy converter

### Modified Files
- `main.py` - Entry point: dotenv load, secret injection, three output files
- `config/sources.json` - Remove telegram_channels (now in Secrets)
- `config/sources.list` - Add new public sources
- `requirements.txt` - Add python-dotenv, pyyaml
- `.gitignore` - Add output/, .env, bin/, config/GeoLite2-City.mmdb
- `.github/workflows/daily.yml` - New workflow with Secrets and GeoIP download

### Output Files (git-tracked)
- `all` - Base64-encoded proxy links
- `sing-box.json` - `{"outbounds": [...]}`
- `clash.yaml` - `proxies:` list

---

## Task 1: Prepare Directory Structure

**Files:**
- Create: `core/converters/__init__.py`
- Modify: `.gitignore`

- [ ] **Step 1: Create directories**

```bash
mkdir -p core/converters
mkdir -p tests
touch core/converters/__init__.py
touch tests/__init__.py
```

- [ ] **Step 2: Update .gitignore**

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
.env

# Output
output/
*.log

# GeoIP database (downloaded at runtime)
config/GeoLite2-City.mmdb

# sing-box binary (cached)
bin/
```

- [ ] **Step 3: Commit**

```bash
git add core/converters/__init__.py tests/__init__.py .gitignore
git commit -m "chore: setup directory structure for crawler integration"
```

---

## Task 2: Implement Clash Converter

**Files:**
- Create: `core/converters/clash.py`
- Create: `tests/test_clash_converter.py`

- [ ] **Step 1: Write failing test for VMess conversion**

```python
# tests/test_clash_converter.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.converters.clash import to_clash_proxy

def test_vmess_conversion():
    singbox_node = {
        "type": "vmess",
        "tag": "test-vmess",
        "server": "1.2.3.4",
        "server_port": 443,
        "uuid": "uuid-1234",
        "security": "auto",
        "tls": {"enabled": True}
    }
    result = to_clash_proxy(singbox_node)
    assert result["name"] == "test-vmess"
    assert result["type"] == "vmess"
    assert result["server"] == "1.2.3.4"
    assert result["port"] == 443
    assert result["uuid"] == "uuid-1234"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /Users/a12/projects/singbox-/awesome-vpn
python -m pytest tests/test_clash_converter.py::test_vmess_conversion -v
```
Expected: `ModuleNotFoundError` or function not found

- [ ] **Step 3: Implement Clash converter**

```python
# core/converters/clash.py
"""Convert sing-box outbounds to Clash proxy format."""
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


def to_clash_proxy(node: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Convert a sing-box outbound dict to Clash proxy dict."""
    ntype = node.get("type", "").lower()
    converter = CONVERTERS.get(ntype)
    if not converter:
        logger.debug(f"Unsupported node type for Clash: {ntype}")
        return None
    return converter(node)


def _convert_vmess(node: Dict[str, Any]) -> Dict[str, Any]:
    proxy = {
        "name": node.get("tag", "vmess"),
        "type": "vmess",
        "server": node.get("server", ""),
        "port": node.get("server_port", 0),
        "uuid": node.get("uuid", ""),
        "alterId": node.get("alter_id", 0),
        "cipher": node.get("security", "auto"),
    }
    tls = node.get("tls", {})
    if tls.get("enabled"):
        proxy["tls"] = True
        if tls.get("server_name"):
            proxy["servername"] = tls["server_name"]
        if tls.get("insecure"):
            proxy["skip-cert-verify"] = True

    transport = node.get("transport", {})
    if transport:
        net_type = transport.get("type", "")
        if net_type == "ws":
            proxy["network"] = "ws"
            ws_opts = {}
            if transport.get("path"):
                ws_opts["path"] = transport["path"]
            if transport.get("headers", {}).get("Host"):
                ws_opts["headers"] = {"Host": transport["headers"]["Host"]}
            if ws_opts:
                proxy["ws-opts"] = ws_opts

    return proxy


def _convert_vless(node: Dict[str, Any]) -> Dict[str, Any]:
    proxy = {
        "name": node.get("tag", "vless"),
        "type": "vless",
        "server": node.get("server", ""),
        "port": node.get("server_port", 0),
        "uuid": node.get("uuid", ""),
    }
    if node.get("flow"):
        proxy["flow"] = node["flow"]

    tls = node.get("tls", {})
    if tls.get("enabled"):
        proxy["tls"] = True
        if tls.get("server_name"):
            proxy["servername"] = tls["server_name"]
        if tls.get("insecure"):
            proxy["skip-cert-verify"] = True

        # REALITY support
        reality = tls.get("reality", {})
        if reality.get("enabled"):
            reality_opts = {}
            if reality.get("public_key"):
                reality_opts["public-key"] = reality["public_key"]
            if reality.get("short_id"):
                reality_opts["short-id"] = reality["short_id"]
            if reality_opts:
                proxy["reality-opts"] = reality_opts

            utls = tls.get("utls", {})
            proxy["client-fingerprint"] = utls.get("fingerprint", "chrome")

    transport = node.get("transport", {})
    if transport:
        net_type = transport.get("type", "")
        proxy["network"] = net_type
        if net_type == "ws":
            ws_opts = {}
            if transport.get("path"):
                ws_opts["path"] = transport["path"]
            if transport.get("headers", {}).get("Host"):
                ws_opts["headers"] = {"Host": transport["headers"]["Host"]}
            if ws_opts:
                proxy["ws-opts"] = ws_opts
        elif net_type == "grpc":
            grpc_opts = {}
            if transport.get("service_name"):
                grpc_opts["grpc-service-name"] = transport["service_name"]
            if grpc_opts:
                proxy["grpc-opts"] = grpc_opts

    return proxy


def _convert_shadowsocks(node: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "name": node.get("tag", "ss"),
        "type": "ss",
        "server": node.get("server", ""),
        "port": node.get("server_port", 0),
        "password": node.get("password", ""),
        "cipher": node.get("method", "none"),
    }


def _convert_trojan(node: Dict[str, Any]) -> Dict[str, Any]:
    proxy = {
        "name": node.get("tag", "trojan"),
        "type": "trojan",
        "server": node.get("server", ""),
        "port": node.get("server_port", 0),
        "password": node.get("password", ""),
    }
    tls = node.get("tls", {})
    if tls.get("enabled"):
        if tls.get("server_name"):
            proxy["sni"] = tls["server_name"]
        if tls.get("insecure"):
            proxy["skip-cert-verify"] = True

    transport = node.get("transport", {})
    if transport:
        net_type = transport.get("type", "")
        if net_type == "ws":
            proxy["network"] = "ws"
            ws_opts = {}
            if transport.get("path"):
                ws_opts["path"] = transport["path"]
            if transport.get("headers", {}).get("Host"):
                ws_opts["headers"] = {"Host": transport["headers"]["Host"]}
            if ws_opts:
                proxy["ws-opts"] = ws_opts

    return proxy


def _convert_hysteria2(node: Dict[str, Any]) -> Dict[str, Any]:
    proxy = {
        "name": node.get("tag", "hysteria2"),
        "type": "hysteria2",
        "server": node.get("server", ""),
        "port": node.get("server_port", 0),
        "password": node.get("password", ""),
    }
    tls = node.get("tls", {})
    if tls.get("server_name"):
        proxy["sni"] = tls["server_name"]
    if tls.get("insecure"):
        proxy["skip-cert-verify"] = True
    return proxy


def _convert_tuic(node: Dict[str, Any]) -> Dict[str, Any]:
    proxy = {
        "name": node.get("tag", "tuic"),
        "type": "tuic",
        "server": node.get("server", ""),
        "port": node.get("server_port", 0),
        "uuid": node.get("uuid", ""),
        "password": node.get("password", ""),
    }
    if node.get("congestion_control"):
        proxy["congestion-controller"] = node["congestion_control"]
    tls = node.get("tls", {})
    if tls.get("alpn"):
        proxy["alpn"] = tls["alpn"] if isinstance(tls["alpn"], list) else [tls["alpn"]]
    return proxy


CONVERTERS = {
    "vmess": _convert_vmess,
    "vless": _convert_vless,
    "shadowsocks": _convert_shadowsocks,
    "ss": _convert_shadowsocks,
    "trojan": _convert_trojan,
    "hysteria2": _convert_hysteria2,
    "hy2": _convert_hysteria2,
    "tuic": _convert_tuic,
}


def to_clash_proxies(nodes: list) -> list:
    """Convert a list of sing-box nodes to Clash proxies."""
    result = []
    for node in nodes:
        proxy = to_clash_proxy(node)
        if proxy:
            result.append(proxy)
    return result
```

- [ ] **Step 4: Run tests to verify**

```bash
python -m pytest tests/test_clash_converter.py -v
```
Expected: All tests PASS

- [ ] **Step 5: Add more tests for coverage**

```python
def test_vless_with_reality():
    node = {
        "type": "vless",
        "tag": "vless-reality",
        "server": "2.3.4.5",
        "server_port": 443,
        "uuid": "uuid-test",
        "tls": {
            "enabled": True,
            "reality": {"enabled": True, "public_key": "pk123", "short_id": "sid456"},
            "utls": {"fingerprint": "chrome"}
        }
    }
    result = to_clash_proxy(node)
    assert result["reality-opts"]["public-key"] == "pk123"
    assert result["client-fingerprint"] == "chrome"

def test_ss_conversion():
    node = {
        "type": "shadowsocks",
        "tag": "ss-node",
        "server": "3.4.5.6",
        "server_port": 8388,
        "password": "pass123",
        "method": "aes-256-gcm"
    }
    result = to_clash_proxy(node)
    assert result["type"] == "ss"
    assert result["cipher"] == "aes-256-gcm"

def test_unsupported_type():
    assert to_clash_proxy({"type": "unknown"}) is None
```

- [ ] **Step 6: Run all tests**

```bash
python -m pytest tests/test_clash_converter.py -v
```
Expected: All tests PASS

- [ ] **Step 7: Commit**

```bash
git add core/converters/ tests/test_clash_converter.py
git commit -m "feat: add Clash converter for sing-box outbounds"
```

---

## Task 3: Copy Core Crawler Files

**Files:**
- Copy: `core/` from SingBox-Crawler

- [ ] **Step 1: Copy all crawler files**

```bash
cd /Users/a12/projects/singbox-
cp -r SingBox-Crawler/core/parsers awesome-vpn/core/
cp SingBox-Crawler/core/spider.py awesome-vpn/core/
cp SingBox-Crawler/core/deduplicator.py awesome-vpn/core/
cp SingBox-Crawler/core/validator.py awesome-vpn/core/
cp SingBox-Crawler/core/binary_manager.py awesome-vpn/core/
cp SingBox-Crawler/core/geo_utils.py awesome-vpn/core/
```

- [ ] **Step 2: Copy config files**

```bash
cp SingBox-Crawler/config/sources.json awesome-vpn/config/
cp SingBox-Crawler/config/sources.list awesome-vpn/config/
cp SingBox-Crawler/requirements.txt awesome-vpn/
```

- [ ] **Step 3: Commit (import verification in Task 4)**

```bash
git add core/ config/ requirements.txt
git commit -m "chore: copy SingBox-Crawler core files"
```

---

## Task 4: Update requirements.txt

**Files:**
- Modify: `requirements.txt`

- [ ] **Step 1: Read current requirements.txt**

```bash
cat requirements.txt
```

- [ ] **Step 2: Add new dependencies**

Add these lines if not present:
```
python-dotenv>=1.0.0
pyyaml>=6.0
```

- [ ] **Step 3: Verify installation works**

```bash
pip install -r requirements.txt
```

- [ ] **Step 4: Verify core imports work**

```bash
cd /Users/a12/projects/singbox-/awesome-vpn
python -c "from core.spider import Spider; print('OK')"
python -c "from core.deduplicator import Deduplicator; print('OK')"
python -c "from core.validator import Validator; print('OK')"
python -c "from core.parsers import vmess, vless, ss, trojan; print('OK')"
```

- [ ] **Step 5: Commit**

```bash
git add requirements.txt
git commit -m "chore: add python-dotenv and pyyaml dependencies"
```

---

## Task 5: Update main.py with Secrets and Three Outputs

**Files:**
- Create: `main.py` (new version)

- [ ] **Step 1: Read existing SingBox-Crawler main.py as reference**

```bash
cat /Users/a12/projects/singbox-/SingBox-Crawler/main.py
```

- [ ] **Step 2: Write new main.py**

```python
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

    # Initialize GeoUtils with GeoLite2-City.mmdb
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

    # Add extra URLs from Secrets first
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

    # Phase 1: Parse all links concurrently (no dedup yet - Deduplicator is not thread-safe)
    raw_parsed_nodes = []
    parse_errors = 0

    def parse_link_simple(link):
        """Parse link without deduplication."""
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
        # Download sing-box binary if not present
        bm = BinaryManager(base_dir)
        sing_box_path = bm.get_singbox_path()
        validator = Validator(sing_box_path)
        valid_nodes = validator.validate_nodes_parallel(valid_nodes, timeout=5, max_workers=5)
        logger.info(f"Valid nodes: {len(valid_nodes)}")

        # Update node tags with geo information
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

    # Output 1: sing-box.json (outbounds only, no extra fields per spec)
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

    # Close GeoLite2-City.mmdb connection
    geo_utils.close()


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Test main.py imports**

```bash
cd /Users/a12/projects/singbox-/awesome-vpn
python -c "import main; print('Imports OK')"
```

- [ ] **Step 4: Commit**

```bash
git add main.py
git commit -m "feat: main.py with secrets injection and three output formats"
```

---

## Task 6: Update BinaryManager to Support Version Pinning

**Files:**
- Modify: `core/binary_manager.py`

- [ ] **Step 1: Read current BinaryManager**

```bash
cat core/binary_manager.py
```

- [ ] **Step 2: Update to accept version from env**

Add at the top of the class or in `_get_latest_version()`:
```python
import os

def _get_latest_version(self):
    # Check for pinned version in environment
    pinned = os.getenv('SING_BOX_VERSION')
    if pinned:
        return pinned.lstrip('v')  # Remove 'v' prefix if present
    # ... existing code to fetch from GitHub API ...
```

- [ ] **Step 3: Commit**

```bash
git add core/binary_manager.py
git commit -m "feat: support SING_BOX_VERSION env var for version pinning"
```

---

## Task 7: Update sources.json (Remove Telegram Channels)

**Files:**
- Modify: `config/sources.json`

- [ ] **Step 1: Read current sources.json**

```bash
cat config/sources.json
```

- [ ] **Step 2: Remove telegram_channels field**

The file should only contain:
```json
{
  "urls": [
    "https://raw.githubusercontent.com/...",
    ...
  ]
}
```

Remove the `telegram_channels` array entirely.

- [ ] **Step 3: Commit**

```bash
git add config/sources.json
git commit -m "chore: remove telegram_channels from sources.json (moved to Secrets)"
```

---

## Task 8: Add New Public Sources to sources.list

**Files:**
- Modify: `config/sources.list`

- [ ] **Step 1: Read current sources.list**

```bash
cat config/sources.list
```

- [ ] **Step 2: Append new sources**

Add to the end (before EOF if present):
```
# Additional high-quality public sources
https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge_base64.txt
https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/splitted/mixed
https://raw.githubusercontent.com/Everyday-VPN/Everyday-VPN/main/subscription/main.txt
https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/All_Configs_Sub.txt
https://raw.githubusercontent.com/NiREvil/vless/main/sub/subs.txt
https://raw.githubusercontent.com/coldwater-10/V2Hub/main/sub
https://raw.githubusercontent.com/mheidari98/.proxy/main/all
https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/sub/mix
https://raw.githubusercontent.com/Ashkan-m/v2ray/main/Sub.txt
```

- [ ] **Step 3: Commit**

```bash
git add config/sources.list
git commit -m "chore: add new public sources to sources.list"
```

---

## Task 9: Create GitHub Actions Workflow

**Files:**
- Create: `.github/workflows/daily.yml`

- [ ] **Step 1: Create workflow directory**

```bash
mkdir -p .github/workflows
```

- [ ] **Step 2: Write workflow file**

```yaml
name: Daily Crawler

on:
  schedule:
    - cron: '0 0 * * *'
  workflow_dispatch:

env:
  SING_BOX_VERSION: "1.10.7"

jobs:
  crawl:
    runs-on: ubuntu-latest
    permissions:
      contents: write

    steps:
    - name: Checkout
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'

    - name: Cache sing-box binary
      uses: actions/cache@v4
      with:
        path: bin/
        key: sing-box-${{ runner.os }}-${{ runner.arch }}-${{ env.SING_BOX_VERSION }}

    - name: Download GeoLite2-City.mmdb
      run: |
        mkdir -p config
        curl -sL "https://github.com/P3TERX/GeoLite.mmdb/raw/download/GeoLite2-City.mmdb" \
          -o config/GeoLite2-City.mmdb

    - name: Install Dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Run Crawler
      env:
        TELEGRAM_CHANNELS: ${{ secrets.TELEGRAM_CHANNELS }}
        EXTRA_URLS: ${{ secrets.EXTRA_URLS }}
        SING_BOX_VERSION: ${{ env.SING_BOX_VERSION }}
      run: |
        python main.py --validate --workers 10 --output .

    - name: Verify Outputs
      run: |
        [ -s all ] || (echo "ERROR: all is empty" && exit 1)
        [ -s sing-box.json ] || (echo "ERROR: sing-box.json is empty" && exit 1)
        [ -s clash.yaml ] || (echo "ERROR: clash.yaml is empty" && exit 1)
        echo "Output sizes:"
        ls -lh all sing-box.json clash.yaml
        echo "Node count: $(python -c 'import json; print(len(json.load(open("sing-box.json"))["outbounds"]))')"

    - name: Commit and Push
      run: |
        git config user.name "github-actions[bot]"
        git config user.email "github-actions[bot]@users.noreply.github.com"
        git add all sing-box.json clash.yaml
        NODE_COUNT=$(python -c 'import json; print(len(json.load(open("sing-box.json"))["outbounds"]))')
        git diff --staged --quiet || \
          git commit -m "update: $(date +'%Y-%m-%d') - ${NODE_COUNT} nodes"
        git push
```

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/daily.yml
git commit -m "ci: add GitHub Actions workflow for daily crawling"
```

---

## Task 10: Final Verification

**Files:**
- All modified files

- [ ] **Step 1: Verify all files are present**

```bash
cd /Users/a12/projects/singbox-/awesome-vpn
ls -la
ls -la core/
ls -la core/parsers/
ls -la core/converters/
ls -la config/
ls -la .github/workflows/
```

- [ ] **Step 2: Test local run (without validation to save time)**

```bash
cd /Users/a12/projects/singbox-/awesome-vpn
python main.py --output test_output --workers 5
```

- [ ] **Step 3: Verify output files were created**

```bash
ls -la test_output/
head -c 200 test_output/all
echo ""
head test_output/sing-box.json
head test_output/clash.yaml
```

- [ ] **Step 4: Decode base64 'all' file to verify**

```bash
base64 -d test_output/all | head -5
```

- [ ] **Step 5: Clean up test output**

```bash
rm -rf test_output
```

- [ ] **Step 6: Final commit**

```bash
git status
git add -A
git commit -m "chore: finalize crawler integration"
```

---

## Known Limitations / Trade-offs

1. **Telegram channel options dropped:** The new secrets-based approach uses plain comma-separated channel names. Per-channel `max_nodes` and `enabled` flags are no longer supported. The original code applied `apply_source_filters` to Telegram results; this is now skipped. If a channel produces excessive nodes, they will all be processed.

2. **BinaryManager version pinning (local only):** The `SING_BOX_VERSION` env var pins the version when downloading a new binary, but if an old binary already exists in `bin/sing-box-{system}-{machine}`, it will be used without checking the version. This only affects local development; GitHub Actions uses cache key with version, so stale binaries are avoided.

3. **Deduplication is single-threaded:** To avoid thread-safety issues with `Deduplicator`, parsing happens in parallel but deduplication happens in a single-threaded pass afterward. This is slightly slower but ensures correctness.

---

## Post-Merge Setup (Manual)

These steps must be done manually in the GitHub UI after merging:

1. **Set Actions Permissions:**
   - Go to repo → Settings → Actions → General
   - Set "Workflow permissions" to "Read and write permissions"

2. **Set Repository Secrets:**
   - Go to repo → Settings → Secrets and variables → Actions
   - Add `TELEGRAM_CHANNELS`: comma-separated list like `chan1,chan2,chan3`
   - Add `EXTRA_URLS`: multiline list of private URLs

3. **Trigger Test Run:**
   - Go to Actions tab → Daily Crawler → Run workflow

---

## Summary

| Task | Component | Key Changes |
|------|-----------|-------------|
| 1 | Directory Structure | Create converters package, update .gitignore |
| 2 | Clash Converter | New file: core/converters/clash.py with tests |
| 3 | Copy Crawler | Copy all SingBox-Crawler core files |
| 4 | Dependencies | Add python-dotenv, pyyaml to requirements.txt |
| 5 | main.py | New version with secrets, dotenv, three outputs |
| 6 | BinaryManager | Support SING_BOX_VERSION env var |
| 7 | sources.json | Remove telegram_channels |
| 8 | sources.list | Add 9 new public sources |
| 9 | GitHub Actions | New workflow with Secrets and GeoIP download |
| 10 | Verification | Test local run, verify all outputs |
