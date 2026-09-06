"""Unit tests for Harvesters and Channel Ledger."""

import json
import os
import tempfile
from unittest.mock import MagicMock, patch

from core.harvesters.channel_ledger import ChannelLedger
from core.harvesters.github_radar import GitHubRadarHarvester
from core.harvesters.telegram import TelegramHarvester


def test_channel_ledger_lifecycle():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        ledger_path = f.name

    try:
        ledger = ChannelLedger(ledger_path)
        ledger.add_channel("test_channel", status="active")
        assert "test_channel" in ledger.channels

        # Candidate discovery
        added = ledger.add_candidate("new_cand", discovered_from="test_channel")
        assert added is True
        assert ledger.channels["new_cand"]["status"] == "candidate"

        # Duplicate candidate ignored
        assert ledger.add_candidate("new_cand", discovered_from="other") is False

        # Empty yield increments failure
        ledger.record_result("new_cand", node_count=0)
        assert ledger.channels["new_cand"]["consecutive_failures"] == 1

        # 3 failures freezes channel
        ledger.record_result("new_cand", node_count=0)
        ledger.record_result("new_cand", node_count=0)
        assert ledger.channels["new_cand"]["status"] == "frozen"

        # Frozen channel excluded from probe list
        probe_list = ledger.get_probe_list()
        assert "new_cand" not in probe_list
        assert "test_channel" in probe_list

        # Yield promotes candidate
        ledger.add_candidate("yield_ch", discovered_from="test_channel")
        ledger.record_result("yield_ch", node_count=5)
        assert ledger.channels["yield_ch"]["status"] == "active"
        assert ledger.channels["yield_ch"]["total_nodes_yielded"] == 5

        # Persistence test
        ledger.save()
        ledger_reloaded = ChannelLedger(ledger_path)
        assert "yield_ch" in ledger_reloaded.channels
        assert ledger_reloaded.channels["yield_ch"]["total_nodes_yielded"] == 5

    finally:
        if os.path.exists(ledger_path):
            os.remove(ledger_path)


def test_telegram_harvester_extraction():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        ledger_path = f.name

    try:
        ledger = ChannelLedger(ledger_path)
        harvester = TelegramHarvester(ledger=ledger)

        fake_html = """
        <div class="tgme_widget_message_text">
            Check out @friend_channel and vmess://eyJ2IjoiMiIsInBzIjoidGVzdCJ9
        </div>
        """
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = fake_html

        with patch.object(harvester.spider.session, "get", return_value=mock_resp):
            name, links, discovered = harvester.fetch_channel("seed_ch")
            assert name == "seed_ch"
            assert any(link.startswith("vmess://") for link in links)
            assert "friend_channel" in discovered
    finally:
        if os.path.exists(ledger_path):
            os.remove(ledger_path)


def test_github_radar_harvester():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(
            {
                "repositories": [
                    {
                        "repo": "demo/repo",
                        "branch": "main",
                        "paths": ["sub.txt"],
                        "enabled": True,
                    }
                ]
            },
            f,
        )
        radar_path = f.name

    try:
        harvester = GitHubRadarHarvester(radar_config_path=radar_path)
        with patch.object(harvester.spider, "fetch_url", return_value="ss://abc@1.2.3.4:443#demo"):
            result = harvester.harvest()
            assert len(result.links) == 1
            assert result.links[0].startswith("ss://")
            assert result.source_map[result.links[0]] == "GH:demo/repo"
    finally:
        if os.path.exists(radar_path):
            os.remove(radar_path)
