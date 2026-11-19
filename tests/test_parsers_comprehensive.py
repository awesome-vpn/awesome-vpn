"""Comprehensive unit tests for active protocol parsers under core/parsers/."""

import base64
import json

from core.parsers import hysteria2, ss, trojan, tuic, vless, vmess


def test_hysteria2_parser_full_and_fallback_options():
    uri = (
        "hysteria2://pw123@[2001:4860:1::1]:443,10000-20000/"
        "?sni=hy2.example&upmbps=50&downmbps=300&obfs=salamander&obfs-password=obfspw"
        "&alpn={h3,h3-29}&allowInsecure=1#HY2Node"
    )
    node = hysteria2.parse(uri)
    assert node["type"] == "hysteria2"
    assert node["tag"] == "HY2Node"
    assert node["server"] == "2001:4860:1::1"
    assert node["server_port"] == 443
    assert node["server_ports"] == ["10000:20000"]
    assert node["password"] == "pw123"
    assert node["up_mbps"] == 50
    assert node["down_mbps"] == 300
    assert node["obfs"] == {"type": "salamander", "password": "obfspw"}
    assert node["tls"]["insecure"] is True
    assert node["tls"]["alpn"] == ["h3", "h3-29"]

    minimal = hysteria2.parse("hy2://pw@1.2.3.4:8443?auth=overridepw&sni=None")
    assert minimal["password"] == "overridepw"
    assert "server_name" not in minimal["tls"]

    no_sni = hysteria2.parse("hy2://pw@1.2.3.4:8443")
    assert no_sni["tls"]["insecure"] is True


def test_trojan_parser_transports_and_multiplex():
    assert trojan.parse("trojan://invalid-without-at") is None

    ws_uri = (
        "trojan://trpass@1.2.3.4:443/?type=ws&path=/ws?ed=2048&host=ws.example"
        "&sni=sni.example&fp=chrome&alpn={h2,http/1.1}&allowInsecure=true"
        "&protocol=smux&max-streams=16&padding=True#TrWS"
    )
    node = trojan.parse(ws_uri)
    assert node["type"] == "trojan"
    assert node["tag"] == "TrWS"
    assert node["tls"] == {
        "enabled": True,
        "insecure": True,
        "alpn": ["h2", "http/1.1"],
        "server_name": "sni.example",
        "utls": {"enabled": True, "fingerprint": "chrome"},
    }
    assert node["transport"] == {"type": "ws", "path": "/ws", "headers": {"Host": "ws.example"}}
    assert node["multiplex"] == {
        "enabled": True,
        "protocol": "smux",
        "max_streams": 16,
        "padding": True,
    }

    h2_node = trojan.parse("trojan://pw@node.example:443?type=h2&path=/h2")
    assert h2_node["transport"] == {"type": "http", "host": "node.example", "path": "/h2"}

    grpc_node = trojan.parse(
        "trojan://pw@node.example:443?type=grpc&serviceName=svc"
        "&protocol=yamux&max-connections=4&min-streams=2"
    )
    assert grpc_node["transport"] == {"type": "grpc", "service_name": "svc"}
    assert grpc_node["multiplex"] == {
        "enabled": True,
        "protocol": "yamux",
        "max_connections": 4,
        "min_streams": 2,
    }


def test_tuic_parser_variants():
    uri = (
        "tuic://uuid-1:tuicpass@[2001:4860:1::2]:443/"
        "?congestion_control=cubic&udp_relay_mode=native&alpn={h3}"
        "&allow_insecure=true&sni=tuic.example#TuicTag"
    )
    node = tuic.parse(uri)
    assert node["type"] == "tuic"
    assert node["server"] == "2001:4860:1::2"
    assert node["uuid"] == "uuid-1"
    assert node["password"] == "tuicpass"
    assert node["congestion_control"] == "cubic"
    assert node["udp_relay_mode"] == "native"
    assert node["tls"] == {
        "enabled": True,
        "alpn": ["h3"],
        "insecure": True,
        "server_name": "tuic.example",
    }

    peer_node = tuic.parse("tuic://uuid-2@1.2.3.4:443?password=qpw&disable_sni=0")
    assert peer_node["password"] == "qpw"
    assert peer_node["tls"]["server_name"] == ""


def test_vless_parser_reality_transports_and_shadowrocket():
    assert vless.parse("vless://broken") is None
    assert vless.parse("vless://uuid@1.2.3.4:notaport#bad") is None

    reality_uri = (
        "vless://uuid-r@[2001:4860:1::3]:443?security=reality&pbk=pk123&sid=none"
        "&fp=chrome&flow=xtls-rprx-vision&sni=apple.com&allowInsecure=1#RNode"
    )
    node = vless.parse(reality_uri)
    assert node["server"] == "2001:4860:1::3"
    assert node["flow"] == "xtls-rprx-vision"
    assert node["tls"]["insecure"] is True
    assert "short_id" not in node["tls"]["reality"]

    ws_uri = (
        "vless://uuid-w@1.2.3.4:443?tls=1&type=ws&path=/ws?ed=2048&host=cdn.example"
        "&sni=None&remarks=Renamed#FragIgnored"
    )
    ws_node = vless.parse(ws_uri)
    assert ws_node["tag"] == "Renamed"
    assert ws_node["tls"]["server_name"] == "cdn.example"
    assert ws_node["transport"]["max_early_data"] == 2048
    assert ws_node["transport"]["early_data_header_name"] == "Sec-WebSocket-Protocol"

    sr_uri = (
        "vless://uuid-sr@1.2.3.4:443?tls=1&obfs=websocket&path=/sr?ed=1024"
        "&obfsParam=sr.example&protocol=h2mux&max-streams=8&padding=True#SR"
    )
    sr_node = vless.parse(sr_uri)
    assert sr_node["transport"]["type"] == "ws"
    assert sr_node["transport"]["max_early_data"] == 1024
    assert sr_node["multiplex"]["max_streams"] == 8

    http_node = vless.parse("vless://u@1.2.3.4:80?type=http#H")
    assert http_node["transport"] == {"type": "http"}
    grpc_node = vless.parse(
        "vless://u@1.2.3.4:443?type=grpc&serviceName=g&protocol=smux&max-connections=2&min-streams=1#G"
    )
    assert grpc_node["transport"] == {"type": "grpc", "service_name": "g"}
    assert grpc_node["multiplex"]["max_connections"] == 2


def test_vmess_parser_json_and_uri_variants():
    assert vmess.parse("vmess://   ") is None
    assert vmess.parse("vmess://not_valid_base64!!!") is None
    bad_json = base64.b64encode(b"{bad json").decode()
    assert vmess.parse(f"vmess://{bad_json}") is None

    ws_payload = {
        "ps": "WSNode",
        "add": "1.2.3.4",
        "port": 443,
        "id": "uuid-ws",
        "scy": "gun",
        "aid": 2,
        "tls": "tls",
        "verify_cert": True,
        "sni": "sni.example",
        "fp": "chrome",
        "net": "ws",
        "host": "cdn.example",
        "path": "/chat?ed=2048",
    }
    ws_b64 = base64.b64encode(json.dumps(ws_payload).encode()).decode()
    ws_node = vmess.parse(f"vmess://{ws_b64}")
    assert ws_node["security"] == "auto"
    assert ws_node["alter_id"] == 2
    assert ws_node["tls"]["insecure"] is True
    assert ws_node["tls"]["utls"] == {"enabled": True, "fingerprint": "chrome"}
    assert ws_node["transport"]["max_early_data"] == 2048

    h2_payload = {
        "ps": "H2Node",
        "add": "1.2.3.4",
        "port": 443,
        "id": "uuid-h2",
        "net": "h2",
        "host": "h2.example",
        "headers": {"X-Test": "1"},
        "path": ["/p1", "/p2"],
        "tls": "tls",
        "verify_cert": False,
        "protocol": "yamux",
        "max_connections": 4,
        "min_streams": 2,
        "padding": True,
    }
    h2_node = vmess.parse("vmess://" + base64.b64encode(json.dumps(h2_payload).encode()).decode())
    assert h2_node["tls"]["insecure"] is False
    assert h2_node["transport"]["method"] == "GET"
    assert h2_node["transport"]["path"] == "/p1"
    assert h2_node["multiplex"]["padding"] is True

    grpc_payload = {
        "add": "1.2.3.4",
        "port": 443,
        "id": "u",
        "net": "grpc",
        "path": "svc",
        "protocol": "smux",
        "max_streams": 10,
    }
    grpc_node = vmess.parse(
        "vmess://" + base64.b64encode(json.dumps(grpc_payload).encode()).decode()
    )
    assert grpc_node["transport"] == {"type": "grpc", "service_name": "svc"}
    assert grpc_node["multiplex"]["max_streams"] == 10

    quic_payload = {"add": "1.2.3.4", "port": 443, "id": "u", "net": "quic"}
    quic_node = vmess.parse(
        "vmess://" + base64.b64encode(json.dumps(quic_payload).encode()).decode()
    )
    assert quic_node["transport"] == {"type": "quic"}

    # Query-string non-standard VMess URI format with invalid obfsParam fallback
    creds = base64.b64encode(b"aes-128-gcm:uuid-uri@1.2.3.4:443").decode()
    uri_fmt = (
        f"vmess://{creds}?tls=tls&sni=s.example&fp=firefox&obfs=websocket"
        f"&path=/sr?ed=512&host=fallback.example&obfsParam=not-json&remarks=URIVM"
    )
    uri_node = vmess.parse(uri_fmt)
    assert uri_node["tag"] == "URIVM"
    assert uri_node["transport"]["headers"]["Host"] == "fallback.example"

    obfs_json_uri = (
        "vmess://chacha20-poly1305:uuid-2@2.3.4.5:443"
        '?security=tls&peer=peer.example&type=ws&path=/w&obfsParam={"Host":"json.example"}'
    )
    obfs_json_node = vmess.parse(obfs_json_uri)
    assert obfs_json_node["transport"]["headers"]["Host"] == "json.example"


def test_ss_parser_all_plugins_and_variants():
    assert ss.parse("ss://   ") is None
    assert ss.parse("ss://YWJjZGVm") is None

    # SIP002 unencoded userinfo@host:port + plain v2ray-plugin%3B + yamux
    sip_uri = (
        "ss://aes-256-gcm:secretpw@1.2.3.4:443"
        "?plugin=v2ray-plugin%3Bmode=websocket;host=ws.example;path=/ws;tls=true;mux=true"
        "&protocol=yamux&max-connections=4&min-streams=2&padding=True#SIPNode"
    )
    sip_node = ss.parse(sip_uri)
    assert sip_node["tag"] == "SIPNode"
    assert sip_node["method"] == "aes-256-gcm"
    assert sip_node["password"] == "secretpw"
    assert sip_node["plugin"] == "v2ray-plugin"
    assert sip_node["multiplex"] == {
        "enabled": True,
        "protocol": "yamux",
        "max_connections": 4,
        "min_streams": 2,
        "padding": True,
    }

    # Legacy whole-userinfo@host:port base64
    legacy = base64.b64encode(b"chacha20-poly1305:pw@1.2.3.4:8388").decode()
    legacy_node = ss.parse(f"ss://{legacy}?remarks=LegacySS")
    assert legacy_node["method"] == "chacha20-ietf-poly1305"
    assert legacy_node["tag"] == "LegacySS"

    # auto cipher rejected
    auto_b64 = base64.b64encode(b"auto:pw").decode()
    assert ss.parse(f"ss://{auto_b64}@1.2.3.4:8388#Auto") is None

    # v2ray-plugin base64 payload + uot + multiplex
    v2_auth = base64.b64encode(b"xchacha20-poly1305:pw").decode()
    v2_opts = base64.b64encode(
        json.dumps(
            {
                "mode": "websocket",
                "host": "cdn.example",
                "path": "/ws",
                "mux": 1,
                "tls": 1,
                "skip-cert-verify": 1,
            }
        ).encode()
    ).decode()
    v2_uri = f"ss://{v2_auth}@1.2.3.4:443?plugin=v2ray-plugin;{v2_opts}&uot=1&protocol=smux&max-streams=8#V2"
    v2_node = ss.parse(v2_uri)
    assert v2_node["method"] == "xchacha20-ietf-poly1305"
    assert v2_node["plugin"] == "v2ray-plugin"
    assert "tls;" in v2_node["plugin_opts"]
    assert v2_node["udp_over_tcp"] == {"enabled": True, "version": 2}
    assert v2_node["multiplex"]["max_streams"] == 8

    # shadow-tls detour tuple return
    stls_opts = base64.b64encode(
        json.dumps(
            {"version": "3", "password": "stpw", "host": "sni.example", "port": "8443", "fp": "ut"}
        ).encode()
    ).decode()
    stls_uri = f"ss://{v2_auth}@1.2.3.4:443?shadow-tls={stls_opts}#STLS"
    res = ss.parse(stls_uri)
    assert isinstance(res, tuple)
    main_node, tls_node = res
    assert main_node["detour"] == "STLS_shadowtls"
    assert tls_node["type"] == "shadowtls"
    assert tls_node["version"] == 3
    assert tls_node["server_port"] == 8443
