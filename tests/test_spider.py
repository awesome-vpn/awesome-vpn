"""Tests for Spider — demonstrates requests mocking."""

import base64
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import MagicMock, patch

from core.spider import Spider


def test_extract_links_simple():
    spider = Spider()
    text = "ss://abc@1.2.3.4:8388#test vmess://xxx vless://yyy@1.1.1.1:443?x=1#z"
    links = spider.extract_links(text)
    assert any(link.startswith("ss://") for link in links)
    assert any(link.startswith("vmess://") for link in links)
    assert any(link.startswith("vless://") for link in links)


def test_parse_subscription_base64():
    spider = Spider()
    raw = "ss://test@1.2.3.4:8388#tag\nvless://uuid@2.2.2.2:443#tag2"
    b64 = base64.b64encode(raw.encode()).decode()
    links = spider.parse_subscription(b64)
    assert len(links) >= 2


def test_parse_subscription_clash_yaml():
    spider = Spider()
    clash_yaml = """
proxies:
  - name: test-ss
    type: ss
    server: 1.2.3.4
    port: 8388
    cipher: aes-256-gcm
    password: pass123
"""
    links = spider.parse_subscription(clash_yaml)
    assert any("ss://" in link for link in links)


def test_is_fake_node():
    spider = Spider()
    assert spider.is_fake_node({"server": "8.8.8.8", "server_port": 8388}) is True
    assert spider.is_fake_node({"server": "1.2.3.4", "server_port": 443}) is False
    assert spider.is_fake_node({"server": "", "server_port": 443}) is True
    assert spider.is_fake_node({"server": "google.com", "server_port": 443}) is True


def test_fetch_url_mock():
    spider = Spider()
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.iter_content.return_value = [b"ss://abc@1.2.3.4:8388#test"]
    with patch.object(spider.session, "get", return_value=mock_resp):
        content = spider.fetch_url("https://example.com/sub")
        assert content is not None


def test_spider_clash_proxy_conversions_and_extractors():
    spider = Spider()
    yaml_payload = """
proxies:
  - name: vm1
    type: vmess
    server: 1.1.1.1
    port: 443
    uuid: u1
    tls: true
    sni: vm.example
    transport:
      type: ws
    ws-opts:
      path: /ws
      headers:
        Host: h.example
  - name: vl1
    type: vless
    server: 1.1.1.2
    port: 443
    uuid: u2
    tls: true
    sni: vl.example
    flow: xtls-rprx-vision
    transport:
      type: grpc
      service_name: gsvc
  - name: ss1
    type: ss
    server: 1.1.1.3
    port: 8388
    cipher: aes-256-gcm
    password: pw
  - name: tr1
    type: trojan
    server: 1.1.1.4
    port: 443
    password: tp
    sni: tr.example
    transport:
      type: ws
      path: /tr
      headers:
        Host: tr.example
  - name: hy1
    type: hy2
    server: 1.1.1.5
    port: 443
    password: hp
    sni: hy.example
    obfs: salamander
    obfs-password: opw
"""
    links = spider.parse_subscription(yaml_payload)
    assert any(lk.startswith("vmess://") for lk in links)
    assert any(lk.startswith("vless://") for lk in links)
    assert any(lk.startswith("ss://") for lk in links)
    assert any(lk.startswith("trojan://") for lk in links)
    assert any(lk.startswith("hysteria2://") for lk in links)

    sub_text = "Download https://cdn.example/sub.txt and ignore https://github.com/sub.txt"
    subs = spider.extract_subscription_links(sub_text)
    assert subs == ["https://cdn.example/sub.txt"]

    tg_html = (
        '<div class="tgme_widget_message_text">@demo_ch <code>ss://YWVz@1.1.1.1:443#t</code></div>'
    )
    mock_tg = MagicMock(status_code=200, text=tg_html)
    with patch.object(spider.session, "get", return_value=mock_tg):
        tg_links, tg_chans = spider.fetch_telegram("@src")
    assert any(lk.startswith("ss://") for lk in tg_links)
    assert "demo_ch" in tg_chans
