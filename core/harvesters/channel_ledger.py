"""Channel Ledger for Telegram topology state and reputation tracking.

Features self-healing backoff revival, yield-weighted prioritization,
and automated garbage collection of permanently dead channels.
"""

import json
import logging
import os
from datetime import UTC, datetime

logger = logging.getLogger(__name__)


def parse_iso_datetime(iso_str: str | None) -> datetime | None:
    """Parse ISO8601 string into UTC datetime object."""
    if not iso_str:
        return None
    try:
        # Handle 'Z' or offset
        clean_str = iso_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(clean_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return dt
    except Exception:
        return None


class ChannelLedger:
    """
    Maintains reputations, failure counts, and discovery lineage for Telegram channels.
    Prevents crawler traps, implements exponential backoff revival, and prunes dead sources.
    """

    MAX_CONSECUTIVE_FAILURES = 3
    REVIVAL_COOLDOWN_SECONDS = 7 * 86400  # 7 days before probing frozen channels again
    GC_RETENTION_SECONDS = 30 * 86400  # 30 days before purging zero-yield dead channels
    MAX_REVIVALS_PER_RUN = 5

    def __init__(self, ledger_path: str):
        self.ledger_path = ledger_path
        self.channels: dict[str, dict] = {}
        self.load()

    def load(self) -> None:
        """Load channel ledger from disk if present."""
        if not os.path.exists(self.ledger_path):
            self.channels = {}
            return
        try:
            with open(self.ledger_path, encoding="utf-8") as f:
                data = json.load(f)
                self.channels = data.get("channels", {})
        except Exception as e:
            logger.warning(f"Failed to load Channel Ledger from {self.ledger_path}: {e}")
            self.channels = {}

    def save(self) -> None:
        """Persist channel ledger back to disk in deterministic sorted format."""
        try:
            os.makedirs(os.path.dirname(os.path.abspath(self.ledger_path)), exist_ok=True)
            with open(self.ledger_path, "w", encoding="utf-8") as f:
                json.dump(
                    {"channels": self.channels}, f, indent=2, ensure_ascii=False, sort_keys=True
                )
            logger.debug(
                f"Saved Channel Ledger to {self.ledger_path} ({len(self.channels)} channels)"
            )
        except Exception as e:
            logger.error(f"Failed to save Channel Ledger to {self.ledger_path}: {e}")

    def add_channel(
        self, channel: str, status: str = "active", discovered_from: str = "seed"
    ) -> None:
        """Register a new channel or ensure an existing one is updated."""
        name = channel.lstrip("@").strip()
        if not name:
            return
        if name not in self.channels:
            now_iso = datetime.now(UTC).isoformat()
            self.channels[name] = {
                "status": status,  # "active", "candidate", "frozen"
                "consecutive_failures": 0,
                "total_nodes_yielded": 0,
                "first_seen_at": now_iso,
                "last_seen_at": now_iso,
                "discovered_from": discovered_from,
            }
        else:
            self.channels[name]["last_seen_at"] = datetime.now(UTC).isoformat()
            if self.channels[name].get("status") == "frozen" and status == "active":
                self.channels[name]["status"] = "active"
                self.channels[name]["consecutive_failures"] = 0

    def add_candidate(self, channel: str, discovered_from: str) -> bool:
        """
        Record a newly discovered channel from message topology.
        Returns True if newly added as a candidate, False if already known.
        """
        name = channel.lstrip("@").strip()
        if not name or len(name) < 4 or len(name) > 35:
            return False
        # Filter out bots and common false-positive names from TG previews
        ignored_names = {
            "telegram",
            "durov",
            "joinchat",
            "addstickers",
            "share",
            "socks5",
            "proxy",
        }
        if name.lower() in ignored_names or name.lower().endswith("bot"):
            return False

        if name in self.channels:
            return False
        self.add_channel(name, status="candidate", discovered_from=discovered_from)
        logger.info(f"Discovered new candidate channel: @{name} (from @{discovered_from})")
        return True

    def record_result(self, channel: str, node_count: int) -> None:
        """
        Record harvesting outcome for a channel.
        Promotes or revives channels upon yield, or freezes upon repeated consecutive failures.
        """
        name = channel.lstrip("@").strip()
        if name not in self.channels:
            self.add_channel(name, status="active")

        entry = self.channels[name]
        entry["last_probed_at"] = datetime.now(UTC).isoformat()

        if node_count > 0:
            entry["consecutive_failures"] = 0
            entry["total_nodes_yielded"] = entry.get("total_nodes_yielded", 0) + node_count
            entry["last_success_at"] = datetime.now(UTC).isoformat()
            prev_status = entry.get("status")
            if prev_status in ("candidate", "frozen"):
                entry["status"] = "active"
                logger.info(
                    f"Channel @{name} transitioned from {prev_status} to active (yielded {node_count} nodes)"
                )
        else:
            entry["consecutive_failures"] = entry.get("consecutive_failures", 0) + 1
            if entry["consecutive_failures"] >= self.MAX_CONSECUTIVE_FAILURES:
                if entry.get("status") != "frozen" and entry.get("discovered_from") != "seed":
                    entry["status"] = "frozen"
                    logger.warning(
                        f"Channel @{name} dormant (frozen) after {entry['consecutive_failures']} consecutive empty runs"
                    )

    def get_probe_list(
        self,
        max_candidates: int = 15,
        max_revivals: int | None = None,
        seed_channels: list[str] | None = None,
    ) -> list[str]:
        """
        Return prioritized channels to harvest in this run:
        1. All active seed channels
        2. Active channels sorted by lifetime yield (yield-weighted scheduling)
        3. Up to `max_candidates` new candidates
        4. Up to `max_revivals` dormant channels whose 7-day cooldown expired
        """
        if seed_channels:
            for ch in seed_channels:
                self.add_channel(ch, status="active", discovered_from="seed")

        if max_revivals is None:
            max_revivals = self.MAX_REVIVALS_PER_RUN

        now = datetime.now(UTC)
        active_channels: list[tuple[str, int]] = []
        candidates: list[str] = []
        revivals: list[str] = []

        for name, data in self.channels.items():
            status = data.get("status", "active")
            if status == "active":
                yield_count = data.get("total_nodes_yielded", 0)
                active_channels.append((name, yield_count))
            elif status == "candidate":
                candidates.append(name)
            elif status == "frozen":
                # Check for backoff revival
                last_probed = parse_iso_datetime(data.get("last_probed_at"))
                if last_probed:
                    elapsed = (now - last_probed).total_seconds()
                    if elapsed >= self.REVIVAL_COOLDOWN_SECONDS:
                        revivals.append(name)
                else:
                    revivals.append(name)

        # Sort active channels by productivity
        active_channels.sort(key=lambda x: x[1], reverse=True)
        probe_list = [name for name, _ in active_channels]

        # Append candidates up to quota
        probe_list.extend(candidates[:max_candidates])

        # Append revival channels up to quota
        if revivals and max_revivals > 0:
            picked_revivals = revivals[:max_revivals]
            logger.info(
                f"Selecting {len(picked_revivals)} dormant channel(s) for scheduled backoff revival: {picked_revivals}"
            )
            probe_list.extend(picked_revivals)

        return probe_list

    def garbage_collect(self) -> list[str]:
        """
        Purge channels from ledger that:
        - Are not seeds
        - Are currently frozen
        - Have lifetime yielded nodes == 0
        - Were first seen > GC_RETENTION_SECONDS (30 days) ago
        """
        now = datetime.now(UTC)
        to_purge: list[str] = []

        for name, data in self.channels.items():
            if data.get("discovered_from") == "seed":
                continue
            if data.get("status") != "frozen":
                continue
            if data.get("total_nodes_yielded", 0) > 0:
                continue

            first_seen = parse_iso_datetime(data.get("first_seen_at"))
            if first_seen and (now - first_seen).total_seconds() >= self.GC_RETENTION_SECONDS:
                to_purge.append(name)

        for name in to_purge:
            del self.channels[name]

        if to_purge:
            logger.info(
                f"Garbage collected {len(to_purge)} permanently dead channels from ledger: {to_purge}"
            )

        return to_purge
