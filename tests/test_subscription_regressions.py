"""Regression coverage for subscription ingestion, prescreening and Clash export."""

import base64
import http.server
import socket
import threading

import yaml

from core.filters.honeypot import HoneypotFilter
from core.filters.prescreen import PrescreenFunnel, fast_tcp_ping
from core.matrix.exporter import MatrixExporter
from core.parsers import ss, vless
from core.spider import Spider


def test_complete_line_subscription_over_http():
    links = [
        f"vless://00000000-0000-0000-0000-000000000001@node{i}.example:443#entry{i}"
        for i in range(250)
    ]
    payload = ("\n".join(links) + "\n").encode()

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, *args):
            pass

    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        spider = Spider()
        content = spider.fetch_url(f"http://127.0.0.1:{server.server_port}/feed")
        assert content.encode() == payload
        assert set(spider.parse_subscription(content)) == set(links)
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def test_ipv6_parser_and_prescreen():
    uri = "vless://00000000-0000-0000-0000-000000000001@[2001:4860:1234::2]:443#IPv6"
    node = vless.parse(uri)
    assert PrescreenFunnel(local_mode=True).filter([(node, uri, "fixture")])
    for address in ("::1", "fc00::1", "fe80::1", "::", "ff02::1", "192.168.1.1"):
        assert HoneypotFilter.is_honeypot_or_invalid({"server": address, "server_port": 443})


def test_tcp_prescreen_ipv6_loopback():
    with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as listener:
        listener.bind(("::1", 0))
        listener.listen(1)
        assert fast_tcp_ping("::1", listener.getsockname()[1], timeout=1)
        connection, _ = listener.accept()
        connection.close()


def test_ss_plugin_survives_clash_export(tmp_path):
    auth = base64.b64encode(b"aes-128-gcm:fixture-password").decode()
    for mode in ("http", "tls"):
        uri = (
            f"ss://{auth}@node.example:443?"
            f"plugin=obfs-local;obfs={mode};obfs-host=example.com#fixture"
        )
        node = ss.parse(uri)
        path = MatrixExporter(str(tmp_path)).export_curated_clash([node])
        with open(path, encoding="utf-8") as stream:
            exported = yaml.safe_load(stream)
        proxy = exported["proxies"][0]
        assert proxy["plugin"] == "obfs"
        assert proxy["plugin-opts"] == {"mode": mode, "host": "example.com"}
        assert proxy["name"] in exported["proxy-groups"][1]["proxies"]


def test_ss_v2ray_and_unsupported_plugin_clash_export(tmp_path):
    v2ray_node = {
        "type": "shadowsocks",
        "tag": "ss-v2ray",
        "server": "node.example",
        "server_port": 443,
        "method": "aes-128-gcm",
        "password": "fixture-password",
        "plugin": "v2ray-plugin",
        "plugin_opts": "mode=websocket;host=cdn.example;path=/ws;tls;mux=1",
    }
    unsupported_node = {
        "type": "shadowsocks",
        "tag": "ss-unsupported",
        "server": "node2.example",
        "server_port": 443,
        "method": "aes-128-gcm",
        "password": "fixture-password",
        "plugin": "custom-plugin",
        "plugin_opts": "foo=bar",
    }
    path = MatrixExporter(str(tmp_path)).export_curated_clash([v2ray_node, unsupported_node])
    with open(path, encoding="utf-8") as stream:
        exported = yaml.safe_load(stream)
    assert len(exported["proxies"]) == 1
    proxy = exported["proxies"][0]
    assert proxy["plugin"] == "v2ray-plugin"
    assert proxy["plugin-opts"] == {
        "mode": "websocket",
        "host": "cdn.example",
        "path": "/ws",
        "tls": True,
        "mux": True,
    }
