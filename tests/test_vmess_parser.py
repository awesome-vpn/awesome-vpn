import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.parsers.vmess import parse


def test_vmess_uri_allow_insecure_zero_disables_insecure():
    uri = "vmess" + "://" + "auto:abc@1.2.3.4:443?tls=tls&allowInsecure=0&remarks=test-node"
    node = parse(
        uri
    )
    assert node["tls"]["insecure"] is False


def test_vmess_uri_allow_insecure_absent_keeps_insecure_true():
    uri = "vmess" + "://" + "auto:abc@1.2.3.4:443?tls=tls&remarks=test-node"
    node = parse(
        uri
    )
    assert node["tls"]["insecure"] is True
