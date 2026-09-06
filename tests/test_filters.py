"""Unit tests for HoneypotFilter and PrescreenFunnel."""

from core.filters.honeypot import HoneypotFilter
from core.filters.prescreen import PrescreenFunnel


def test_honeypot_filter():
    # RFC 1918 Private IP checks
    assert HoneypotFilter.is_honeypot_or_invalid({"server": "127.0.0.1", "port": 443}) is True
    assert HoneypotFilter.is_honeypot_or_invalid({"server": "192.168.1.1", "port": 8080}) is True
    assert HoneypotFilter.is_honeypot_or_invalid({"server": "10.0.0.5", "port": 1080}) is True
    assert HoneypotFilter.is_honeypot_or_invalid({"server": "172.16.0.1", "port": 443}) is True

    # Public DNS and search engine fakes
    assert HoneypotFilter.is_honeypot_or_invalid({"server": "8.8.8.8", "port": 53}) is True
    assert HoneypotFilter.is_honeypot_or_invalid({"server": "sub.google.com", "port": 443}) is True

    # Bad ports
    assert HoneypotFilter.is_honeypot_or_invalid({"server": "1.2.3.4", "port": 10}) is True
    assert HoneypotFilter.is_honeypot_or_invalid({"server": "1.2.3.4", "port": 99999}) is True

    # Legitimate public node
    assert HoneypotFilter.is_honeypot_or_invalid({"server": "1.2.3.4", "port": 443}) is False
    assert (
        HoneypotFilter.is_honeypot_or_invalid({"server": "node.example.org", "port": 8443}) is False
    )


def test_prescreen_funnel_workflow():
    funnel = PrescreenFunnel(max_validation_candidates=2, local_mode=True)

    candidates = [
        ({"server": "127.0.0.1", "port": 443, "type": "vmess"}, "vmess://bad1", "TG"),
        ({"server": "1.1.1.2", "port": 443, "type": "vmess"}, "vmess://ok1", "TG"),
        ({"server": "1.1.1.3", "port": 443, "type": "hysteria2"}, "hy2://ok2", "GH"),
        ({"server": "1.1.1.4", "port": 443, "type": "tuic"}, "tuic://ok3", "GH"),
    ]

    result = funnel.filter(candidates)
    # 127.0.0.1 should be dropped by Stage 1
    assert not any(item[0]["server"] == "127.0.0.1" for item in result)

    # Max candidates was 2, so should cap to 2
    assert len(result) == 2

    # High-priority protocols (hysteria2, tuic) should beat vmess in sorting
    types = [item[0]["type"] for item in result]
    assert "hysteria2" in types or "tuic" in types


def test_fair_source_interleaving():
    funnel = PrescreenFunnel(max_validation_candidates=3, local_mode=True)
    candidates = [
        ({"server": "2.2.2.1", "port": 443, "type": "vless"}, "vless://1", "SourceA"),
        ({"server": "2.2.2.2", "port": 443, "type": "vless"}, "vless://2", "SourceA"),
        ({"server": "2.2.2.3", "port": 443, "type": "vless"}, "vless://3", "SourceA"),
        ({"server": "3.3.3.1", "port": 443, "type": "vless"}, "vless://4", "SourceB"),
        ({"server": "4.4.4.1", "port": 443, "type": "vless"}, "vless://5", "SourceC"),
    ]
    result = funnel.filter(candidates)
    sources = [item[2] for item in result]
    # In round 0, each source gets 1 node
    assert len(result) == 3
    assert "SourceA" in sources
    assert "SourceB" in sources
    assert "SourceC" in sources
