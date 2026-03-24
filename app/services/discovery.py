from dataclasses import dataclass
from typing import Protocol


@dataclass
class DiscoveredJob:
    source: str
    company: str
    title: str
    location: str
    url: str
    description: str
    external_id: str | None = None


class JobSource(Protocol):
    async def fetch(self) -> list[DiscoveredJob]: ...


class StaticSource:
    def __init__(self, source: str, jobs: list[DiscoveredJob]):
        self.source = source
        self.jobs = jobs

    async def fetch(self) -> list[DiscoveredJob]:
        return self.jobs


class DiscoveryOrchestrator:
    def __init__(self, sources: list[JobSource]):
        self.sources = sources

    async def collect(self) -> list[DiscoveredJob]:
        items: list[DiscoveredJob] = []
        for source in self.sources:
            items.extend(await source.fetch())
        return items
