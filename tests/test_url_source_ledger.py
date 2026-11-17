"""Unit tests for UrlSourceLedger and StaticFeedHarvester dynamic source tracking."""

import json
import os
import tempfile
from unittest.mock import patch

from core.harvesters.static_feed import (
    StaticFeedHarvester,
    parse_sources_entries,
    parse_sources_json_str,
)
from core.harvesters.url_source_ledger import UrlSourceLedger


def test_url_source_ledger_lifecycle():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        ledger_path = f.name

    try:
        ledger = UrlSourceLedger(ledger_path)
        ledger.add_source("https://example.com/a.txt", status="active")
        assert "https://example.com/a.txt" in ledger.sources

        # Candidate discovery
        added = ledger.add_candidate("https://example.com/new.txt", discovered_from="nested-list")
        assert added is True
        assert ledger.sources["https://example.com/new.txt"]["status"] == "candidate"

        # Duplicate candidate ignored
        assert ledger.add_candidate("https://example.com/new.txt", discovered_from="other") is False

        # Empty yield increments failure
        ledger.record_result("https://example.com/new.txt", node_count=0)
        assert ledger.sources["https://example.com/new.txt"]["consecutive_failures"] == 1

        # 3 failures freezes the source
        ledger.record_result("https://example.com/new.txt", node_count=0)
        ledger.record_result("https://example.com/new.txt", node_count=0)
        assert ledger.sources["https://example.com/new.txt"]["status"] == "frozen"

        # Frozen source excluded from probe list (cooldown not yet elapsed)
        probe_list = [url for url, _ in ledger.get_probe_list()]
        assert "https://example.com/new.txt" not in probe_list
        assert "https://example.com/a.txt" in probe_list

        # Yield promotes candidate
        ledger.add_candidate("https://example.com/yield.txt", discovered_from="a")
        ledger.record_result("https://example.com/yield.txt", node_count=5)
        assert ledger.sources["https://example.com/yield.txt"]["status"] == "active"
        assert ledger.sources["https://example.com/yield.txt"]["total_nodes_yielded"] == 5

        # Persistence test
        ledger.save()
        reloaded = UrlSourceLedger(ledger_path)
        assert "https://example.com/yield.txt" in reloaded.sources
        assert reloaded.sources["https://example.com/yield.txt"]["total_nodes_yielded"] == 5
    finally:
        if os.path.exists(ledger_path):
            os.remove(ledger_path)


def test_url_source_ledger_seed_urls_carry_options():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        ledger_path = f.name

    try:
        ledger = UrlSourceLedger(ledger_path)
        seed = [("https://example.com/sub.txt", {"max_nodes": 10})]
        probe = dict(ledger.get_probe_list(seed_urls=seed))
        assert probe["https://example.com/sub.txt"] == {"max_nodes": 10}
        # Seeds should never be garbage collected even if they never yield.
        ledger.record_result("https://example.com/sub.txt", node_count=0)
        ledger.record_result("https://example.com/sub.txt", node_count=0)
        ledger.record_result("https://example.com/sub.txt", node_count=0)
        purged = ledger.garbage_collect()
        assert "https://example.com/sub.txt" not in purged
    finally:
        if os.path.exists(ledger_path):
            os.remove(ledger_path)


def test_url_source_ledger_garbage_collect_only_purges_stale_frozen():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        ledger_path = f.name

    try:
        ledger = UrlSourceLedger(ledger_path)
        ledger.add_candidate("https://example.com/dead.txt", discovered_from="nested")
        entry = ledger.sources["https://example.com/dead.txt"]
        entry["status"] = "frozen"
        entry["total_nodes_yielded"] = 0
        entry["first_seen_at"] = "2000-01-01T00:00:00+00:00"

        purged = ledger.garbage_collect()
        assert purged == ["https://example.com/dead.txt"]
        assert "https://example.com/dead.txt" not in ledger.sources
    finally:
        if os.path.exists(ledger_path):
            os.remove(ledger_path)


def test_parse_sources_entries_respects_enabled_and_options():
    data = {
        "urls": [
            "https://example.com/plain.txt",
            {"url": "https://example.com/disabled.txt", "enabled": False},
            {
                "url": "https://example.com/opts.txt",
                "max_nodes": 5,
                "ignore_protocols": ["ss"],
            },
        ]
    }
    entries = parse_sources_entries(data)
    urls = [u for u, _ in entries]
    assert "https://example.com/plain.txt" in urls
    assert "https://example.com/disabled.txt" not in urls
    opts = dict(entries)["https://example.com/opts.txt"]
    assert opts == {"max_nodes": 5, "ignore_protocols": ["ss"]}


def test_parse_sources_json_str_seeds_from_secret():
    raw = json.dumps({"urls": ["https://example.com/seed.txt"]})
    entries = parse_sources_json_str(raw)
    assert entries == [("https://example.com/seed.txt", {})]
    assert parse_sources_json_str("") == []
    assert parse_sources_json_str("not json") == []


def test_static_feed_harvester_records_results_into_ledger():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        ledger_path = f.name

    try:
        ledger = UrlSourceLedger(ledger_path)
        harvester = StaticFeedHarvester(
            ledger=ledger,
            seed_entries=[
                ("https://example.com/good.txt", {}),
                ("https://example.com/bad.txt", {}),
            ],
        )

        def fake_fetch_urls_parallel(urls, max_workers=10):
            return {
                "https://example.com/good.txt": "ss://YWVzLTI1Ni1nY206dGVzdA==@1.2.3.4:443#node",
                "https://example.com/bad.txt": None,
            }

        with patch.object(
            harvester.spider, "fetch_urls_parallel", side_effect=fake_fetch_urls_parallel
        ):
            result = harvester.harvest()

        assert len(result.links) == 1
        assert ledger.sources["https://example.com/good.txt"]["total_nodes_yielded"] == 1
        assert ledger.sources["https://example.com/bad.txt"]["consecutive_failures"] == 1

        # Persisted to disk by the harvester itself.
        reloaded = UrlSourceLedger(ledger_path)
        assert reloaded.sources["https://example.com/good.txt"]["total_nodes_yielded"] == 1
    finally:
        if os.path.exists(ledger_path):
            os.remove(ledger_path)


def test_static_feed_harvester_without_ledger_is_non_persistent():
    harvester = StaticFeedHarvester(
        ledger=None, seed_entries=[("https://example.com/good.txt", {})]
    )

    def fake_fetch_urls_parallel(urls, max_workers=10):
        return {"https://example.com/good.txt": "ss://YWVzLTI1Ni1nY206dGVzdA==@1.2.3.4:443#node"}

    with patch.object(
        harvester.spider, "fetch_urls_parallel", side_effect=fake_fetch_urls_parallel
    ):
        result = harvester.harvest()

    assert len(result.links) == 1
