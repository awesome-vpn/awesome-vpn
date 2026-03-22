# tests/test_clash_converter.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.converters.clash import to_clash_proxy, to_clash_proxies


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


def test_vmess_tls_fields():
    node = {
        "type": "vmess",
        "tag": "vmess-tls",
        "server": "1.2.3.4",
        "server_port": 443,
        "uuid": "abc",
        "tls": {"enabled": True, "server_name": "example.com", "insecure": True}
    }
    result = to_clash_proxy(node)
    assert result["tls"] is True
    assert result["servername"] == "example.com"
    assert result["skip-cert-verify"] is True


def test_vmess_websocket_transport():
    node = {
        "type": "vmess",
        "tag": "vmess-ws",
        "server": "1.2.3.4",
        "server_port": 80,
        "uuid": "abc",
        "transport": {
            "type": "ws",
            "path": "/path",
            "headers": {"Host": "cdn.example.com"}
        }
    }
    result = to_clash_proxy(node)
    assert result["network"] == "ws"
    assert result["ws-opts"]["path"] == "/path"
    assert result["ws-opts"]["headers"]["Host"] == "cdn.example.com"


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
    assert result["reality-opts"]["short-id"] == "sid456"
    assert result["client-fingerprint"] == "chrome"


def test_vless_with_flow():
    node = {
        "type": "vless",
        "tag": "vless-flow",
        "server": "2.3.4.5",
        "server_port": 443,
        "uuid": "uuid-test",
        "flow": "xtls-rprx-vision",
        "tls": {"enabled": True}
    }
    result = to_clash_proxy(node)
    assert result["flow"] == "xtls-rprx-vision"


def test_vless_grpc_transport():
    node = {
        "type": "vless",
        "tag": "vless-grpc",
        "server": "2.3.4.5",
        "server_port": 443,
        "uuid": "uuid-test",
        "tls": {"enabled": True},
        "transport": {"type": "grpc", "service_name": "myservice"}
    }
    result = to_clash_proxy(node)
    assert result["network"] == "grpc"
    assert result["grpc-opts"]["grpc-service-name"] == "myservice"


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
    assert result["password"] == "pass123"
    assert result["server"] == "3.4.5.6"
    assert result["port"] == 8388


def test_ss_alias():
    """Ensure 'ss' type alias maps to shadowsocks converter."""
    node = {
        "type": "ss",
        "tag": "ss-alias",
        "server": "5.6.7.8",
        "server_port": 1234,
        "password": "pw",
        "method": "chacha20-ietf-poly1305"
    }
    result = to_clash_proxy(node)
    assert result["type"] == "ss"
    assert result["cipher"] == "chacha20-ietf-poly1305"


def test_trojan_conversion():
    node = {
        "type": "trojan",
        "tag": "trojan-node",
        "server": "4.5.6.7",
        "server_port": 443,
        "password": "trpass",
        "tls": {"enabled": True, "server_name": "trojan.example.com", "insecure": False}
    }
    result = to_clash_proxy(node)
    assert result["type"] == "trojan"
    assert result["password"] == "trpass"
    assert result["sni"] == "trojan.example.com"


def test_trojan_insecure():
    node = {
        "type": "trojan",
        "tag": "trojan-insecure",
        "server": "4.5.6.7",
        "server_port": 443,
        "password": "pw",
        "tls": {"enabled": True, "insecure": True}
    }
    result = to_clash_proxy(node)
    assert result["skip-cert-verify"] is True


def test_trojan_websocket_transport():
    node = {
        "type": "trojan",
        "tag": "trojan-ws",
        "server": "4.5.6.7",
        "server_port": 443,
        "password": "pw",
        "transport": {"type": "ws", "path": "/ws"}
    }
    result = to_clash_proxy(node)
    assert result["network"] == "ws"
    assert result["ws-opts"]["path"] == "/ws"


def test_hysteria2_conversion():
    node = {
        "type": "hysteria2",
        "tag": "hy2-node",
        "server": "5.6.7.8",
        "server_port": 443,
        "password": "hypass",
        "tls": {"server_name": "hy2.example.com", "insecure": True}
    }
    result = to_clash_proxy(node)
    assert result["type"] == "hysteria2"
    assert result["password"] == "hypass"
    assert result["sni"] == "hy2.example.com"
    assert result["skip-cert-verify"] is True


def test_hysteria2_alias():
    """Ensure 'hy2' type alias maps to hysteria2 converter."""
    node = {
        "type": "hy2",
        "tag": "hy2-alias",
        "server": "5.6.7.8",
        "server_port": 443,
        "password": "pw",
        "tls": {}
    }
    result = to_clash_proxy(node)
    assert result["type"] == "hysteria2"


def test_tuic_conversion():
    node = {
        "type": "tuic",
        "tag": "tuic-node",
        "server": "6.7.8.9",
        "server_port": 443,
        "uuid": "tuic-uuid",
        "password": "tuicpass",
        "congestion_control": "bbr",
        "tls": {"alpn": ["h3"]}
    }
    result = to_clash_proxy(node)
    assert result["type"] == "tuic"
    assert result["uuid"] == "tuic-uuid"
    assert result["congestion-controller"] == "bbr"
    assert result["alpn"] == ["h3"]


def test_tuic_alpn_string_normalized_to_list():
    node = {
        "type": "tuic",
        "tag": "tuic-node",
        "server": "6.7.8.9",
        "server_port": 443,
        "uuid": "uuid",
        "password": "pw",
        "tls": {"alpn": "h3"}
    }
    result = to_clash_proxy(node)
    assert result["alpn"] == ["h3"]


def test_unsupported_type():
    assert to_clash_proxy({"type": "unknown"}) is None


def test_missing_type():
    assert to_clash_proxy({}) is None


def test_to_clash_proxies_filters_unsupported():
    nodes = [
        {"type": "vmess", "tag": "n1", "server": "1.1.1.1", "server_port": 443, "uuid": "u1"},
        {"type": "unknown", "tag": "bad"},
        {"type": "shadowsocks", "tag": "n2", "server": "2.2.2.2", "server_port": 8388,
         "password": "pw", "method": "aes-256-gcm"},
    ]
    result = to_clash_proxies(nodes)
    assert len(result) == 2
    assert result[0]["name"] == "n1"
    assert result[1]["name"] == "n2"


def test_to_clash_proxies_empty_list():
    assert to_clash_proxies([]) == []


def test_vmess_default_tag_when_missing():
    node = {"type": "vmess", "server": "1.2.3.4", "server_port": 80, "uuid": "u"}
    result = to_clash_proxy(node)
    assert result["name"] == "vmess"


def test_vmess_alter_id_default_zero():
    node = {"type": "vmess", "tag": "n", "server": "1.2.3.4", "server_port": 80, "uuid": "u"}
    result = to_clash_proxy(node)
    assert result["alterId"] == 0
