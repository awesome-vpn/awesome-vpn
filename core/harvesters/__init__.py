"""Harvesters package for awesome-vpn."""

from core.harvesters.base import BaseHarvester, HarvestResult
from core.harvesters.channel_ledger import ChannelLedger
from core.harvesters.github_radar import GitHubRadarHarvester
from core.harvesters.static_feed import StaticFeedHarvester
from core.harvesters.telegram import TelegramHarvester

__all__ = [
    "BaseHarvester",
    "HarvestResult",
    "ChannelLedger",
    "TelegramHarvester",
    "GitHubRadarHarvester",
    "StaticFeedHarvester",
]
