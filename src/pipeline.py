"""
Pipeline orchestration for Awesome VPN crawler.
Refactored from monolithic main.py to clean architecture.
"""

import os
import sys
import json
import logging
from typing import List, Dict, Tuple

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.fetchers import Spider
from src.validators import Validator, quick_tcp_prescreen
from src.processors import Deduplicator, GeoEnricher
from src.exporters import Base64Exporter, SingboxExporter, ClashExporter

logger = logging.getLogger(__name__)


class Pipeline:
    """Main pipeline orchestrating the entire crawling and validation process."""
    
    def __init__(
        self,
        enable_validation: bool = True,
        enable_speed_test: bool = False,
        workers: int = 24,
        validate_workers: int = 50,
        tcp_prescreen: bool = True,
        base_dir: str = None
    ):
        self.enable_validation = enable_validation
        self.enable_speed_test = enable_speed_test
        self.workers = workers
        self.validate_workers = validate_workers
        self.tcp_prescreen = tcp_prescreen
        self.base_dir = base_dir or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Initialize components
        self.spider = Spider(max_workers=workers)
        self.deduplicator = Deduplicator()
        self.geo_enricher = GeoEnricher(self.base_dir)
        
        self.validator = None
        if enable_validation:
            from src.validators.binary_manager import BinaryManager
            bm = BinaryManager(self.base_dir)
            sing_box_path = bm.get_singbox_path()
            self.validator = Validator(sing_box_path)
    
    def run(self, sources_config: Dict, output_dir: str) -> List[Dict]:
        """
        Execute the full pipeline.
        
        Args:
            sources_config: Dict with 'urls', 'telegram_channels', 'extra_urls'
            output_dir: Directory to save output files
            
        Returns:
            List of valid nodes
        """
        logger.info("=" * 60)
        logger.info("Pipeline Starting...")
        logger.info("=" * 60)
        
        # Phase 1: Fetch
        nodes = self._fetch(sources_config)
        
        # Phase 2: Parse & Deduplicate
        nodes = self._deduplicate(nodes)
        
        # Phase 3: Validate
        if self.enable_validation and nodes:
            nodes = self._validate(nodes)
        
        # Phase 4: Enrich
        if nodes:
            nodes = self._enrich(nodes)
        
        # Phase 5: Export
        if nodes:
            self._export(nodes, output_dir)
        
        logger.info("=" * 60)
        logger.info(f"Pipeline Complete: {len(nodes)} nodes")
        logger.info("=" * 60)
        
        return nodes
    
    def _fetch(self, config: Dict) -> List[str]:
        """Fetch all links from sources."""
        logger.info("\n[1/5] Fetching from sources...")
        
        all_links = []
        
        # Fetch URLs
        urls = config.get('urls', [])
        if urls:
            results = self.spider.fetch_urls_parallel(urls)
            for url, content in results.items():
                if content:
                    links = self.spider.parse_subscription(content)
                    logger.info(f"  {url}: {len(links)} links")
                    all_links.extend(links)
        
        # Fetch Telegram
        channels = config.get('telegram_channels', [])
        if channels:
            logger.info(f"\n  Fetching {len(channels)} Telegram channels...")
            import concurrent.futures
            def fetch_ch(channel):
                links, _ = self.spider.fetch_telegram(channel)
                return channel, links
            
            tg_workers = min(24, len(channels)) if channels else 1
            with concurrent.futures.ThreadPoolExecutor(max_workers=tg_workers) as executor:
                for channel, links in executor.map(fetch_ch, channels):
                    logger.info(f"    @{channel}: {len(links)} links")
                    all_links.extend(links)
        
        # Extra URLs
        extra_urls = config.get('extra_urls', [])
        for url in extra_urls:
            content = self.spider.fetch_url(url)
            if content:
                links = self.spider.parse_subscription(content)
                all_links.extend(links)
        
        unique_links = list(set(all_links))
        logger.info(f"\n  Total unique links: {len(unique_links)}")
        return unique_links
    
    def _deduplicate(self, links: List[str]) -> List[Dict]:
        """Parse links and deduplicate nodes."""
        logger.info("\n[2/5] Parsing and deduplicating...")
        
        import concurrent.futures
        from core.parsers import vmess, vless, ss, trojan, hysteria2, tuic
        
        PROTOCOL_PARSERS = {
            'vmess': vmess, 'vless': vless, 'ss': ss,
            'trojan': trojan, 'hysteria2': hysteria2, 'hy2': hysteria2, 'tuic': tuic
        }
        
        def parse_link(link):
            try:
                protocol = link.split('://')[0].lower()
                parser = PROTOCOL_PARSERS.get(protocol)
                if parser:
                    return parser.parse(link), link
            except:
                pass
            return None, link
        
        # Parse concurrently
        raw_nodes = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.workers) as executor:
            futures = {executor.submit(parse_link, link): link for link in links}
            for future in concurrent.futures.as_completed(futures):
                node, link = future.result()
                if node:
                    raw_nodes.append((node, link))
        
        # Deduplicate (single-threaded for thread safety)
        nodes = []
        for node, link in raw_nodes:
            if not self.deduplicator.is_duplicate(node) and not self.deduplicator.is_redundant_server(node):
                node['_original_link'] = link  # Keep for later
                nodes.append(node)
        
        logger.info(f"  Parsed: {len(raw_nodes)}, After dedup: {len(nodes)}")
        return nodes
    
    def _validate(self, nodes: List[Dict]) -> List[Dict]:
        """Validate nodes."""
        logger.info("\n[3/5] Validating nodes...")
        
        # TCP pre-screening
        if self.tcp_prescreen:
            logger.info("  Quick TCP pre-screening...")
            nodes = quick_tcp_prescreen(nodes, max_workers=100, timeout=2)
            logger.info(f"  After TCP pre-screen: {len(nodes)}")
        
        # Full validation
        if self.validator:
            nodes = self.validator.validate_nodes_parallel(
                nodes, timeout=5, max_workers=self.validate_workers
            )
            logger.info(f"  After full validation: {len(nodes)}")
        
        return nodes
    
    def _enrich(self, nodes: List[Dict]) -> List[Dict]:
        """Enrich nodes with geo information."""
        logger.info("\n[4/5] Enriching with geo info...")
        
        for node in nodes:
            server = node.get('server', '')
            if server:
                node['tag'] = self.geo_enricher.format_node_name(server)
        
        return nodes
    
    def _export(self, nodes: List[Dict], output_dir: str):
        """Export to all formats."""
        logger.info("\n[5/5] Exporting...")
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Sing-box JSON
        SingboxExporter.export(nodes, os.path.join(output_dir, 'sing-box.json'))
        
        # Base64
        link_map = {n.get('tag', ''): n.get('_original_link', '') for n in nodes}
        Base64Exporter.export(nodes, link_map, os.path.join(output_dir, 'all'))
        
        # Clash YAML
        ClashExporter.export(nodes, os.path.join(output_dir, 'clash.yaml'))
        
        logger.info(f"  Exported to {output_dir}")
