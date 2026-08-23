import base64
import concurrent.futures
import json
import logging
import re
from urllib.parse import quote

import requests
import yaml
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

FAKE_IPS = ["8.8.8.8", "8.8.4.4", "4.2.2.2", "4.2.2.1", "114.114.114.114", "127.0.0.1", "0.0.0.0"]
FAKE_DOMAINS = [".google.com", ".github.com"]


class Spider:
    def __init__(self, max_workers=10, timeout=15):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Clash-verge/v2.0.3 AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }
        self.proxies = None
        self.max_workers = max_workers
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.session.trust_env = False
        # reuse connection pooling
        adapter = requests.adapters.HTTPAdapter(pool_connections=20, pool_maxsize=50, max_retries=1)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def fetch_url(self, url, timeout=None):
        if timeout is None:
            timeout = self.timeout
        try:
            resp = self.session.get(url, timeout=timeout, stream=True)
            if resp.status_code != 200:
                logger.debug(f"fetch_url {url} -> HTTP {resp.status_code}")
                return None
            return self._download_content(resp)
        except requests.RequestException as e:
            logger.debug(f"fetch_url {url} failed: {e}")
            return None

    def _download_content(self, response):
        content = ""
        tp = None
        pending = None
        for chunk in response.iter_content(chunk_size=8192):
            if not chunk:
                continue
            if pending is not None:
                chunk = pending + chunk
                pending = None
            if tp == "sub":
                content += chunk.decode(errors="ignore")
                continue
            lines = chunk.splitlines()
            if lines and lines[-1] and chunk and lines[-1][-1] == chunk[-1]:
                pending = lines.pop()
            while lines:
                line = lines.pop(0).rstrip().decode(errors="ignore").replace("\r", "")
                if not line:
                    continue
                if not tp:
                    if ": " in line:
                        kv = line.split(": ")
                        if len(kv) == 2 and kv[0].isalpha():
                            tp = "yaml"
                    elif line[0] == "#":
                        pass
                    else:
                        tp = "sub"
                if tp == "yaml":
                    if content:
                        if line in ("proxy-groups:", "rules:", "script:"):
                            return content
                        content += line + "\n"
                    elif line == "proxies:":
                        content = line + "\n"
                elif tp == "sub":
                    content = chunk.decode(errors="ignore")
                    return content
        if pending is not None:
            content += pending.decode(errors="ignore")
        return content

    def fetch_urls_parallel(self, urls, max_workers=None):
        if max_workers is None:
            max_workers = self.max_workers
        results = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {executor.submit(self.fetch_url, url): url for url in urls}
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    results[url] = future.result()
                except Exception as e:
                    logger.debug(f"fetch_urls_parallel {url} failed: {e}")
                    results[url] = None
        return results

    def extract_links(self, text):
        """
        Extract proxy links from arbitrary text (HTML, Markdown, etc.)
        """
        links = []
        protocols = ["vmess", "vless", "ss", "trojan", "hysteria2", "tuic", "hy2"]
        proto_pattern = r"(?:" + "|".join(protocols) + r")://"

        matches = list(re.finditer(proto_pattern, text))
        for i, match in enumerate(matches):
            start = match.start()
            if i < len(matches) - 1:
                end = matches[i + 1].start()
            else:
                end = len(text)

            candidate = text[start:end].strip()
            if "\n" in candidate:
                candidate = candidate.split("\n")[0]
            if " " in candidate:
                candidate = candidate.split(" ")[0]
            if '"' in candidate:
                candidate = candidate.split('"')[0]
            if "'" in candidate:
                candidate = candidate.split("'")[0]
            if "<" in candidate:
                candidate = candidate.split("<")[0]
            if "`" in candidate:
                candidate = candidate.split("`")[0]

            if len(candidate) > 10:
                links.append(candidate)
        return list(set(links))

    def extract_subscription_links(self, text):
        """
        Extract HTTP/HTTPS links that might be subscription sources
        """
        urls = re.findall(r'https?://[^\s<>"`\])]+', text)
        subs = []
        for url in urls:
            if any(
                x in url.lower()
                for x in ["sub", "clash", "node", "yaml", "yml", "txt", "b64", "list"]
            ):
                if not any(
                    x in url.lower() for x in ["github.com", "google.com", "t.me", "twitter.com"]
                ):
                    subs.append(url)
        return list(set(subs))

    def fetch_telegram(self, channel):
        if channel.startswith("@"):
            channel = channel[1:]

        url = f"https://t.me/s/{channel}"
        logger.info(f"Fetching Telegram Channel: {channel}")
        try:
            # reuse session for connection pooling and consistent UA
            resp = self.session.get(url, timeout=15)
            if resp.status_code != 200:
                logger.warning(f"Failed to fetch {channel}: HTTP {resp.status_code}")
                return [], []

            soup = BeautifulSoup(resp.text, "html.parser")
            messages = soup.select(".tgme_widget_message_text")

            links = []
            discovered_channels = []

            for msg in messages:
                text = msg.get_text(separator="\n")
                links.extend(self.extract_links(text))
                codes = msg.select("code")
                for code in codes:
                    links.extend(self.extract_links(code.get_text()))
                channel_pattern = r"(?:@|t\.me/)([a-zA-Z0-9_]{5,32})"
                found_channels = re.findall(channel_pattern, text)
                discovered_channels.extend(found_channels)

            return list(set(links)), list(set(discovered_channels))
        except requests.RequestException as e:
            logger.debug(f"Error fetching telegram {channel}: {e}")
            return [], []
        except Exception as e:
            logger.debug(f"Unexpected error fetching telegram {channel}: {e}")
            return [], []

    def parse_subscription(self, content):
        """
        Parse content that might be base64 encoded or plain text list
        """
        if not content:
            return []
        links = []
        try:
            clean_content = content.strip().replace("\n", "").replace(" ", "")
            if len(clean_content) % 4 != 0:
                pad = 4 - (len(clean_content) % 4)
                clean_content += "=" * pad
            decoded = base64.b64decode(clean_content, validate=True).decode(
                "utf-8", errors="ignore"
            )
            if "://" in decoded:
                links.extend(self.extract_links(decoded))
                return links
        except Exception:
            pass
        links.extend(self.extract_links(content))
        try:
            data = yaml.safe_load(content)
            if isinstance(data, dict) and "proxies" in data:
                links.extend(self._parse_clash_proxies(data["proxies"]))
        except Exception:
            pass
        return list(set(links))

    def _parse_clash_proxies(self, proxies):
        links = []
        for proxy in proxies:
            try:
                link = self._clash_proxy_to_link(proxy)
                if link:
                    links.append(link)
            except Exception as e:
                logger.debug(f"_parse_clash_proxies failed for {proxy}: {e}")
        return links

    def _clash_proxy_to_link(self, proxy):
        if not isinstance(proxy, dict):
            return None
        ptype = proxy.get("type", "")
        if ptype == "vmess":
            return self._vmess_to_link(proxy)
        elif ptype == "vless":
            return self._vless_to_link(proxy)
        elif ptype == "ss":
            return self._ss_to_link(proxy)
        elif ptype == "trojan":
            return self._trojan_to_link(proxy)
        elif ptype in ["hysteria2", "hy2"]:
            return self._hysteria2_to_link(proxy)
        return None

    def _vmess_to_link(self, p):
        v = {
            "v": "2",
            "ps": p.get("name", ""),
            "add": p.get("server", ""),
            "port": str(p.get("port", "")),
            "id": p.get("uuid", ""),
            "aid": str(p.get("alterId", 0)),
            "scy": p.get("cipher", "auto"),
            "net": "tcp",
            "type": "none",
            "tls": "",
        }
        if p.get("tls"):
            v["tls"] = "tls"
            if p.get("sni"):
                v["sni"] = p["sni"]
        transport = p.get("network", p.get("transport", {}))
        if isinstance(transport, str):
            v["net"] = transport
        elif isinstance(transport, dict):
            v["net"] = transport.get("type", "tcp")
            if v["net"] == "ws":
                opts = p.get("ws-opts", {})
                if opts.get("path"):
                    v["path"] = opts["path"]
                if opts.get("headers", {}).get("Host"):
                    v["host"] = opts["headers"]["Host"]
            elif v["net"] == "grpc":
                opts = p.get("grpc-opts", {})
                if opts.get("grpc-service-name"):
                    v["path"] = opts["grpc-service-name"]
        return "vmess://" + base64.b64encode(json.dumps(v, ensure_ascii=False).encode()).decode()

    def _vless_to_link(self, p):
        uuid = quote(p.get("uuid", ""))
        server = p.get("server", "")
        port = p.get("port", "")
        name = quote(p.get("name", ""))
        params = []
        if p.get("tls"):
            params.append("security=tls")
        if p.get("sni"):
            params.append(f"sni={p['sni']}")
        if p.get("flow"):
            params.append(f"flow={p['flow']}")
        transport = p.get("network", p.get("transport", {}))
        if isinstance(transport, dict):
            ttype = transport.get("type", "")
            if ttype:
                params.append(f"type={ttype}")
                if ttype == "ws":
                    if transport.get("path"):
                        params.append(f"path={transport['path']}")
                    if transport.get("headers", {}).get("Host"):
                        params.append(f"host={transport['headers']['Host']}")
                elif ttype == "grpc":
                    if transport.get("service_name"):
                        params.append(f"serviceName={transport['service_name']}")
        param_str = "&".join(params)
        return f"vless://{uuid}@{server}:{port}?{param_str}#{name}"

    def _ss_to_link(self, p):
        cipher = p.get("cipher", "aes-128-gcm")
        password = p.get("password", "")
        server = p.get("server", "")
        port = p.get("port", "")
        name = quote(p.get("name", ""))
        userinfo = base64.urlsafe_b64encode(f"{cipher}:{password}".encode()).decode().rstrip("=")
        return f"ss://{userinfo}@{server}:{port}#{name}"

    def _trojan_to_link(self, p):
        password = quote(p.get("password", ""))
        server = p.get("server", "")
        port = p.get("port", "")
        name = quote(p.get("name", ""))
        params = []
        if p.get("sni"):
            params.append(f"sni={p['sni']}")
        transport = p.get("network", p.get("transport", {}))
        if isinstance(transport, dict):
            ttype = transport.get("type", "")
            if ttype:
                params.append(f"type={ttype}")
                if ttype == "ws":
                    if transport.get("path"):
                        params.append(f"path={transport['path']}")
                    if transport.get("headers", {}).get("Host"):
                        params.append(f"host={transport['headers']['Host']}")
        param_str = "&".join(params) if params else ""
        return f"trojan://{password}@{server}:{port}?{param_str}#{name}"

    def _hysteria2_to_link(self, p):
        password = quote(p.get("password", ""))
        server = p.get("server", "")
        port = p.get("port", 443)
        name = quote(p.get("name", ""))
        params = []
        if p.get("sni"):
            params.append(f"sni={p['sni']}")
        if p.get("obfs"):
            params.append(f"obfs={p['obfs']}")
        if p.get("obfs-password"):
            params.append(f"obfs-password={p['obfs-password']}")
        param_str = "&".join(params) if params else ""
        return f"hysteria2://{password}@{server}:{port}?{param_str}#{name}"

    def is_fake_node(self, node):
        try:
            server = node.get("server", "")
            port = node.get("server_port") or node.get("port")
            if not server or "." not in server:
                return True
            if server in FAKE_IPS:
                return True
            if port and int(port) < 20:
                return True
            for domain in FAKE_DOMAINS:
                if server == domain.lstrip("."):
                    return True
                if server.endswith(domain):
                    return True
        except (ValueError, TypeError, AttributeError):
            pass
        return False
