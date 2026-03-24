from dataclasses import dataclass
from app.models.entities import JobListing


@dataclass
class ApplicationResult:
    success: bool
    status: str
    notes: str
    channel: str


class APIApplicator:
    async def apply(self, job: JobListing, payload: dict) -> ApplicationResult:
        # Placeholder for source-specific API integrations.
        if not payload.get("resume"):
            return ApplicationResult(False, "failed", "missing resume", "api")
        return ApplicationResult(True, "submitted", "submitted via API adapter", "api")


class BrowserApplicator:
    async def apply(self, job: JobListing, payload: dict) -> ApplicationResult:
        # Placeholder for Playwright-driven flows.
        if payload.get("requires_human"):
            return ApplicationResult(False, "needs_review", "unknown question encountered", "browser")
        return ApplicationResult(True, "submitted", "submitted via browser adapter", "browser")


class HybridApplicator:
    def __init__(self):
        self.api = APIApplicator()
        self.browser = BrowserApplicator()

    async def apply(self, job: JobListing, payload: dict) -> ApplicationResult:
        api_result = await self.api.apply(job, payload)
        if api_result.success:
            return api_result
        return await self.browser.apply(job, payload)
