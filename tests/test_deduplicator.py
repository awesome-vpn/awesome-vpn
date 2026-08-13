from core.deduplicator import ensure_unique_tags


def test_ensure_unique_tags_suffixes_duplicate_names():
    nodes = [
        {"tag": "美国/United States"},
        {"tag": "美国/United States"},
        {"tag": "美国/United States"},
    ]

    renamed = ensure_unique_tags(nodes)

    assert renamed == 2
    assert [node["tag"] for node in nodes] == [
        "美国/United States",
        "美国/United States #2",
        "美国/United States #3",
    ]


def test_ensure_unique_tags_reserves_existing_suffixes():
    nodes = [
        {"tag": "US"},
        {"tag": "US"},
        {"tag": "US #2"},
    ]

    ensure_unique_tags(nodes)

    assert [node["tag"] for node in nodes] == ["US", "US #3", "US #2"]


def test_ensure_unique_tags_is_idempotent_and_ignores_empty_tags():
    nodes = [
        {"tag": "US"},
        {"tag": "US #2"},
        {"tag": ""},
        {},
    ]

    assert ensure_unique_tags(nodes) == 0
    assert ensure_unique_tags(nodes) == 0
    assert nodes == [
        {"tag": "US"},
        {"tag": "US #2"},
        {"tag": ""},
        {},
    ]
