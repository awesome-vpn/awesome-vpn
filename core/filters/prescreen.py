"""Tiered Prescreen Funnel to protect validator resources and prioritize modern protocols."""

import concurrent.futures
import logging
import socket
from typing import Any

from core.deduplicator import Deduplicator
from core.filters.honeypot import HoneypotFilter

logger = logging.getLogger(__name__)

# Protocol priority weight (higher score = more modern, anti-censorship resilient)
PROTOCOL_WEIGHTS = {
    "hysteria2": 100,
    "hy2": 100,
    "tuic": 90,
    "vless": 80,
    "trojan": 70,
    "ss": 50,
    "vmess": 40,
}

UDP_PROTOCOLS = {"hysteria2", "hy2", "tuic"}


def fast_tcp_ping(server: str, port: int, timeout: float = 2.0) -> bool:
    """Non-blocking TCP socket connect check to eliminate completely dead hosts."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            sock.connect((server, port))
            return True
    except Exception:
        return False


class PrescreenFunnel:
    """
    Tiered prescreen funnel:
    1. Honeypot & RFC private IP elimination
    2. Exact & redundant server deduplication
    3. Fast TCP non-handshake prescreen (UDP protocols bypass)
    4. Modern protocol weighted prioritization & quota truncation
    """

    def __init__(
        self,
        max_validation_candidates: int = 400,
        tcp_workers: int = 60,
        tcp_timeout: float = 2.0,
        local_mode: bool = False,
    ):
        self.max_validation_candidates = max_validation_candidates
        self.tcp_workers = tcp_workers
        self.tcp_timeout = tcp_timeout
        self.local_mode = local_mode
        self.deduplicator = Deduplicator()

    def filter(
        self,
        raw_nodes_with_meta: list[tuple[dict[str, Any], str, str]],
    ) -> list[tuple[dict[str, Any], str, str]]:
        """
        Process candidate nodes through the multi-stage funnel.
        Input: list of (node_dict, original_link, source_label).
        Output: Curated candidate list ready for sing-box validation.
        """
        total_input = len(raw_nodes_with_meta)
        logger.info(
            f"[PrescreenFunnel] Stage 1: Security & honeypot screening on {total_input} nodes..."
        )

        # Stage 1: Honeypot & Private IP Filter
        safe_nodes = []
        for node, link, source in raw_nodes_with_meta:
            if not HoneypotFilter.is_honeypot_or_invalid(node):
                safe_nodes.append((node, link, source))

        honeypot_dropped = total_input - len(safe_nodes)
        logger.info(
            f"  Dropped {honeypot_dropped} honeypot/invalid/private-IP nodes. Remaining: {len(safe_nodes)}"
        )

        # Stage 2: Deduplication
        logger.info(
            f"[PrescreenFunnel] Stage 2: Deduplicating across {len(safe_nodes)} safe nodes..."
        )
        deduped_nodes = []
        for node, link, source in safe_nodes:
            if self.deduplicator.is_duplicate(node) or self.deduplicator.is_redundant_server(node):
                continue
            deduped_nodes.append((node, link, source))

        dedup_dropped = len(safe_nodes) - len(deduped_nodes)
        logger.info(f"  Dropped {dedup_dropped} duplicates. Remaining: {len(deduped_nodes)}")

        # Stage 3: Fast TCP prescreen (skip if in local mode behind GFW)
        if self.local_mode:
            logger.info("  Skipping TCP prescreen in local mode (GFW environment).")
            passed_nodes = deduped_nodes
        else:
            logger.info(
                f"[PrescreenFunnel] Stage 3: Parallel TCP prescreen (workers={self.tcp_workers}, timeout={self.tcp_timeout}s)..."
            )
            passed_nodes = []
            tcp_candidates = []
            udp_candidates = []

            for item in deduped_nodes:
                node = item[0]
                ntype = str(node.get("type", "")).lower()
                if ntype in UDP_PROTOCOLS:
                    udp_candidates.append(item)
                else:
                    tcp_candidates.append(item)

            passed_nodes.extend(udp_candidates)

            def _check_tcp(entry):
                node = entry[0]
                server = node.get("server", "")
                port = int(node.get("server_port") or node.get("port", 0))
                return entry if fast_tcp_ping(server, port, timeout=self.tcp_timeout) else None

            with concurrent.futures.ThreadPoolExecutor(max_workers=self.tcp_workers) as executor:
                results = executor.map(_check_tcp, tcp_candidates)
                for res in results:
                    if res is not None:
                        passed_nodes.append(res)

            tcp_failed = len(tcp_candidates) - (len(passed_nodes) - len(udp_candidates))
            logger.info(
                f"  TCP prescreen done: {len(passed_nodes)}/{len(deduped_nodes)} alive "
                f"({tcp_failed} unreachable TCP endpoints dropped, {len(udp_candidates)} UDP preserved)"
            )

        # Stage 4: Source-Diversified Prioritization & Protocol Weighting
        def _get_protocol_weight(item):
            node = item[0]
            ntype = str(node.get("type", "")).lower()
            return PROTOCOL_WEIGHTS.get(ntype, 30)

        # Group by source to ensure balanced representation across all harvesters
        source_buckets: dict[str, list[tuple[dict[str, Any], str, str]]] = {}
        for item in passed_nodes:
            src = item[2]
            source_buckets.setdefault(src, []).append(item)

        # Sort each bucket by protocol weight descending
        for src, items in source_buckets.items():
            items.sort(key=_get_protocol_weight, reverse=True)

        # Fair round-robin interleaving across sources
        prioritized_nodes: list[tuple[dict[str, Any], str, str]] = []
        bucket_lists = list(source_buckets.values())
        max_depth = max(len(b) for b in bucket_lists) if bucket_lists else 0

        for depth in range(max_depth):
            for bucket in bucket_lists:
                if depth < len(bucket):
                    prioritized_nodes.append(bucket[depth])
                    if len(prioritized_nodes) >= self.max_validation_candidates:
                        break
            if len(prioritized_nodes) >= self.max_validation_candidates:
                break

        if len(passed_nodes) > self.max_validation_candidates:
            excess = len(passed_nodes) - len(prioritized_nodes)
            logger.info(
                f"[PrescreenFunnel] Stage 4: Prioritized Top-{len(prioritized_nodes)} candidates "
                f"via fair source interleaving across {len(source_buckets)} sources (dropped {excess} overflow)"
            )
        else:
            logger.info(
                f"[PrescreenFunnel] Stage 4: All {len(prioritized_nodes)} candidates within validator capacity "
                f"(<= {self.max_validation_candidates})"
            )

        return prioritized_nodes
