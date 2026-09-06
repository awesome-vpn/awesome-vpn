"""GitHub Radar Harvester for sniffing high-velocity open-source proxy repositories.

Features automatic repository health tracking, 404/failure pruning,
and dynamic candidate repository discovery.
"""

import concurrent.futures
import json
import logging
import os
from datetime import UTC, datetime
from typing import Any

from core.harvesters.base import BaseHarvester, HarvestResult
from core.spider import Spider

logger = logging.getLogger(__name__)


class GitHubRadarHarvester(BaseHarvester):
    """
    Harvests nodes directly from raw files of active GitHub proxy projects.
    Bypasses GitHub Search API rate limits while maintaining freshness.
    Automatically disables 404/dead repositories and tracks yield reputation.
    """

    RAW_URL_TEMPLATE = "https://raw.githubusercontent.com/{repo}/{branch}/{path}"
    MAX_CONSECUTIVE_FAILURES = 3

    def __init__(
        self,
        radar_config_path: str,
        spider: Spider | None = None,
        timeout: float = 10.0,
        max_workers: int = 10,
        max_links_per_target: int = 150,
    ):
        super().__init__(name="GitHubRadarHarvester", timeout=int(timeout))
        self.radar_config_path = radar_config_path
        self.spider = spider or Spider(max_workers=max_workers)
        self.max_workers = max_workers
        self.max_links_per_target = max_links_per_target
        self.repositories: list[dict[str, Any]] = []
        self.load_radar()

    def load_radar(self) -> None:
        """Load tracked repositories from radar.json."""
        if not os.path.exists(self.radar_config_path):
            self.repositories = []
            return
        try:
            with open(self.radar_config_path, encoding="utf-8") as f:
                data = json.load(f)
                self.repositories = data.get("repositories", [])
        except Exception as e:
            logger.warning(f"Failed to read radar config from {self.radar_config_path}: {e}")
            self.repositories = []

    def save_radar(self) -> None:
        """Persist tracked repositories with updated health metrics back to radar.json."""
        try:
            os.makedirs(os.path.dirname(os.path.abspath(self.radar_config_path)), exist_ok=True)
            with open(self.radar_config_path, "w", encoding="utf-8") as f:
                json.dump({"repositories": self.repositories}, f, indent=2, ensure_ascii=False)
            logger.debug(f"Saved radar config to {self.radar_config_path}")
        except Exception as e:
            logger.error(f"Failed to save radar config to {self.radar_config_path}: {e}")

    def add_repository(
        self,
        repo: str,
        branch: str = "main",
        paths: list[str] | None = None,
        description: str = "",
    ) -> bool:
        """Register a new candidate repository into the radar."""
        clean_repo = repo.strip()
        if not clean_repo or "/" not in clean_repo:
            return False
        for entry in self.repositories:
            if entry.get("repo", "").lower() == clean_repo.lower():
                return False

        new_entry = {
            "repo": clean_repo,
            "branch": branch,
            "paths": paths or ["sub.txt"],
            "enabled": True,
            "description": description,
            "consecutive_failures": 0,
            "total_yielded": 0,
            "first_added_at": datetime.now(UTC).isoformat(),
        }
        self.repositories.append(new_entry)
        self.save_radar()
        logger.info(f"Added new repository to GitHub Radar: {clean_repo}")
        return True

    def fetch_target(self, repo: str, branch: str, path: str) -> tuple[str, list[str]]:
        """Fetch and parse a single raw target file."""
        url = self.RAW_URL_TEMPLATE.format(repo=repo, branch=branch, path=path.lstrip("/"))
        source_label = f"GH:{repo}"
        try:
            content = self.spider.fetch_url(url, timeout=self.timeout)
            if not content:
                return source_label, []
            links = self.spider.parse_subscription(content)
            if self.max_links_per_target > 0 and len(links) > self.max_links_per_target:
                links = links[: self.max_links_per_target]
            return source_label, links
        except Exception as e:
            logger.debug(f"Failed to fetch radar target {url}: {e}")
            return source_label, []

    def harvest(self) -> HarvestResult:
        """Execute parallel fetching of all active radar targets and update health ledger."""
        targets: list[tuple[str, str, str]] = []
        active_repos: list[dict[str, Any]] = []

        for entry in self.repositories:
            if not entry.get("enabled", True):
                continue
            repo = entry.get("repo", "").strip()
            branch = entry.get("branch", "master").strip()
            paths = entry.get("paths", [])
            if not repo or not paths:
                continue
            active_repos.append(entry)
            for p in paths:
                targets.append((repo, branch, p))

        logger.info(
            f"[{self.name}] Polling {len(targets)} targets across {len(active_repos)} active repositories..."
        )

        all_links: list[str] = []
        source_map: dict[str, str] = {}
        repo_yields: dict[str, int] = {entry["repo"]: 0 for entry in active_repos}

        workers = min(self.max_workers, max(1, len(targets)))
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            future_to_target = {
                executor.submit(self.fetch_target, repo, branch, path): (repo, path)
                for repo, branch, path in targets
            }
            for future in concurrent.futures.as_completed(future_to_target):
                repo, path = future_to_target[future]
                try:
                    source_label, links = future.result()
                    if links:
                        logger.info(f"  {source_label}/{path}: {len(links)} links")
                        for lk in links:
                            if lk not in source_map:
                                source_map[lk] = source_label
                        all_links.extend(links)
                        repo_yields[repo] = repo_yields.get(repo, 0) + len(links)
                    else:
                        logger.debug(f"  {source_label}/{path}: 0 links")
                except Exception as e:
                    logger.debug(f"Radar target error on {repo}/{path}: {e}")

        # Update health status and auto-prune failing repos
        now_iso = datetime.now(UTC).isoformat()
        state_changed = False
        for entry in active_repos:
            repo_name = entry["repo"]
            yielded = repo_yields.get(repo_name, 0)
            entry["last_probed_at"] = now_iso

            if yielded > 0:
                entry["consecutive_failures"] = 0
                entry["total_yielded"] = entry.get("total_yielded", 0) + yielded
                entry["last_success_at"] = now_iso
                state_changed = True
            else:
                entry["consecutive_failures"] = entry.get("consecutive_failures", 0) + 1
                state_changed = True
                if entry["consecutive_failures"] >= self.MAX_CONSECUTIVE_FAILURES:
                    entry["enabled"] = False
                    entry["disabled_reason"] = (
                        f"Auto-disabled after {entry['consecutive_failures']} empty/404 runs"
                    )
                    logger.warning(
                        f"Repository '{repo_name}' auto-disabled in radar after {entry['consecutive_failures']} consecutive empty runs"
                    )

        if state_changed:
            self.save_radar()

        unique_links = list(set(all_links))
        logger.info(f"[{self.name}] Completed: {len(unique_links)} unique links extracted")

        return HarvestResult(
            links=unique_links,
            source_map=source_map,
            metadata={"targets_polled": len(targets)},
        )
