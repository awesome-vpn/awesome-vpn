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
