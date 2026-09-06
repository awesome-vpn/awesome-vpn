"""Base interface and data models for node harvesters."""

import abc
from dataclasses import dataclass, field
from typing import Any


@dataclass
class HarvestResult:
    """Result of a harvesting operation from a source."""

    links: list[str] = field(default_factory=list)
    source_map: dict[str, str] = field(default_factory=dict)  # link -> source descriptor
    discovered_sources: list[str] = field(
        default_factory=list
    )  # e.g., newly discovered channels or repos
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseHarvester(abc.ABC):
    """Abstract base class for all dynamic and static node harvesters."""

    def __init__(self, name: str, timeout: int = 15):
        self.name = name
        self.timeout = timeout

    @abc.abstractmethod
    def harvest(self) -> HarvestResult:
        """Run the harvesting cycle and return discovered proxy links and metadata."""
        raise NotImplementedError
