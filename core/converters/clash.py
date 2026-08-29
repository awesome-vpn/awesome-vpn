# core/converters/clash.py
"""Convert sing-box outbounds to Clash proxy format."""

import logging
from typing import Any

logger = logging.getLogger(__name__)

# Emoji for ideal clash format (subconverter emoji=true)
COUNTRY_EMOJI = {
    "United States": "🇺🇸",
    "Japan": "🇯🇵",
    "Germany": "🇩🇪",
    "Netherlands": "🇳🇱",
    "Singapore": "🇸🇬",
    "Hong Kong": "🇭🇰",
    "Taiwan": "🇹🇼",
    "United Kingdom": "🇬🇧",
    "France": "🇫🇷",
    "Canada": "🇨🇦",
    "Australia": "🇦🇺",
    "South Korea": "🇰🇷",
    "Russia": "🇷🇺",
    "Turkey": "🇹🇷",
    "Sweden": "🇸🇪",
    "Switzerland": "🇨🇭",
    "Brazil": "🇧🇷",
    "India": "🇮🇳",
    "Italy": "🇮🇹",
    "Spain": "🇪🇸",
    "Poland": "🇵🇱",
    "Romania": "🇷🇴",
    "Norway": "🇳🇴",
    "Finland": "🇫🇮",
    "Denmark": "🇩🇰",
    "Ireland": "🇮🇪",
    "Austria": "🇦🇹",
    "Belgium": "🇧🇪",
    "Czech Republic": "🇨🇿",
    "Greece": "🇬🇷",
    "Israel": "🇮🇱",
    "Mexico": "🇲🇽",
    "Argentina": "🇦🇷",
    "Chile": "🇨🇱",
    "Colombia": "🇨🇴",
    "Malaysia": "🇲🇾",
    "Thailand": "🇹🇭",
    "Vietnam": "🇻🇳",
    "Indonesia": "🇮🇩",
    "Philippines": "🇵🇭",
    "New Zealand": "🇳🇿",
    "South Africa": "🇿🇦",
    "United Arab Emirates": "🇦🇪",
    "Saudi Arabia": "🇸🇦",
    "Egypt": "🇪🇬",
    "Nigeria": "🇳🇬",
    "Kenya": "🇰🇪",
    "Unknown": "🏳️",
}

EMOJI_FALLBACK = "🌍"


def _emoji_for_tag(tag: str) -> str:
    for country, emoji in COUNTRY_EMOJI.items():
        if country in tag:
            return emoji
    return EMOJI_FALLBACK


def to_clash_proxy(node: dict[str, Any]) -> dict[str, Any] | None:
    """Convert a sing-box outbound dict to Clash proxy dict."""
    ntype = node.get("type", "").lower()
    converter = CONVERTERS.get(ntype)
    if not converter:
        logger.debug(f"Unsupported node type for Clash: {ntype}")
        return None
    return converter(node)


def _convert_vmess(node: dict[str, Any]) -> dict[str, Any]:
    tag = node.get("tag", "vmess")
    proxy = {
        "name": f"{_emoji_for_tag(tag)} {tag}",
        "type": "vmess",
        "server": node.get("server", ""),
        "port": node.get("server_port", 0),
        "uuid": node.get("uuid", ""),
        "alterId": node.get("alter_id", 0),
        "cipher": node.get("security", "auto"),
        "udp": True,
    }
    tls = node.get("tls") or {}
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


def _convert_vless(node: dict[str, Any]) -> dict[str, Any]:
    tag = node.get("tag", "vless")
    proxy = {
        "name": f"{_emoji_for_tag(tag)} {tag}",
        "type": "vless",
        "server": node.get("server", ""),
        "port": node.get("server_port", 0),
        "uuid": node.get("uuid", ""),
        "udp": True,
    }
    if node.get("flow"):
        proxy["flow"] = node["flow"]

    tls = node.get("tls") or {}
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
        if net_type == "ws":
            proxy["network"] = "ws"
            ws_opts = {}
            if transport.get("path"):
                ws_opts["path"] = transport["path"]
            if transport.get("headers", {}).get("Host"):
                ws_opts["headers"] = {"Host": transport["headers"]["Host"]}
            if ws_opts:
                proxy["ws-opts"] = ws_opts
        elif net_type == "grpc":
            proxy["network"] = "grpc"
            grpc_opts = {}
            if transport.get("service_name"):
                grpc_opts["grpc-service-name"] = transport["service_name"]
            if grpc_opts:
                proxy["grpc-opts"] = grpc_opts

    return proxy


def _convert_shadowsocks(node: dict[str, Any]) -> dict[str, Any]:
    tag = node.get("tag", "ss")
    return {
        "name": f"{_emoji_for_tag(tag)} {tag}",
        "type": "ss",
        "server": node.get("server", ""),
        "port": node.get("server_port", 0),
        "password": node.get("password", ""),
        "cipher": node.get("method", "none"),
        "udp": True,
    }


def _convert_trojan(node: dict[str, Any]) -> dict[str, Any]:
    tag = node.get("tag", "trojan")
    proxy = {
        "name": f"{_emoji_for_tag(tag)} {tag}",
        "type": "trojan",
        "server": node.get("server", ""),
        "port": node.get("server_port", 0),
        "password": node.get("password", ""),
        "udp": True,
    }
    tls = node.get("tls") or {}
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


def _convert_hysteria2(node: dict[str, Any]) -> dict[str, Any]:
    tag = node.get("tag", "hysteria2")
    proxy = {
        "name": f"{_emoji_for_tag(tag)} {tag}",
        "type": "hysteria2",
        "server": node.get("server", ""),
        "port": node.get("server_port", 0),
        "password": node.get("password", ""),
        "udp": True,
    }
    tls = node.get("tls") or {}
    if tls.get("server_name"):
        proxy["sni"] = tls["server_name"]
    if tls.get("insecure"):
        proxy["skip-cert-verify"] = True
    return proxy


def _convert_tuic(node: dict[str, Any]) -> dict[str, Any]:
    tag = node.get("tag", "tuic")
    proxy = {
        "name": f"{_emoji_for_tag(tag)} {tag}",
        "type": "tuic",
        "server": node.get("server", ""),
        "port": node.get("server_port", 0),
        "uuid": node.get("uuid", ""),
        "password": node.get("password", ""),
        "udp": True,
    }
    if node.get("congestion_control"):
        proxy["congestion-controller"] = node["congestion_control"]
    tls = node.get("tls") or {}
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


def to_clash_proxies(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert a list of sing-box nodes to Clash proxies with unique names."""
    result = []
    used_names = set()
    name_counter = {}

    for node in nodes:
        proxy = to_clash_proxy(node)
        if not proxy:
            continue

        name = proxy.get("name", "unnamed")

        # Handle duplicate names by adding suffix
        if name in used_names:
            if name not in name_counter:
                name_counter[name] = 1
            name_counter[name] += 1
            new_name = f"{name}-{name_counter[name]}"
            proxy["name"] = new_name
            used_names.add(new_name)
        else:
            used_names.add(name)

        result.append(proxy)

    return result
