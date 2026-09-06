"""Telegram Topology Harvester with automated graph expansion and ledger feedback."""

import concurrent.futures
import logging
import re

from bs4 import BeautifulSoup

from core.harvesters.base import BaseHarvester, HarvestResult
from core.harvesters.channel_ledger import ChannelLedger
from core.spider import Spider

logger = logging.getLogger(__name__)


class TelegramHarvester(BaseHarvester):
    """
    Harvests proxy links from public Telegram channels via web preview,
    and dynamically expands channel topology through message mentions.
    """

    CHANNEL_PATTERN = re.compile(r"(?:@|t\.me/)([a-zA-Z0-9_]{5,32})")

    def __init__(
        self,
        ledger: ChannelLedger,
        spider: Spider | None = None,
        max_workers: int = 15,
        max_candidates_per_run: int = 20,
        timeout: int = 15,
    ):
        super().__init__(name="TelegramTopologyHarvester", timeout=timeout)
        self.ledger = ledger
        self.spider = spider or Spider(max_workers=max_workers, timeout=timeout)
        self.max_workers = max_workers
        self.max_candidates_per_run = max_candidates_per_run

    def fetch_channel(self, channel: str) -> tuple[str, list[str], list[str]]:
        """
        Fetch web preview for a single Telegram channel.
        Returns (channel_name, extracted_proxy_links, discovered_sub_channels).
        """
        name = channel.lstrip("@").strip()
        url = f"https://t.me/s/{name}"
        try:
            resp = self.spider.session.get(url, timeout=self.timeout)
            if resp.status_code == 404:
                logger.debug(f"Telegram channel @{name} not found (404)")
                return name, [], []
            if resp.status_code == 429:
                logger.warning(f"Telegram rate limited (429) when fetching @{name}")
                return name, [], []
            if resp.status_code != 200:
                logger.debug(f"Failed to fetch Telegram channel @{name}: HTTP {resp.status_code}")
                return name, [], []

            soup = BeautifulSoup(resp.text, "html.parser")
            messages = soup.select(".tgme_widget_message_text")

            links: list[str] = []
            discovered_channels: list[str] = []

            for msg in messages:
                text = msg.get_text(separator="\n")
                links.extend(self.spider.extract_links(text))
                for code in msg.select("code"):
                    links.extend(self.spider.extract_links(code.get_text()))

                # Extract forwarded / mentioned channels for topology expansion
                found = self.CHANNEL_PATTERN.findall(text)
                for f_channel in found:
                    f_clean = f_channel.strip()
                    if f_clean and f_clean.lower() != name.lower():
                        discovered_channels.append(f_clean)

            return name, list(set(links)), list(set(discovered_channels))

        except Exception as e:
            logger.debug(f"Error fetching channel @{name}: {e}")
            return name, [], []

    def harvest(self, seed_channels: list[str] | None = None) -> HarvestResult:
        """
        Execute parallel harvesting over active ledger channels and newly discovered candidates.
        """
        target_channels = self.ledger.get_probe_list(
            max_candidates=self.max_candidates_per_run, seed_channels=seed_channels
        )
        logger.info(
            f"[{self.name}] Probing {len(target_channels)} channels (max {self.max_workers} concurrent workers)..."
        )

        all_links: list[str] = []
        source_map: dict[str, str] = {}
        all_discovered_channels: list[str] = []

        workers = min(self.max_workers, max(1, len(target_channels)))
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            future_to_ch = {executor.submit(self.fetch_channel, ch): ch for ch in target_channels}
            for future in concurrent.futures.as_completed(future_to_ch):
                ch_name = future_to_ch[future]
                try:
                    name, links, discovered = future.result()
                    # Record channel yield back to ledger for adaptive pruning/promotion
                    self.ledger.record_result(name, len(links))

                    src_tag = f"https://t.me/s/{name}"
                    for lk in links:
                        if lk not in source_map:
                            source_map[lk] = src_tag
                    all_links.extend(links)

                    # Expand topology into candidate ledger
                    for disc_ch in discovered:
                        if self.ledger.add_candidate(disc_ch, discovered_from=name):
                            all_discovered_channels.append(disc_ch)

                    if links:
                        logger.info(f"  @{name}: {len(links)} links found")
                    else:
                        logger.debug(f"  @{name}: 0 links")

                except Exception as e:
                    logger.debug(f"Harvester worker error on @{ch_name}: {e}")
                    self.ledger.record_result(ch_name, 0)

        # Save ledger changes to disk
        self.ledger.save()

        unique_links = list(set(all_links))
        logger.info(
            f"[{self.name}] Completed: {len(unique_links)} unique links extracted, "
            f"{len(all_discovered_channels)} new channels added to ledger"
        )

        return HarvestResult(
            links=unique_links,
            source_map=source_map,
            discovered_sources=all_discovered_channels,
            metadata={"channels_probed": len(target_channels)},
        )
