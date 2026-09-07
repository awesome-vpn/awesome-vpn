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

    def export_all(
        self,
        curated_nodes: list[dict[str, Any]],
        source_links: dict[int, str],
        raw_links: list[str] | None = None,
    ) -> dict[str, str]:
        """Generate only the 3 standardized subscription feeds."""
        return {
            "sing-box": self.export_curated_singbox(curated_nodes),
            "clash": self.export_curated_clash(curated_nodes),
            "all": self.export_curated_base64(curated_nodes, source_links),
        }
