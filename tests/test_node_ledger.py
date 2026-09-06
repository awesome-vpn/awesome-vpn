"""Unit tests for NodeLedger."""

import os
import tempfile
from datetime import UTC, datetime, timedelta

import pytest

from core.node_ledger import NodeLedger
from core.quality import quality_score


@pytest.fixture
def temp_ledger():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name
    ledger = NodeLedger(path)
    yield ledger
    if os.path.exists(path):
        os.remove(path)


def test_fingerprint():
    node1 = {"type": "vless", "server": "example.com", "server_port": 443}
    node2 = {"type": "VLESS", "server": "EXAMPLE.COM", "port": 443}
    assert NodeLedger.get_fingerprint(node1) == "vless://example.com:443"
    assert NodeLedger.get_fingerprint(node2) == "vless://example.com:443"


def test_record_validation_and_streak(temp_ledger):
    node = {"type": "vless", "server": "1.2.3.4", "server_port": 443}

    # Initial pass
    temp_ledger.record_validation(node, is_valid=True, latency_ms=120.0)
    fp = NodeLedger.get_fingerprint(node)
    entry = temp_ledger.nodes[fp]
    assert entry["consecutive_passes"] == 1
    assert entry["total_checks"] == 1
    assert entry["total_passes"] == 1
    assert entry["avg_latency_ms"] == 120.0
    assert temp_ledger.get_longevity_bonus(node) == 4.0

    # Second pass
    temp_ledger.record_validation(node, is_valid=True, latency_ms=100.0)
    assert temp_ledger.nodes[fp]["consecutive_passes"] == 2
    assert temp_ledger.get_longevity_bonus(node) == 8.0

    # Third pass
    temp_ledger.record_validation(node, is_valid=True, latency_ms=110.0)
    assert temp_ledger.nodes[fp]["consecutive_passes"] == 3
    # 3 consecutive passes (15.0) + high pass rate bonus (5.0) = 20.0
    assert temp_ledger.get_longevity_bonus(node) == 20.0

    # Failure resets streak
    temp_ledger.record_validation(node, is_valid=False)
    assert temp_ledger.nodes[fp]["consecutive_passes"] == 0
    assert temp_ledger.nodes[fp]["total_checks"] == 4
    assert temp_ledger.nodes[fp]["total_passes"] == 3
    # Streak is 0, bonus is 0
    assert temp_ledger.get_longevity_bonus(node) == 0.0


def test_5_plus_streak_bonus(temp_ledger):
    node = {"type": "hysteria2", "server": "fast.hy2.com", "server_port": 8443}
    for _ in range(5):
        temp_ledger.record_validation(node, is_valid=True, latency_ms=80.0)

    # 5+ streak bonus (25.0) + high pass rate (5.0) = 30.0
    assert temp_ledger.get_longevity_bonus(node) == 30.0


def test_garbage_collection(temp_ledger):
    now = datetime.now(UTC)
    old_time = (now - timedelta(days=20)).isoformat()
    fresh_time = (now - timedelta(days=2)).isoformat()

    temp_ledger.nodes = {
        "vless://old.com:443": {
            "first_seen_at": old_time,
            "last_seen_at": old_time,
            "consecutive_passes": 5,
        },
        "vless://fresh.com:443": {
            "first_seen_at": fresh_time,
            "last_seen_at": fresh_time,
            "consecutive_passes": 1,
        },
    }

    purged = temp_ledger.garbage_collect()
    assert purged == 1
    assert "vless://old.com:443" not in temp_ledger.nodes
    assert "vless://fresh.com:443" in temp_ledger.nodes


def test_save_and_load(temp_ledger):
    node = {"type": "trojan", "server": "trojan.test", "server_port": 443}
    temp_ledger.record_validation(node, is_valid=True, latency_ms=150.0)
    temp_ledger.save()

    # Create new instance pointing to same file
    loaded = NodeLedger(temp_ledger.ledger_path)
    fp = NodeLedger.get_fingerprint(node)
    assert fp in loaded.nodes
    assert loaded.nodes[fp]["total_passes"] == 1


def test_quality_score_with_longevity():
    node = {
        "type": "vless",
        "server": "example.com",
        "server_port": 443,
        "tls": {"enabled": True, "reality": {"enabled": True}, "server_name": "apple.com"},
    }
    score_no_bonus = quality_score(node, latency_ms=200.0, longevity_bonus=0.0)
    score_with_bonus = quality_score(node, latency_ms=200.0, longevity_bonus=25.0)
    assert score_with_bonus == score_no_bonus + 25.0
