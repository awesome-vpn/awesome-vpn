"""Lock standardized subscription structure: English groups, zero Chinese in configs."""

import json
import sys
import tempfile
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.geo_utils import GeoUtils  # noqa: F401, E402  (import order checked by ruff per-file)
from main import save_clash, save_singbox


def _fake_nodes():
    # Minimal valid outbounds; Geo naming not involved here
    return [
        {
            "tag": "node-1",
            "type": "vless",
            "server": "1.1.1.1",
            "server_port": 443,
            "uuid": "uuid-1",
            "tls": {"enabled": True, "server_name": "www.apple.com", "reality": {"enabled": True}},
        },
        {
            "tag": "node-2",
            "type": "shadowsocks",
            "server": "2.2.2.2",
            "server_port": 8388,
            "method": "aes-256-gcm",
            "password": "pass",
        },
        {
            "tag": "node-3",
            "type": "vmess",
            "server": "3.3.3.3",
            "server_port": 443,
            "uuid": "uuid-3",
            "security": "auto",
        },
    ]


def test_singbox_groups_are_english_and_standard():
    nodes = _fake_nodes()
    with tempfile.TemporaryDirectory() as tmp:
        save_singbox(tmp, nodes)
        data = json.loads((Path(tmp) / "sing-box.json").read_text())
        outbounds = data["outbounds"]
        tags = {n.get("tag") for n in outbounds}
        types = {n.get("type") for n in outbounds}
        # English groups only
        assert "PROXY" in tags
        assert "Auto" in tags
        assert "auto" not in tags and "proxy" not in tags
        # selector must be PROXY -> [Auto, direct]
        sel = next(n for n in outbounds if n.get("type") == "selector")
        assert sel["tag"] == "PROXY"
        assert sel["outbounds"] == ["Auto", "direct"]
        assert sel["default"] == "Auto"
        # urltest must be Auto and contain all real nodes
        ut = next(n for n in outbounds if n.get("type") == "urltest")
        assert ut["tag"] == "Auto"
        assert set(ut["outbounds"]) == {"node-1", "node-2", "node-3"}
        # ordinary nodes must NOT leak into selector
        assert not any(t.startswith("node-") for t in sel["outbounds"])
        # direct exists
        assert "direct" in tags
        assert "direct" in types
        # count = nodes + 3 groups
        assert len(outbounds) == len(nodes) + 3


def test_clash_groups_are_english_and_standard():
    nodes = _fake_nodes()
    with tempfile.TemporaryDirectory() as tmp:
        save_clash(tmp, nodes)
        data = yaml.safe_load((Path(tmp) / "clash.yaml").read_text())
        assert "proxies" in data
        groups = {g["name"]: g for g in data["proxy-groups"]}
        # English groups
        assert "PROXY" in groups
        assert "Auto" in groups
        assert "proxy" not in groups and "auto" not in groups
        # PROXY is select with only Auto+DIRECT
        assert groups["PROXY"]["type"] == "select"
        assert groups["PROXY"]["proxies"] == ["Auto", "DIRECT"]
        # Auto is url-test with all nodes
        assert groups["Auto"]["type"] == "url-test"
        assert set(groups["Auto"]["proxies"]) == {"node-1", "node-2", "node-3"}
        assert groups["Auto"]["url"] == "https://www.google.com/generate_204"
        # rules
        assert data["rules"][-1] == "MATCH,PROXY"
        # ordinary nodes must not appear in PROXY select alongside Auto
        assert not any(
            n.startswith("node-") for n in groups["PROXY"]["proxies"] if n not in ("Auto", "DIRECT")
        )


def test_output_configs_contain_no_chinese():
    nodes = _fake_nodes()
    # Geo naming produces English-only now; verify via direct GeoUtils call
    geo = GeoUtils("/nonexistent.mmdb")
    geo._cache["9.9.9.9"] = ("日本", "Japan", "东京", "Tokyo")
    assert geo.format_node_name("9.9.9.9") == "Japan/Tokyo"
    assert all(ord(c) < 128 or c in " []:.-_/" for c in geo.format_node_name("9.9.9.9"))
    geo.close()

    with tempfile.TemporaryDirectory() as tmp:
        save_singbox(tmp, nodes)
        save_clash(tmp, nodes)
        sing_text = (Path(tmp) / "sing-box.json").read_text()
        clash_text = (Path(tmp) / "clash.yaml").read_text()
        for txt in (sing_text, clash_text):
            # Config files should contain no CJK range
            assert not any("\u4e00" <= ch <= "\u9fff" for ch in txt), "config must be English-only"
