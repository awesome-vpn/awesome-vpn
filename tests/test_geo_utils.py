"""Tests for GeoUtils — demonstrates mocking external I/O (DNS + HTTP)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import patch

from core.geo_utils import GeoUtils


def test_format_node_name_with_city(tmp_path):
    mmdb = tmp_path / "dummy.mmdb"
    mmdb.write_text("")
    geo = GeoUtils(str(mmdb))
    # Mock cache directly to avoid network/DNS
    geo._cache["1.2.3.4"] = ("美国", "United States", "洛杉矶", "Los Angeles")
    assert geo.format_node_name("1.2.3.4") == "美国/洛杉矶/United States/Los Angeles"
    geo.close()


def test_format_node_name_without_city(tmp_path):
    mmdb = tmp_path / "dummy.mmdb"
    mmdb.write_text("")
    geo = GeoUtils(str(mmdb))
    geo._cache["5.6.7.8"] = ("德国", "Germany", "", "")
    assert geo.format_node_name("5.6.7.8") == "德国/Germany"
    geo.close()


def test_get_geo_info_caches(tmp_path):
    mmdb = tmp_path / "dummy.mmdb"
    mmdb.write_text("")
    geo = GeoUtils(str(mmdb))
    with patch.object(
        geo, "_fetch_geo_info", return_value=("日本", "Japan", "东京", "Tokyo")
    ) as mock_fetch:
        first = geo.get_geo_info("9.9.9.9")
        second = geo.get_geo_info("9.9.9.9")
        assert first == ("日本", "Japan", "东京", "Tokyo")
        assert second == first
        mock_fetch.assert_called_once()  # second call hits cache
    geo.close()


def test_resolve_to_ip_direct():
    geo = GeoUtils("/nonexistent.mmdb")
    assert geo._resolve_to_ip("8.8.8.8") == "8.8.8.8"
    # invalid host returns None (no network)
    with patch("socket.gethostbyname", side_effect=OSError("fail")):
        assert geo._resolve_to_ip("bad.invalid.example") is None
    geo.close()
