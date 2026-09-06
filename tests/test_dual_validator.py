"""Unit tests for DualValidator (Sing-box and Mihomo)."""

from unittest.mock import patch

from core.dual_validator import DualValidator, detect_physical_interface


def test_detect_physical_interface():
    iface = detect_physical_interface()
    assert isinstance(iface, str)
    assert len(iface) > 0
    assert not iface.startswith("utun")


def test_dual_validator_mock():
    validator = DualValidator(
        sing_box_bin="/bin/true",
        mihomo_bin="/bin/true",
        interface="en0",
    )
    assert validator.interface == "en0"

    fake_node = {
        "tag": "test-node",
        "type": "ss",
        "server": "1.2.3.4",
        "server_port": 8388,
        "method": "aes-128-gcm",
        "password": "pass",
    }

    with (
        patch.object(validator, "test_with_singbox", return_value=(True, 120.5, "OK")),
        patch.object(validator, "test_with_mihomo", return_value=(True, 130.0, "OK")),
    ):
        res = validator.test_node_dual(fake_node)
        assert res["both_ok"] is True
        assert res["singbox"]["ok"] is True
        assert res["mihomo"]["ok"] is True
        assert res["singbox"]["latency_ms"] == 120.5
