"""Property-based / hypothesis tests — mainstream quality technique."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from hypothesis import given
from hypothesis import strategies as st

from core.converters.clash import to_clash_proxy
from core.deduplicator import ensure_unique_tags


@given(st.lists(st.text(min_size=1, max_size=10), min_size=1, max_size=20))
def test_ensure_unique_tags_never_duplicates(tags):
    nodes = [{"tag": t} for t in tags]
    ensure_unique_tags(nodes)
    result_tags = [n["tag"] for n in nodes]
    assert len(result_tags) == len(set(result_tags)), "tags must be unique after deduplication"


@given(st.text(min_size=1, max_size=20), st.integers(min_value=1, max_value=65535))
def test_clash_proxy_vmess_roundtrip(server, port):
    node = {
        "type": "vmess",
        "tag": "hypo",
        "server": server,
        "server_port": port,
        "uuid": "u",
        "security": "auto",
    }
    # should not crash on arbitrary strings
    proxy = to_clash_proxy(node)
    assert proxy is not None
    assert proxy["server"] == server
    assert proxy["port"] == port


def test_deduplicator_idempotent():
    nodes = [{"tag": "A"}, {"tag": "A"}, {"tag": "A #2"}]
    ensure_unique_tags(nodes)
    snapshot = [n["tag"] for n in nodes]
    ensure_unique_tags(nodes)
    assert [n["tag"] for n in nodes] == snapshot
