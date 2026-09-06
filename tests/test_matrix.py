"""Unit tests for MatrixExporter and TelemetryReporter."""

import os
import tempfile

from core.matrix.exporter import MatrixExporter
from core.matrix.telemetry import TelemetryReporter


def test_matrix_exporter_and_telemetry():
    with tempfile.TemporaryDirectory() as tmpdir:
        exporter = MatrixExporter(output_dir=tmpdir)
        reporter = TelemetryReporter(output_dir=tmpdir)

        test_nodes = [
            {
                "tag": "🇯🇵 Japan-01",
                "server": "1.2.3.4",
                "server_port": 443,
                "type": "hysteria2",
                "password": "pass",
            },
            {
                "tag": "🇸🇬 Singapore-01",
                "server": "5.6.7.8",
                "server_port": 8443,
                "type": "vless",
                "uuid": "uuid1",
                "tls": {"reality": True},
            },
        ]
        source_links = {id(n): f"{n['type']}://test#{n['tag']}" for n in test_nodes}
        raw_links = ["ss://test1", "vmess://test2"]

        # Export Matrix
        exported = exporter.export_all(test_nodes, source_links, raw_links)
        assert os.path.exists(exported["sing-box"])
        assert os.path.exists(exported["clash"])
        assert os.path.exists(exported["all"])
        assert os.path.exists(exported["raw"])
        assert "hysteria2_clash" in exported
        assert "reality_singbox" in exported

        # Telemetry
        rep = reporter.generate_report(
            test_nodes, total_raw_count=100, passed_validation_count=2, latencies=[120.5, 180.0]
        )
        assert rep["curated_nodes_count"] == 2
        assert rep["average_latency_ms"] == 150.2
        assert os.path.exists(os.path.join(tmpdir, "status.svg"))
        assert os.path.exists(os.path.join(tmpdir, "telemetry.json"))
