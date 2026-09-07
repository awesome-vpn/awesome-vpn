"""Core orchestration pipeline for awesome-vpn."""

import concurrent.futures
import logging
import os
from typing import Any

from core.binary_manager import BinaryManager
from core.deduplicator import ensure_unique_tags
from core.filters.prescreen import PrescreenFunnel
from core.geo_utils import GeoUtils
from core.harvesters.channel_ledger import ChannelLedger
from core.harvesters.github_radar import GitHubRadarHarvester
from core.harvesters.static_feed import StaticFeedHarvester
from core.harvesters.telegram import TelegramHarvester
from core.matrix.exporter import MatrixExporter
from core.node_ledger import NodeLedger
from core.quality import filter_by_china_probe, filter_timeout_outliers, quality_score
from core.spider import Spider
from core.validator import Validator

# Import protocol parsers
try:
    import hysteria2
    import ss
    import trojan
    import tuic
    import vless
    import vmess
except ImportError:
    from core.parsers import hysteria2, ss, trojan, tuic, vless, vmess

PROTOCOL_PARSERS = {
    "vmess": vmess,
    "vless": vless,
    "ss": ss,
    "trojan": trojan,
    "hysteria2": hysteria2,
    "hy2": hysteria2,
    "tuic": tuic,
}

logger = logging.getLogger(__name__)


def format_source_label(source_url: str) -> str:
    """Generate concise source label for node tags."""
    if not source_url:
        return "Unknown"
    s = source_url.strip()
    if "t.me" in s:
        try:
            channel = s.split("t.me/")[-1].split("/")[0].lstrip("@").split("?")[0]
            if channel and channel != "s":
                return f"TG:{channel[:18]}"
        except Exception:
            pass
        return "TG"
    if s.startswith("@"):
        return f"TG:{s.lstrip('@')[:18]}"
    if "github" in s.lower() or "raw.githubusercontent" in s.lower():
        try:
            from urllib.parse import urlparse

            path = urlparse(s).path.strip("/")
            parts = path.split("/")
            if len(parts) >= 2:
                repo = f"{parts[0]}/{parts[1]}"[:24]
                return f"GH:{repo}"
        except Exception:
            pass
        return "GH"
    try:
        from urllib.parse import urlparse

        host = urlparse(s).hostname or ""
        if host.startswith("www."):
            host = host[4:]
        return host[:24] if host else s[:16]
    except Exception:
        return s[:16]


class NodePipeline:
    """End-to-end pipeline coordinating discovery, screening, verification, and matrix export."""

    def __init__(
        self,
        base_dir: str,
        output_dir: str,
        validate: bool = True,
        local_mode: bool = False,
        workers: int = 10,
        validate_workers: int = 30,
        max_nodes: int = 80,
    ):
        self.base_dir = base_dir
        self.output_dir = output_dir
        self.validate = validate
        self.local_mode = local_mode
        self.workers = workers
        self.validate_workers = validate_workers
        self.max_nodes = max_nodes

        self.spider = Spider(max_workers=self.workers)
        self.ledger_path = os.path.join(self.base_dir, "config", "channels.json")
        self.radar_path = os.path.join(self.base_dir, "config", "radar.json")
        self.node_ledger_path = os.path.join(self.base_dir, "config", "node_ledger.json")
        self.sources_json_path = os.path.join(self.base_dir, "config", "sources.json")
        self.sources_list_path = os.path.join(self.base_dir, "config", "sources.list")
        self.mmdb_path = os.path.join(self.base_dir, "config", "GeoLite2-City.mmdb")

        self.ledger = ChannelLedger(self.ledger_path)
        self.node_ledger = NodeLedger(self.node_ledger_path)
        self.exporter = MatrixExporter(self.output_dir)

    def harvest_all(self) -> tuple[list[str], dict[str, str]]:
        """Harvest across Telegram topology, GitHub Radar, and static feeds."""
        logger.info("\n" + "=" * 60)
        logger.info("[1/4] Harvesting proxy nodes across distributed sources...")
        logger.info("=" * 60)

        all_links: list[str] = []
        link_to_source: dict[str, str] = {}

        # 1. Telegram Topology Harvester
        tg_secrets = os.getenv("TELEGRAM_CHANNELS", "")
        seed_channels = [c.strip() for c in tg_secrets.split(",") if c.strip()]
        tg_harvester = TelegramHarvester(
            ledger=self.ledger,
            spider=self.spider,
            max_workers=min(20, self.workers * 2),
        )
        tg_result = tg_harvester.harvest(seed_channels=seed_channels)
        all_links.extend(tg_result.links)
        link_to_source.update(tg_result.source_map)

        # 2. GitHub Radar Harvester
        gh_harvester = GitHubRadarHarvester(
            radar_config_path=self.radar_path,
            spider=self.spider,
            max_workers=self.workers,
        )
        gh_result = gh_harvester.harvest()
        all_links.extend(gh_result.links)
        link_to_source.update(gh_result.source_map)

        # 3. Static & Parameterized Feeds
        extra_urls = [u.strip() for u in os.getenv("EXTRA_URLS", "").splitlines() if u.strip()]
        static_harvester = StaticFeedHarvester(
            config_path=self.sources_json_path,
            sources_list_path=self.sources_list_path,
            extra_urls=extra_urls,
            spider=self.spider,
            max_workers=self.workers,
        )
        static_result = static_harvester.harvest()
        all_links.extend(static_result.links)
        link_to_source.update(static_result.source_map)

        unique_links = list(dict.fromkeys(all_links))
        logger.info(f"Harvest complete. Total unique raw candidate links: {len(unique_links)}")
        return unique_links, link_to_source

    def parse_links_parallel(
        self, unique_links: list[str], link_to_source: dict[str, str]
    ) -> list[tuple[dict[str, Any], str, str]]:
        """Parse raw links into node configuration dictionaries."""
        logger.info("\n" + "=" * 60)
        logger.info(f"[2/4] Parsing {len(unique_links)} raw links to Sing-box outbounds...")
        logger.info("=" * 60)

        def _parse(link):
            try:
                protocol = link.split("://")[0].lower() if "://" in link else ""
                parser = PROTOCOL_PARSERS.get(protocol)
                if parser:
                    return parser.parse(link), link
            except Exception:
                pass
            return None, link

        parsed_items: list[tuple[dict[str, Any], str, str]] = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.workers) as executor:
            future_to_link = {executor.submit(_parse, lk): lk for lk in unique_links}
            for future in concurrent.futures.as_completed(future_to_link):
                node, link = future.result()
                if node:
                    source_label = link_to_source.get(link, "Unknown")
                    nodes = list(node) if isinstance(node, tuple) else [node]
                    for n in nodes:
                        parsed_items.append((n, link, source_label))

        logger.info(f"Successfully parsed: {len(parsed_items)} raw node objects")
        return parsed_items

    def screen_and_validate(
        self,
        raw_nodes: list[tuple[dict[str, Any], str, str]],
    ) -> tuple[list[dict[str, Any]], dict[int, str], list[float]]:
        """Screen candidates with tiered funnel and perform active validation."""
        logger.info("\n" + "=" * 60)
        logger.info("[3/4] Tiered prescreening & active validation...")
        logger.info("=" * 60)

        # 1. Prescreen Funnel
        funnel = PrescreenFunnel(
            max_validation_candidates=400,
            tcp_workers=60,
            tcp_timeout=2.0,
            local_mode=self.local_mode,
        )
        screened_candidates = funnel.filter(raw_nodes)

        valid_nodes: list[dict[str, Any]] = [item[0] for item in screened_candidates]
        source_links: dict[int, str] = {id(item[0]): item[1] for item in screened_candidates}
        node_source_map: dict[int, str] = {id(item[0]): item[2] for item in screened_candidates}

        latencies: list[float] = []

        if not valid_nodes:
            logger.info("No candidates available for screening.")
            return [], source_links, []

        if not self.validate:
            logger.info(
                "Active validation skipped. Ranking candidates by static anti-censorship score..."
            )
            for n in valid_nodes:
                longevity_bonus = self.node_ledger.get_longevity_bonus(n)
                n["_quality"] = quality_score(n, None, longevity_bonus=longevity_bonus)
            valid_nodes.sort(key=lambda x: x.get("_quality", 0), reverse=True)
            tested_nodes = valid_nodes
        else:
            # 2. Sing-box Active Validation
            bm = BinaryManager(self.base_dir)
            sing_box_path = bm.get_singbox_path()
            validator = Validator(sing_box_path, local_mode=self.local_mode)
            tested_nodes = validator.validate_nodes_parallel(
                valid_nodes, timeout=5, max_workers=self.validate_workers
            )
            logger.info(f"Active validation passed: {len(tested_nodes)} nodes")

            passed_ids = {id(n) for n in tested_nodes}
            for n in valid_nodes:
                if id(n) in passed_ids:
                    lat = float(n.get("_latency_ms", 0.0))
                    self.node_ledger.record_validation(n, is_valid=True, latency_ms=lat)
                else:
                    self.node_ledger.record_validation(n, is_valid=False)

            if not tested_nodes:
                self.node_ledger.garbage_collect()
                self.node_ledger.save()
                return [], source_links, []

            # 3. Quality scoring & Latency outlier filter (500ms hard threshold)
            for n in tested_nodes:
                lat = n.get("_latency_ms", 0.0)
                if lat > 0:
                    latencies.append(lat)
                longevity_bonus = self.node_ledger.get_longevity_bonus(n)
                n["_quality"] = quality_score(n, lat, longevity_bonus=longevity_bonus)

            tested_nodes.sort(key=lambda x: x.get("_quality", 0), reverse=True)
            max_lat_threshold = 2000 if self.local_mode else 500
            tested_nodes = filter_timeout_outliers(
                tested_nodes, "_latency_ms", max_latency_ms=max_lat_threshold
            )

            # 4. Optional China external probe filter
            china_check_url = os.getenv("CHINA_CHECK_URL", "").strip()
            if china_check_url:
                tested_nodes = filter_by_china_probe(tested_nodes, china_check_url)

            self.node_ledger.garbage_collect()
            self.node_ledger.save()

        # 5. Top-N truncation
        if self.max_nodes > 0 and len(tested_nodes) > self.max_nodes:
            logger.info(f"Truncating to Top-{self.max_nodes} highest quality nodes")
            tested_nodes = tested_nodes[: self.max_nodes]

        # Clean internal markers
        for n in tested_nodes:
            n.pop("_quality", None)
            n.pop("_latency_ms", None)

        # 6. Geo resolving
        geo_utils = GeoUtils(self.mmdb_path)
        node_data = [
            (node, node.get("tag", ""), node_source_map.get(id(node), "Unknown"))
            for node in tested_nodes
        ]

        def _resolve_geo(item):
            node, original_tag, source_url = item
            server = node.get("server", "")
            geo_name = geo_utils.format_node_name(server) if server else original_tag
            source_label = format_source_label(source_url)
            node_name = f"{geo_name} [{source_label}]"
            return node, node_name

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=min(30, max(1, len(tested_nodes)))
        ) as executor:
            geo_results = list(executor.map(_resolve_geo, node_data))

        for node, node_name in geo_results:
            node["tag"] = node_name

        geo_utils.close()
        ensure_unique_tags(tested_nodes)

        return tested_nodes, source_links, latencies

    def export(
        self,
        curated_nodes: list[dict[str, Any]],
        source_links: dict[int, str],
        raw_links: list[str],
        latencies: list[float],
    ) -> dict[str, str]:
        """Export multi-tier subscription matrix and generate telemetry."""
        logger.info("\n" + "=" * 60)
        logger.info("[4/4] Exporting subscription matrix and telemetry...")
        logger.info("=" * 60)

        exported_paths = self.exporter.export_all(curated_nodes, source_links, raw_links)

        logger.info(f"Exported files to {self.output_dir}:")
        for key, path in exported_paths.items():
            logger.info(f"  [{key}] -> {path}")

        return exported_paths

    def run(self) -> dict[str, Any]:
        """Execute the complete pipeline."""
        raw_links, link_to_source = self.harvest_all()
        raw_nodes = self.parse_links_parallel(raw_links, link_to_source)
        curated_nodes, source_links, latencies = self.screen_and_validate(raw_nodes)
        exported = self.export(curated_nodes, source_links, raw_links, latencies)
        return {
            "total_raw": len(raw_links),
            "curated_count": len(curated_nodes),
            "exported_files": exported,
        }
