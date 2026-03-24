from pydantic import BaseModel, Field


class CandidateProfileCreate(BaseModel):
    full_name: str
    email: str
    linkedin_url: str | None = None
    master_resume: str
    preferences_json: str = Field(default="{}")


class JobCreate(BaseModel):
    source: str
    company: str
    title: str
    location: str = ""
    external_id: str | None = None
    url: str
    description: str


class RunControlUpdate(BaseModel):
    is_running: bool


class GenerateDraftRequest(BaseModel):
    profile_id: int
    job_id: int


class AnswerQuestionRequest(BaseModel):
    question_text: str
    answer_text: str
    approved: bool = True


class QuestionLookupRequest(BaseModel):
    question_text: str
