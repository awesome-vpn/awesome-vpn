"""Subscription Matrix Exporter: generates curated, raw, and protocol-specific subscription feeds."""

import base64
import json
import logging
import os
from typing import Any

import yaml

from core.converters.clash import to_clash_proxies

logger = logging.getLogger(__name__)


class MatrixExporter:
    """Exports nodes into multi-tiered subscription matrix."""

    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def export_curated_singbox(self, nodes: list[dict[str, Any]]) -> str:
        """Export standardized sing-box.json with Auto url-test and PROXY selector."""
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

        path = os.path.join(self.output_dir, "sing-box.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"outbounds": outbounds}, f, indent=2, ensure_ascii=False)
        return path

    def export_curated_clash(self, nodes: list[dict[str, Any]]) -> str:
        """Export Clash YAML with secure anti-SSRF LAN rules and proxy groups."""
        proxies = to_clash_proxies(nodes)
        proxy_names = [p.get("name") for p in proxies if p.get("name")]

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
            "allow-lan": False,  # Secure default
            "mode": "Rule",
            "log-level": "info",
            "external-controller": "127.0.0.1:9090",
            "proxies": proxies,
            "proxy-groups": proxy_groups,
            # Mandatory LAN/Private IP protection rules
            "rules": [
                "DOMAIN-SUFFIX,local,DIRECT",
                "IP-CIDR,127.0.0.0/8,DIRECT,no-resolve",
                "IP-CIDR,192.168.0.0/16,DIRECT,no-resolve",
                "IP-CIDR,10.0.0.0/8,DIRECT,no-resolve",
                "IP-CIDR,172.16.0.0/12,DIRECT,no-resolve",
                "IP-CIDR,100.64.0.0/10,DIRECT,no-resolve",
                "GEOIP,LAN,DIRECT,no-resolve",
                "MATCH,PROXY",
            ],
        }

        path = os.path.join(self.output_dir, "clash.yaml")
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        return path

    def export_curated_base64(
        self, nodes: list[dict[str, Any]], source_links: dict[int, str]
    ) -> str:
        """Export base64-encoded `all` subscription file."""
        links_output = []
        for node in nodes:
            tag = node.get("tag", "")
            original_link = source_links.get(id(node), "")
            if original_link:
                base_link = (
                    original_link.rsplit("#", 1)[0] if "#" in original_link else original_link
                )
                links_output.append(f"{base_link}#{tag}")
            else:
                server = node.get("server", "")
                port = node.get("server_port") or node.get("port", "")
                ntype = node.get("type", "")
                links_output.append(f"{ntype}://{tag}@{server}:{port}")

        encoded = base64.b64encode("\n".join(links_output).encode()).decode()
        path = os.path.join(self.output_dir, "all")
        with open(path, "w", encoding="utf-8") as f:
            f.write(encoded)
        return path

    def export_raw_pool(self, raw_links: list[str]) -> str:
        """Export raw, unfiltered candidate proxy link list."""
        path = os.path.join(self.output_dir, "raw.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(raw_links))
        return path

    def export_protocol_specific(
        self, nodes: list[dict[str, Any]], source_links: dict[int, str]
    ) -> dict[str, str]:
        """Export dedicated subscription endpoints for modern protocols (Hysteria2, Reality)."""
        hy2_nodes = [n for n in nodes if n.get("type") in ("hysteria2", "hy2")]
        reality_nodes = [
            n for n in nodes if n.get("type") == "vless" and n.get("tls", {}).get("reality")
        ]

        results = {}

        # 1. Hysteria2 Clash subscription
        hy2_proxies = to_clash_proxies(hy2_nodes) if hy2_nodes else []
        hy2_names = [p["name"] for p in hy2_proxies if "name" in p]
        hy2_data = {
            "port": 7890,
            "mode": "Rule",
            "proxies": hy2_proxies,
            "proxy-groups": [
                {
                    "name": "Auto-HY2",
                    "type": "url-test",
                    "proxies": hy2_names if hy2_names else ["DIRECT"],
                    "url": "https://www.google.com/generate_204",
                    "interval": 300,
                }
            ],
            "rules": ["MATCH,Auto-HY2"],
        }
        hy2_clash_path = os.path.join(self.output_dir, "hysteria2.yaml")
        with open(hy2_clash_path, "w", encoding="utf-8") as f:
            yaml.dump(hy2_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        results["hysteria2_clash"] = hy2_clash_path

        # Hysteria2 Base64
        hy2_links = [
            source_links.get(
                id(n), f"hysteria2://{n.get('tag')}@{n.get('server')}:{n.get('server_port')}"
            )
            for n in hy2_nodes
        ]
        hy2_b64_path = os.path.join(self.output_dir, "hysteria2.txt")
        with open(hy2_b64_path, "w", encoding="utf-8") as f:
            f.write(base64.b64encode("\n".join(hy2_links).encode()).decode())
        results["hysteria2_b64"] = hy2_b64_path

        # 2. Reality Sing-box subscription
        reality_path = os.path.join(self.output_dir, "reality.json")
        with open(reality_path, "w", encoding="utf-8") as f:
            json.dump({"outbounds": reality_nodes}, f, indent=2, ensure_ascii=False)
        results["reality_singbox"] = reality_path

        return results

    def export_all(
        self,
        curated_nodes: list[dict[str, Any]],
        source_links: dict[int, str],
        raw_links: list[str],
    ) -> dict[str, str]:
        """Generate the full subscription matrix."""
        res = {
            "sing-box": self.export_curated_singbox(curated_nodes),
            "clash": self.export_curated_clash(curated_nodes),
            "all": self.export_curated_base64(curated_nodes, source_links),
            "raw": self.export_raw_pool(raw_links),
        }
        res.update(self.export_protocol_specific(curated_nodes, source_links))
        return res
