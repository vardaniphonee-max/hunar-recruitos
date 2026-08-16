from typing import Any
from pydantic import BaseModel, Field


class QuestionIn(BaseModel):
    prompt: str = Field(min_length=8, max_length=500)
    result_key: str = Field(pattern=r"^[a-z][a-z0-9_]{1,79}$")


class RoleCreate(BaseModel):
    title: str = Field(min_length=3, max_length=160)
    description: str = Field(min_length=30, max_length=8000)
    location: str = Field(min_length=2, max_length=160)
    experience_min: int = Field(ge=0, le=50)
    experience_max: int = Field(ge=0, le=50)
    skills: list[str] = Field(min_length=1, max_length=20)
    questions: list[QuestionIn] = Field(min_length=1, max_length=12)


class SearchCriteria(BaseModel):
    role_id: int
    titles: list[str] = Field(min_length=1, max_length=10)
    locations: list[str] = Field(default_factory=list, max_length=10)
    keywords: list[str] = Field(default_factory=list, max_length=20)
    page: int = Field(default=1, ge=1, le=500)
    per_page: int = Field(default=10, ge=1, le=100)


class CandidateResult(BaseModel):
    external_id: str
    source: str
    is_demo: bool
    name: str
    title: str
    company: str
    location: str
    experience_years: int
    skills: list[str]
    phone: str | None = None
    email: str | None = None
    match_score: int = Field(ge=0, le=100)
    match_reasons: list[str]


class CampaignCreate(BaseModel):
    role_id: int
    name: str = Field(min_length=3, max_length=160)
    candidate_ids: list[int] = Field(min_length=1, max_length=100)
    authorized_live_call: bool = False


class ReviewCreate(BaseModel):
    decision: str = Field(min_length=3, max_length=60)
    note: str = Field(min_length=3, max_length=2000)


class ProviderCallResult(BaseModel):
    provider_call_id: str
    request_id: str
    status: str
    lifecycle_status: str
    raw: dict[str, Any]
