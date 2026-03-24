# core/converters/clash.py
"""Convert sing-box outbounds to Clash proxy format."""
import logging
from typing import Optional, Dict, Any, List

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


def _convert_hysteria2(node: Dict[str, Any]) -> Dict[str, Any]:
    proxy = {
        "name": node.get("tag", "hysteria2"),
        "type": "hysteria2",
        "server": node.get("server", ""),
        "port": node.get("server_port", 0),
        "password": node.get("password", ""),
    }
    tls = node.get("tls") or {}
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


def to_clash_proxies(nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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
