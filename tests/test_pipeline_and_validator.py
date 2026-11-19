"""Unit tests for NodePipeline, Validator, BinaryManager, and StaticFeedHarvester."""

import io
import os
import socket
import struct
import tarfile
from unittest.mock import MagicMock, patch

from core.binary_manager import BinaryManager
from core.harvesters.base import HarvestResult
from core.harvesters.static_feed import (
    StaticFeedHarvester,
    apply_source_filters,
    parse_source_params,
    resolve_date_url,
)
from core.pipeline import NodePipeline, format_source_label
from core.validator import Validator, _get_unique_port, quick_tcp_prescreen


def test_format_source_label_variants():
    assert format_source_label("") == "Unknown"
    assert format_source_label("https://t.me/my_channel_name") == "TG:my_channel_name"
    assert format_source_label("https://t.me/s/my_channel_name") == "TG"
    assert format_source_label("@abc_chan") == "TG:abc_chan"
    assert (
        format_source_label("https://raw.githubusercontent.com/owner/repo/main/sub.txt")
        == "GH:owner/repo"
    )
    assert format_source_label("https://www.sub.example.com/feed") == "sub.example.com"


def test_static_feed_helpers_and_sources_list(tmp_path):
    opts = parse_source_params("max=5&ignore=ss,vmess")
    assert opts == {"max_nodes": 5, "ignore_protocols": ["ss", "vmess"]}
    assert parse_source_params("") == {}

    links = [f"vless://u@1.1.1.{i}:443#n{i}" for i in range(10)] + ["ss://a@1.1.1.1:80#s"]
    filtered = apply_source_filters(links, opts)
    assert len(filtered) == 5
    assert all(lk.startswith("vless://") for lk in filtered)
    assert apply_source_filters([], opts) == []

    resolved = resolve_date_url("https://example.com/%Y.txt")
    assert "%Y" not in resolved

    sources_list = tmp_path / "sources.list"
    sources_list.write_text(
        "# comment\n"
        "! https://blocked.example/a\n"
        "+date https://feed.example/%Y/sub.txt#max=3\n"
        "* https://list.example/nested.txt\n"
        "https://plain.example/sub.txt\n"
        "EOF\n"
        "https://after-eof.example/sub.txt\n",
        encoding="utf-8",
    )

    harvester = StaticFeedHarvester(sources_list_path=str(sources_list))
    with patch.object(
        harvester.spider, "fetch_url", return_value="https://child.example/node.txt\n"
    ):
        entries = harvester._load_sources_list()
    urls = [u for u, _ in entries]
    assert "https://blocked.example/a" not in urls
    assert "https://after-eof.example/sub.txt" not in urls
    assert "https://child.example/node.txt" in urls
    assert "https://plain.example/sub.txt" in urls


def test_pipeline_end_to_end_mocked(tmp_path):
    base_dir = tmp_path / "repo"
    out_dir = tmp_path / "out"
    (base_dir / "config").mkdir(parents=True)
    (base_dir / "bin").mkdir(parents=True)

    pipeline = NodePipeline(
        base_dir=str(base_dir),
        output_dir=str(out_dir),
        validate=True,
        local_mode=False,
        workers=2,
        validate_workers=2,
        max_nodes=5,
    )

    sample_links = [
        "vless://00000000-0000-0000-0000-000000000001@1.2.3.4:443?security=reality&pbk=pk&sni=apple.com#Node1",
        "hy2://pw@5.6.7.8:443?sni=hy2.example#Node2",
    ]
    source_map = {sample_links[0]: "https://t.me/s/demo", sample_links[1]: "GH:demo/repo"}

    with (
        patch(
            "core.pipeline.TelegramHarvester.harvest",
            return_value=HarvestResult(
                links=[sample_links[0]], source_map={sample_links[0]: source_map[sample_links[0]]}
            ),
        ),
        patch(
            "core.pipeline.GitHubRadarHarvester.harvest",
            return_value=HarvestResult(
                links=[sample_links[1]], source_map={sample_links[1]: source_map[sample_links[1]]}
            ),
        ),
        patch(
            "core.pipeline.StaticFeedHarvester.harvest",
            return_value=HarvestResult(links=[], source_map={}),
        ),
        patch("core.pipeline.BinaryManager.get_singbox_path", return_value="/usr/bin/sing-box"),
        patch(
            "core.pipeline.Validator.validate_nodes_parallel",
            side_effect=lambda nodes, timeout=5, max_workers=30: [
                dict(n, _latency_ms=120.0) for n in nodes
            ],
        ),
        patch("core.pipeline.GeoUtils.format_node_name", return_value="United States/San Jose"),
        patch("core.pipeline.PrescreenFunnel.filter", side_effect=lambda x: x),
    ):
        result = pipeline.run()

    assert result["total_raw"] == 2
    assert result["curated_count"] == 2
    assert os.path.exists(result["exported_files"]["sing-box"])
    assert os.path.exists(result["exported_files"]["clash"])
    assert os.path.exists(result["exported_files"]["all"])


def test_validator_methods_and_quick_prescreen(tmp_path):
    port = _get_unique_port()
    assert 1024 <= port <= 65535

    with (
        patch("core.validator.Validator._get_original_ip", return_value="1.2.3.4"),
        patch("core.validator.Validator._find_sing_box", return_value=None),
    ):
        val = Validator(sing_box_path="/nonexistent/sing-box", local_mode=False)

    assert val.validate_nodes_parallel([{"type": "vless"}]) == [{"type": "vless"}]

    # Exercise _get_original_ip and SOCKS5 TCP/UDP DNS helpers with mocked sockets/requests
    with patch("core.validator.requests.Session") as mock_sess_cls:
        mock_sess_cls.return_value.get.return_value = MagicMock(status_code=200, text="9.9.9.9\n")
        assert val._get_original_ip() == "9.9.9.9"

    mock_tcp_sock = MagicMock()
    mock_tcp_sock.recv.side_effect = [
        b"\x05\x00",
        b"\x05\x00\x00\x01\x7f\x00\x00\x01\x14\xe9",
    ]
    mock_udp_sock = MagicMock()
    mock_udp_sock.recvfrom.return_value = (b"dns-reply", ("127.0.0.1", 5353))
    with patch("core.validator.socket.socket", side_effect=[mock_tcp_sock, mock_udp_sock]):
        assert val.check_udp_dns_via_socks5(1080, timeout=1) is True

    query = val._build_dns_query("www.google.com")
    assert b"google" in query
    dns_resp = (
        query[:2]
        + struct.pack(">HHHHH", 0x8180, 1, 1, 0, 0)
        + query[12:]
        + b"\xc0\x0c"
        + struct.pack(">HHIH", 1, 1, 60, 4)
        + socket.inet_aton("8.8.8.8")
    )
    assert val._parse_dns_response(dns_resp) == "8.8.8.8"
    assert val._parse_dns_response(b"short") is None

    mock_dns_sock = MagicMock()
    mock_dns_sock.recv.side_effect = [
        b"\x05\x00",
        b"\x05\x00\x00\x01\x00\x00\x00\x00\x00\x00",
        struct.pack(">H", len(dns_resp)),
        dns_resp,
    ]
    with patch("socket.socket", return_value=mock_dns_sock):
        assert val.check_dns_via_proxy(1080, "www.google.com", timeout=1) is True

    # Test real loopback TCP connection + wait_for_socks5_ready
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.bind(("127.0.0.1", 0))
        srv.listen(8)
        srv_port = srv.getsockname()[1]
        assert val.tcp_ping("127.0.0.1", srv_port, timeout=1) is True
        conn, _ = srv.accept()
        conn.close()
        assert val._wait_for_socks5_ready(srv_port, timeout=1) is True
        conn, _ = srv.accept()
        conn.close()

        prescreened = quick_tcp_prescreen(
            [
                {"server": "127.0.0.1", "port": srv_port, "type": "vless"},
                {"server": "1.2.3.4", "port": 443, "type": "hysteria2"},
                {"server": "", "port": 0, "type": "vmess"},
            ],
            max_workers=2,
            timeout=1,
        )
        conn, _ = srv.accept()
        conn.close()
        assert len(prescreened) == 2

    # Mocked sing-box subprocess validation success
    fake_bin = tmp_path / "sing-box"
    fake_bin.write_text("#!/bin/sh\n")
    with patch("core.validator.Validator._get_original_ip", return_value="1.2.3.4"):
        val2 = Validator(sing_box_path=str(fake_bin), local_mode=False)

    mock_proc = MagicMock()
    mock_proc.poll.return_value = None
    mock_resp = MagicMock(status_code=204)
    mock_session = MagicMock()
    mock_session.get.return_value = mock_resp

    with (
        patch.object(val2, "tcp_ping", return_value=True),
        patch("core.validator.subprocess.Popen", return_value=mock_proc),
        patch.object(val2, "_wait_for_socks5_ready", return_value=True),
        patch("core.validator.requests.Session", return_value=mock_session),
    ):
        ok, lat = val2.validate_node_final(
            {"type": "vless", "server": "1.2.3.4", "server_port": 443}, timeout=2
        )
    assert ok is True
    assert lat >= 0.0


def test_binary_manager_paths_and_extraction(tmp_path):
    bm = BinaryManager(str(tmp_path))
    assert "darwin-arm64" in bm._get_download_url("1.13.3", "darwin", "arm64")
    assert "linux-amd64" in bm._get_download_url("1.13.3", "linux", "amd64")
    assert bm._get_download_url("1.13.3", "windows", "amd64") is None

    # Create tar.gz fixture containing nested sing-box binary
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(parents=True)
    tar_path = bin_dir / "sing-box-linux-amd64.tar.gz"
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        payload = b"#!/bin/sh\necho sing-box\n"
        info = tarfile.TarInfo("sing-box-1.13.3-linux-amd64/sing-box")
        info.size = len(payload)
        tar.addfile(info, io.BytesIO(payload))
    tar_bytes = buf.getvalue()

    mock_dl = MagicMock(status_code=200, headers={"content-length": str(len(tar_bytes))})
    mock_dl.iter_content.return_value = [tar_bytes]
    mock_ok = MagicMock(status_code=200)

    target = bin_dir / "sing-box-linux-amd64"
    with patch("core.binary_manager.requests.get", side_effect=[mock_ok, mock_dl]):
        assert bm._download_with_retry(
            "https://example.com/sb.tar.gz", str(target), "sing-box-linux-amd64", max_retries=1
        )
    assert target.exists()
    assert not tar_path.exists()

    with (
        patch("core.binary_manager.platform.system", return_value="Linux"),
        patch("core.binary_manager.platform.machine", return_value="x86_64"),
    ):
        found = bm.get_singbox_path()
    assert found == str(target)


def test_geo_utils_ipinfo_and_mmdb_fallback(tmp_path):
    from core.geo_utils import GeoUtils

    geo = GeoUtils(str(tmp_path / "missing.mmdb"))
    assert geo._resolve_to_ip("::1") == "::1"
    mock_resp = MagicMock(status_code=200)
    mock_resp.json.return_value = {"country": "JP", "city": "Tokyo"}
    with patch.object(geo._session, "get", return_value=mock_resp):
        assert geo.format_node_name("8.8.8.8") == "Japan/Tokyo"
    geo.close()


def test_telegram_harvester_harvest_and_main_cli(tmp_path, monkeypatch):
    import sys

    import main as cli_main
    from core.harvesters.channel_ledger import ChannelLedger
    from core.harvesters.telegram import TelegramHarvester

    ledger = ChannelLedger(str(tmp_path / "channels.json"))
    harvester = TelegramHarvester(ledger=ledger)
    with patch.object(
        harvester,
        "fetch_channel",
        return_value=("seed_ch", ["vless://u@1.1.1.1:443#t"], ["discovered_ch"]),
    ):
        res = harvester.harvest(seed_channels=["seed_ch"])
    assert res.links == ["vless://u@1.1.1.1:443#t"]
    assert "discovered_ch" in res.discovered_sources

    out_dir = tmp_path / "cli_out"
    nodes = [{"type": "vless", "tag": "t1", "server": "1.1.1.1", "server_port": 443, "uuid": "u"}]
    assert os.path.exists(cli_main.save_singbox(str(out_dir), nodes))
    assert os.path.exists(cli_main.save_clash(str(out_dir), nodes))
    assert os.path.exists(cli_main.save_all(str(out_dir), nodes, {}))

    monkeypatch.setenv("MAX_NODES", "10")
    monkeypatch.setattr(sys, "argv", ["main.py", "--local", "--output", str(out_dir)])
    with patch(
        "main.NodePipeline.run",
        return_value={"total_raw": 1, "curated_count": 1, "exported_files": {}},
    ):
        cli_main.main()


def test_dual_validator_engines_mocked(tmp_path):
    from core.dual_validator import (
        DualValidator,
        detect_physical_interface,
        get_free_port,
        release_port,
    )

    p = get_free_port()
    release_port(p)
    with patch(
        "core.dual_validator.subprocess.run",
        return_value=MagicMock(stdout="   interface: en0\n"),
    ):
        assert detect_physical_interface() == "en0"

    sb = tmp_path / "sing-box"
    mi = tmp_path / "mihomo"
    sb.write_text("#!/bin/sh\n")
    mi.write_text("#!/bin/sh\n")

    dv = DualValidator(sing_box_bin=str(sb), mihomo_bin=str(mi), interface="en0", timeout=2.0)
    mock_proc = MagicMock()
    mock_proc.poll.return_value = None
    mock_sess = MagicMock()
    mock_sess.get.return_value = MagicMock(status_code=204)

    node = {"type": "vless", "tag": "n1", "server": "1.1.1.1", "server_port": 443, "uuid": "u1"}
    with (
        patch("core.dual_validator.subprocess.Popen", return_value=mock_proc),
        patch("core.dual_validator.wait_for_port", return_value=True),
        patch("core.dual_validator.requests.Session", return_value=mock_sess),
    ):
        ok_sb, _, msg_sb = dv.test_with_singbox(node)
        ok_mi, _, msg_mi = dv.test_with_mihomo(node)

    assert ok_sb and msg_sb == "OK"
    assert ok_mi and msg_mi == "OK"
