import uuid
from datetime import datetime

from pydantic import BaseModel, field_validator

from app.models import AnalysisStatus


class RepoBase(BaseModel):
    owner: str
    name: str
    full_name: str
    description: str | None = None
    language: str | None = None
    stars: int = 0
    license_name: str | None = None
    topics: str | None = None
    locked_sections: str | None = None


class RepoResponse(RepoBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RepoLocksUpdate(BaseModel):
    locked_sections: list[str]


class EstimateRequest(BaseModel):
    repo_url: str
    github_token: str 
    style: str | None = None
    style_url: str | None = None

    @field_validator("repo_url")
    @classmethod
    def validate_github_url(cls, v: str) -> str:
        if "github.com" not in v:
            raise ValueError("URL must be a GitHub repository URL")
        return v.strip().rstrip("/").removesuffix(".git")


class EstimateResponse(BaseModel):
    repo_full_name: str
    file_count: int
    filtered_file_count: int
    estimated_input_tokens: int
    estimated_output_tokens: int
    estimated_cost_usd: float
    model: str
    analysis_id: uuid.UUID


class AnalysisCreate(BaseModel):
    analysis_id: uuid.UUID
    github_token: str 
    openai_key: str
    confirmed: bool
    style: str | None = None
    style_url: str | None = None

    @field_validator("confirmed")
    @classmethod
    def must_be_confirmed(cls, v: bool) -> bool:
        if not v:
            raise ValueError(
                "confirmed must be true — call the estimate endpoint first"
            )
        return v


class PushRequest(BaseModel):
    github_token: str


class RegenerateRequest(BaseModel):
    openai_key: str
    github_token: str
    feedback: str | None = None
    style: str | None = None
    style_url: str | None = None


class UpdateEstimateRequest(BaseModel):
    repo_url: str
    github_token: str 

    @field_validator("repo_url")
    @classmethod
    def validate_github_url(cls, v: str) -> str:
        if "github.com" not in v:
            raise ValueError("URL must be a GitHub repository URL")
        return v.strip().rstrip("/").removesuffix(".git")


class UpdateEstimateResponse(BaseModel):
    repo_full_name: str
    commits_in_window: int
    changed_file_count: int
    estimated_input_tokens: int
    estimated_output_tokens: int
    estimated_cost_usd: float
    model: str
    analysis_id: uuid.UUID


class UpdateConfirm(BaseModel):
    analysis_id: uuid.UUID
    github_token: str
    openai_key: str
    confirmed: bool

    @field_validator("confirmed")
    @classmethod
    def must_be_confirmed(cls, v: bool) -> bool:
        if not v:
            raise ValueError("confirmed must be true")
        return v


class AnalysisResponse(BaseModel):
    id: uuid.UUID
    repo_id: uuid.UUID
    status: AnalysisStatus
    mode: str
    file_count: int | None = None
    filtered_file_count: int | None = None
    estimated_input_tokens: int | None = None
    estimated_output_tokens: int | None = None
    estimated_cost_usd: str | None = None
    readme_content: str | None = None
    previous_readme: str | None = None
    commit_url: str | None = None
    commit_sha: str | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}