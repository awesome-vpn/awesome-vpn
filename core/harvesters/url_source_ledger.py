"""URL Source Ledger for static/parameterized feed URLs.

Turns the previously static, git-ignored `sources.json` secret into a
self-updating, git-tracked store: mirrors `ChannelLedger`'s active/candidate/
frozen lifecycle so unproductive URLs are automatically backed off and
eventually revived or garbage collected, instead of requiring a maintainer
to hand-edit a secret whenever a source goes stale.
"""

import json
import logging
import os
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)


def parse_iso_datetime(iso_str: str | None) -> datetime | None:
    """Parse ISO8601 string into UTC datetime object."""
    if not iso_str:
        return None
    try:
        clean_str = iso_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(clean_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return dt
    except Exception:
        return None


class UrlSourceLedger:
    """
    Maintains reputations, failure counts, and discovery lineage for static
    subscription/source URLs. Prevents dead URLs from being probed forever,
    implements exponential backoff revival, and prunes permanently dead
    sources - the same self-updating pattern already used for Telegram
    channels (`ChannelLedger`) and GitHub Radar repositories.
    """

    MAX_CONSECUTIVE_FAILURES = 3
    REVIVAL_COOLDOWN_SECONDS = 7 * 86400  # 7 days before probing frozen URLs again
    GC_RETENTION_SECONDS = 30 * 86400  # 30 days before purging zero-yield dead URLs
    MAX_REVIVALS_PER_RUN = 5

    def __init__(self, ledger_path: str):
        self.ledger_path = ledger_path
        self.sources: dict[str, dict[str, Any]] = {}
        self.load()

    def load(self) -> None:
        """Load URL source ledger from disk if present."""
        if not os.path.exists(self.ledger_path):
            self.sources = {}
            return
        try:
            with open(self.ledger_path, encoding="utf-8") as f:
                data = json.load(f)
                self.sources = data.get("sources", {})
        except Exception as e:
            logger.warning(f"Failed to load UrlSourceLedger from {self.ledger_path}: {e}")
            self.sources = {}

    def save(self) -> None:
        """Persist URL source ledger back to disk in deterministic sorted format."""
        try:
            os.makedirs(os.path.dirname(os.path.abspath(self.ledger_path)), exist_ok=True)
            with open(self.ledger_path, "w", encoding="utf-8") as f:
                json.dump(
                    {"sources": self.sources}, f, indent=2, ensure_ascii=False, sort_keys=True
                )
            logger.debug(f"Saved UrlSourceLedger to {self.ledger_path} ({len(self.sources)} URLs)")
        except Exception as e:
            logger.error(f"Failed to save UrlSourceLedger to {self.ledger_path}: {e}")

    def add_source(
        self,
        url: str,
        status: str = "active",
        discovered_from: str = "seed",
        options: dict[str, Any] | None = None,
    ) -> None:
        """Register a new URL source or ensure an existing one is updated."""
        url = url.strip()
        if not url:
            return
        if url not in self.sources:
            now_iso = datetime.now(UTC).isoformat()
            self.sources[url] = {
                "status": status,  # "active", "candidate", "frozen"
                "enabled": True,
                "consecutive_failures": 0,
                "total_nodes_yielded": 0,
                "first_seen_at": now_iso,
                "last_seen_at": now_iso,
                "discovered_from": discovered_from,
                "options": options or {},
            }
        else:
            entry = self.sources[url]
            entry["last_seen_at"] = datetime.now(UTC).isoformat()
            if options:
                entry["options"] = options
            if entry.get("status") == "frozen" and status == "active":
                entry["status"] = "active"
                entry["consecutive_failures"] = 0

    def add_candidate(
        self, url: str, discovered_from: str, options: dict[str, Any] | None = None
    ) -> bool:
        """
        Record a newly discovered URL (e.g. from a nested subscription list).
        Returns True if newly added as a candidate, False if already known.
        """
        url = url.strip()
        if not url or not url.startswith("http"):
            return False
        if url in self.sources:
            return False
        self.add_source(url, status="candidate", discovered_from=discovered_from, options=options)
        logger.info(f"Discovered new candidate URL source: {url} (from {discovered_from})")
        return True

    def record_result(self, url: str, node_count: int) -> None:
        """
        Record harvesting outcome for a URL.
        Promotes or revives sources upon yield, or freezes upon repeated
        consecutive failures.
        """
        url = url.strip()
        if not url:
            return
        if url not in self.sources:
            self.add_source(url, status="active")

        entry = self.sources[url]
        entry["last_probed_at"] = datetime.now(UTC).isoformat()

        if node_count > 0:
            entry["consecutive_failures"] = 0
            entry["total_nodes_yielded"] = entry.get("total_nodes_yielded", 0) + node_count
            entry["last_success_at"] = datetime.now(UTC).isoformat()
            prev_status = entry.get("status")
            if prev_status in ("candidate", "frozen"):
                entry["status"] = "active"
                logger.info(
                    f"URL source {url} transitioned from {prev_status} to active "
                    f"(yielded {node_count} nodes)"
                )
        else:
            entry["consecutive_failures"] = entry.get("consecutive_failures", 0) + 1
            if entry["consecutive_failures"] >= self.MAX_CONSECUTIVE_FAILURES:
                if entry.get("status") != "frozen" and entry.get("discovered_from") != "seed":
                    entry["status"] = "frozen"
                    logger.warning(
                        f"URL source {url} dormant (frozen) after "
                        f"{entry['consecutive_failures']} consecutive empty runs"
                    )

    def get_probe_list(
        self,
        max_candidates: int = 30,
        max_revivals: int | None = None,
        seed_urls: list[tuple[str, dict[str, Any]]] | None = None,
    ) -> list[tuple[str, dict[str, Any]]]:
        """
        Return prioritized (url, options) pairs to harvest in this run:
        1. All seed URLs (explicitly supplied this run, e.g. from secrets)
        2. Active URLs sorted by lifetime yield (yield-weighted scheduling)
        3. Up to `max_candidates` new candidates
        4. Up to `max_revivals` dormant URLs whose 7-day cooldown expired
        """
        if seed_urls:
            for url, options in seed_urls:
                self.add_source(url, status="active", discovered_from="seed", options=options)

        if max_revivals is None:
            max_revivals = self.MAX_REVIVALS_PER_RUN

        now = datetime.now(UTC)
        active_sources: list[tuple[str, int]] = []
        candidates: list[str] = []
        revivals: list[str] = []

        for url, data in self.sources.items():
            if data.get("enabled") is False:
                continue
            status = data.get("status", "active")
            if status == "active":
                yield_count = data.get("total_nodes_yielded", 0)
                active_sources.append((url, yield_count))
            elif status == "candidate":
                candidates.append(url)
            elif status == "frozen":
                last_probed = parse_iso_datetime(data.get("last_probed_at"))
                if last_probed:
                    elapsed = (now - last_probed).total_seconds()
                    if elapsed >= self.REVIVAL_COOLDOWN_SECONDS:
                        revivals.append(url)
                else:
                    revivals.append(url)

        active_sources.sort(key=lambda x: x[1], reverse=True)
        probe_list = [url for url, _ in active_sources]
        probe_list.extend(candidates[:max_candidates])

        if revivals and max_revivals > 0:
            picked_revivals = revivals[:max_revivals]
            logger.info(
                f"Selecting {len(picked_revivals)} dormant URL source(s) for scheduled "
                f"backoff revival: {picked_revivals}"
            )
            probe_list.extend(picked_revivals)

        return [(url, self.sources[url].get("options", {})) for url in probe_list]

    def garbage_collect(self) -> list[str]:
        """
        Purge URL sources from the ledger that:
        - Are not seeds
        - Are currently frozen
        - Have lifetime yielded nodes == 0
        - Were first seen > GC_RETENTION_SECONDS (30 days) ago
        """
        now = datetime.now(UTC)
        to_purge: list[str] = []

        for url, data in self.sources.items():
            if data.get("discovered_from") == "seed":
                continue
            if data.get("status") != "frozen":
                continue
            if data.get("total_nodes_yielded", 0) > 0:
                continue

            first_seen = parse_iso_datetime(data.get("first_seen_at"))
            if first_seen and (now - first_seen).total_seconds() >= self.GC_RETENTION_SECONDS:
                to_purge.append(url)

        for url in to_purge:
            del self.sources[url]

        if to_purge:
            logger.info(
                f"Garbage collected {len(to_purge)} permanently dead URL sources from ledger: "
                f"{to_purge}"
            )

        return to_purge
