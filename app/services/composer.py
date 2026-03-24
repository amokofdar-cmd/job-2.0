from app.models.entities import CandidateProfile, JobListing
from app.services.llm_router import LLMRouter


class DraftComposer:
    def __init__(self, llm_router: LLMRouter):
        self.llm = llm_router

    async def compose(self, profile: CandidateProfile, job: JobListing) -> dict:
        prompt = (
            "Generate a truthful tailored resume summary and short cover letter."
            f"\nCandidate: {profile.full_name}\n"
            f"Resume: {profile.master_resume}\n"
            f"Job: {job.title} at {job.company}\n"
            f"Description: {job.description}\n"
            "Return JSON keys: resume_summary, cover_letter, interview_prep_topics."
        )
        response = await self.llm.chat(messages=[{"role": "user", "content": prompt}])
        return {
            "model": response.model,
            "raw": response.text,
        }
