"""Node Longevity Ledger: tracks multi-day survival and assigns stability bonuses."""

import json
import logging
import os
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)


def parse_iso(iso_str: str | None) -> datetime | None:
    if not iso_str:
        return None
    try:
        clean = iso_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(clean)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return dt
    except Exception:
        return None


class NodeLedger:
    """
    Persistent registry of proxy servers across test runs.
    Calculates historical uptime streaks to award longevity bonuses to rock-solid nodes.
    """

    MAX_RETENTION_SECONDS = 14 * 86400  # 14 days retention for dead nodes

    def __init__(self, ledger_path: str):
        self.ledger_path = ledger_path
        self.nodes: dict[str, dict[str, Any]] = {}
        self.load()

    def load(self) -> None:
        if not os.path.exists(self.ledger_path):
            self.nodes = {}
            return
        try:
            with open(self.ledger_path, encoding="utf-8") as f:
                data = json.load(f)
                self.nodes = data.get("nodes", {})
        except Exception as e:
            logger.warning(f"Failed to load NodeLedger from {self.ledger_path}: {e}")
            self.nodes = {}

    def save(self) -> None:
        try:
            os.makedirs(os.path.dirname(os.path.abspath(self.ledger_path)), exist_ok=True)
            with open(self.ledger_path, "w", encoding="utf-8") as f:
                json.dump({"nodes": self.nodes}, f, indent=2, ensure_ascii=False)
            logger.debug(f"Saved NodeLedger with {len(self.nodes)} tracked servers.")
        except Exception as e:
            logger.error(f"Failed to save NodeLedger to {self.ledger_path}: {e}")

    @staticmethod
    def get_fingerprint(node: dict[str, Any]) -> str:
        """Deterministic identity for a server node."""
        ntype = str(node.get("type", "")).strip().lower()
        server = str(node.get("server", "")).strip().lower()
        port = str(node.get("server_port") or node.get("port", "")).strip()
        return f"{ntype}://{server}:{port}"

    def record_validation(
        self, node: dict[str, Any], is_valid: bool, latency_ms: float = 0.0
    ) -> None:
        """Record check result for a node."""
        fp = self.get_fingerprint(node)
        now_iso = datetime.now(UTC).isoformat()

        if fp not in self.nodes:
            self.nodes[fp] = {
                "first_seen_at": now_iso,
                "last_seen_at": now_iso,
                "consecutive_passes": 0,
                "total_checks": 0,
                "total_passes": 0,
                "avg_latency_ms": latency_ms if is_valid else 0.0,
            }

        entry = self.nodes[fp]
        entry["last_seen_at"] = now_iso
        entry["total_checks"] = entry.get("total_checks", 0) + 1

        if is_valid:
            entry["consecutive_passes"] = entry.get("consecutive_passes", 0) + 1
            entry["total_passes"] = entry.get("total_passes", 0) + 1
            entry["last_pass_at"] = now_iso
            # Rolling average latency
            prev_avg = entry.get("avg_latency_ms", 0.0)
            if prev_avg > 0 and latency_ms > 0:
                entry["avg_latency_ms"] = round((prev_avg + latency_ms) / 2.0, 1)
            else:
                entry["avg_latency_ms"] = round(latency_ms, 1)
        else:
            entry["consecutive_passes"] = 0

    def get_longevity_bonus(self, node: dict[str, Any]) -> float:
        """
        Calculate stability bonus:
        - 1 consecutive pass: +4
        - 2 consecutive passes: +8
        - 3 consecutive passes: +15
        - 5+ consecutive passes: +25 (proven multi-day rock-solid server)
        """
        fp = self.get_fingerprint(node)
        entry = self.nodes.get(fp)
        if not entry:
            return 0.0

        streak = entry.get("consecutive_passes", 0)
        if streak >= 5:
            bonus = 25.0
        elif streak >= 3:
            bonus = 15.0
        elif streak >= 2:
            bonus = 8.0
        elif streak >= 1:
            bonus = 4.0
        else:
            bonus = 0.0

        # Additional bonus for high historical pass rate (> 80% with >= 3 checks)
        total_checks = entry.get("total_checks", 0)
        total_passes = entry.get("total_passes", 0)
        if total_checks >= 3 and (total_passes / total_checks) >= 0.8:
            bonus += 5.0

        return bonus

    def garbage_collect(self) -> int:
        """Purge records not seen for over 14 days."""
        now = datetime.now(UTC)
        to_delete = []
        for fp, entry in self.nodes.items():
            last_seen = parse_iso(entry.get("last_seen_at"))
            if last_seen and (now - last_seen).total_seconds() > self.MAX_RETENTION_SECONDS:
                to_delete.append(fp)

        for fp in to_delete:
            del self.nodes[fp]

        if to_delete:
            logger.info(f"NodeLedger: Purged {len(to_delete)} expired stale server records.")
        return len(to_delete)
