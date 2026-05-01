from pydantic import BaseModel, Field


class AnalysisResponse(BaseModel):
    job_id: str
    filename: str
    plagiarism_percentage: float = Field(..., ge=0, le=100)
    humanized_percentage: float = Field(..., ge=0, le=100)
    ai_generated_percentage: float = Field(..., ge=0, le=100)
    top_sources: list[dict]


class ErrorResponse(BaseModel):
    detail: str
from pydantic import BaseModel, Field


class AnalysisResponse(BaseModel):
    job_id: str
    filename: str
    plagiarism_percentage: float = Field(..., ge=0, le=100)
    humanized_percentage: float = Field(..., ge=0, le=100)
    ai_generated_percentage: float = Field(..., ge=0, le=100)
    top_sources: list[dict]


class ErrorResponse(BaseModel):
    detail: str
