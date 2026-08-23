"""Tests for China-aware quality scoring."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.quality import china_resistance_score, filter_by_china_probe, quality_score


def test_reality_ws_443_scores_high():
    node = {
        "type": "vless",
        "server_port": 443,
        "tls": {
            "enabled": True,
            "server_name": "www.apple.com",
            "reality": {"enabled": True},
            "utls": {"enabled": True},
        },
        "transport": {"type": "ws", "headers": {"Host": "cdn.example.com"}},
    }
    assert china_resistance_score(node) >= 20


def test_shadowsocks_no_tls_scores_low():
    node = {"type": "shadowsocks", "server_port": 8388, "tls": {}}
    assert china_resistance_score(node) < 0


def test_quality_score_latency_penalty():
    node = {
        "type": "vless",
        "server_port": 443,
        "tls": {"enabled": True, "server_name": "apple.com", "reality": {"enabled": True}},
    }
    fast = quality_score(node, latency_ms=200)
    slow = quality_score(node, latency_ms=1200)
    assert fast > slow


def test_filter_by_china_probe_no_url_pass_through():
    nodes = [{"server": "1.1.1.1", "server_port": 443}]
    assert filter_by_china_probe(nodes, "") == nodes
    assert filter_by_china_probe(nodes, None) == nodes


def test_filter_by_china_probe_uses_probe(monkeypatch):
    nodes = [{"server": "1.1.1.1", "server_port": 443}, {"server": "2.2.2.2", "server_port": 443}]

    class FakeResp:
        status_code = 200
        headers = {"Content-Type": "application/json"}

        def json(self):
            return {"ok": True}

    def fake_post(url, json=None, timeout=None):
        # only 1.1.1.1 reachable
        if json["server"] == "1.1.1.1":
            return FakeResp()

        # 2.2.2.2 not reachable
        class FailResp:
            status_code = 200
            headers = {"Content-Type": "application/json"}

            def json(self):
                return {"ok": False}

        return FailResp()

    monkeypatch.setattr("core.quality.requests.post", fake_post)
    kept = filter_by_china_probe(nodes, "https://probe.example/check")
    assert len(kept) == 1
    assert kept[0]["server"] == "1.1.1.1"
