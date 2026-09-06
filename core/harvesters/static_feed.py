"""Static Feed Harvester for fixed URLs, date-parameterized sources, and nested lists."""

import json
import logging
import os
import urllib.parse
from datetime import datetime
from typing import Any

from core.harvesters.base import BaseHarvester, HarvestResult
from core.spider import Spider

logger = logging.getLogger(__name__)


def parse_source_params(param_str: str) -> dict[str, Any]:
    options: dict[str, Any] = {}
    if not param_str:
        return options
    try:
        params = urllib.parse.parse_qs(param_str, keep_blank_values=True)
        if "max" in params and params["max"]:
            try:
                options["max_nodes"] = int(params["max"][0])
            except (ValueError, TypeError):
                pass
        if "ignore" in params and params["ignore"]:
            ignore = [p.strip() for p in params["ignore"][0].split(",") if p.strip()]
            if ignore:
                options["ignore_protocols"] = ignore
    except Exception:
        pass
    return options


def apply_source_filters(links: list[str], options: dict) -> list[str]:
    if not links:
        return []
    ignore = set([p.lower() for p in options.get("ignore_protocols", [])])
    if ignore:
        filtered = []
        for link in links:
            protocol = link.split("://")[0].lower() if "://" in link else ""
            if protocol and protocol in ignore:
                continue
            filtered.append(link)
        links = filtered
    max_nodes = options.get("max_nodes")
    if isinstance(max_nodes, int) and max_nodes > 0:
        links = links[:max_nodes]
    return links


def resolve_date_url(url: str) -> str:
    try:
        return datetime.now().strftime(url)
    except Exception:
        return url


class StaticFeedHarvester(BaseHarvester):
    """Harvester for static seed URLs, sources.json, and sources.list files."""

    def __init__(
        self,
        config_path: str | None = None,
        sources_list_path: str | None = None,
        extra_urls: list[str] | None = None,
        spider: Spider | None = None,
        max_workers: int = 10,
        timeout: int = 15,
    ):
        super().__init__(name="StaticFeedHarvester", timeout=timeout)
        self.config_path = config_path
        self.sources_list_path = sources_list_path
        self.extra_urls = extra_urls or []
        self.spider = spider or Spider(max_workers=max_workers, timeout=timeout)
        self.max_workers = max_workers

    def _load_sources_json(self) -> tuple[list[str], dict[str, dict[str, Any]]]:
        urls: list[str] = []
        url_options: dict[str, dict[str, Any]] = {}
        if not self.config_path or not os.path.exists(self.config_path):
            return urls, url_options

        try:
            with open(self.config_path, encoding="utf-8") as f:
                data = json.load(f)
            raw_sources = data.get("urls", [])
            for entry in raw_sources:
                options: dict[str, Any] = {}
                if isinstance(entry, dict):
                    if entry.get("enabled") is False:
                        continue
                    url = entry.get("url")
                    if not url:
                        continue
                    if entry.get("update_method") == "change_date":
                        url = resolve_date_url(url)
                    if entry.get("max_nodes"):
                        options["max_nodes"] = entry.get("max_nodes")
                    if entry.get("ignore_protocols"):
                        options["ignore_protocols"] = entry.get("ignore_protocols")
                else:
                    url = str(entry)
                urls.append(url)
                url_options[url] = options
        except Exception as e:
            logger.warning(f"Error loading {self.config_path}: {e}")

        return urls, url_options

    def _load_sources_list(self) -> list[tuple[str, dict[str, Any]]]:
        entries: list[tuple[str, dict[str, Any]]] = []
        if not self.sources_list_path or not os.path.exists(self.sources_list_path):
            return entries

        allow_blocked = os.getenv("ALLOW_BLOCKED_SOURCES") == "1"
        try:
            with open(self.sources_list_path, encoding="utf-8") as f:
                for raw_line in f:
                    line = raw_line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if line == "EOF":
                        break
                    blocked = False
                    if line.startswith("!"):
                        blocked = True
                        line = line[1:].strip()
                    if blocked and not allow_blocked:
                        continue
                    is_date = False
                    if line.startswith("+date"):
                        is_date = True
                        line = line[len("+date") :].strip()
                    is_list = False
                    if line.startswith("*"):
                        is_list = True
                        line = line[1:].strip()
                    param_str = ""
                    if "#" in line:
                        line, param_str = line.split("#", 1)
                    url = line.strip()
                    if not url:
                        continue
                    if is_date:
                        url = resolve_date_url(url)
                    options = parse_source_params(param_str)
                    if is_list:
                        try:
                            content = self.spider.fetch_url(url)
                            if content:
                                for item in content.splitlines():
                                    item = item.strip()
                                    if not item or item.startswith("#"):
                                        continue
                                    item_url = item.split("#")[0].strip()
                                    if item_url.startswith("http"):
                                        entries.append((item_url, options))
                        except Exception as e:
                            logger.debug(f"Error fetching nested list {url}: {e}")
                    else:
                        entries.append((url, options))
        except Exception as e:
            logger.warning(f"Error reading sources.list {self.sources_list_path}: {e}")

        return entries

    def harvest(self) -> HarvestResult:
        urls_to_fetch, url_options = self._load_sources_json()

        for u in self.extra_urls:
            urls_to_fetch.append(u)
            url_options[u] = {}

        list_entries = self._load_sources_list()
        for u, opts in list_entries:
            urls_to_fetch.append(u)
            url_options[u] = opts

        urls_to_fetch = list(dict.fromkeys(urls_to_fetch))
        logger.info(f"[{self.name}] Fetching {len(urls_to_fetch)} static and parameterized URLs...")

        all_links: list[str] = []
        source_map: dict[str, str] = {}

        fetch_results = self.spider.fetch_urls_parallel(urls_to_fetch, max_workers=self.max_workers)
        for url, content in fetch_results.items():
            if content:
                links = self.spider.parse_subscription(content)
                links = apply_source_filters(links, url_options.get(url, {}))
                logger.info(f"  {url}: {len(links)} links")
                for link in links:
                    if link not in source_map:
                        source_map[link] = url
                all_links.extend(links)

        unique_links = list(set(all_links))
        logger.info(f"[{self.name}] Completed: {len(unique_links)} unique links extracted")
        return HarvestResult(links=unique_links, source_map=source_map)
