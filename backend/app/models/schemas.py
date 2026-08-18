"""
DriftLens Control Center - API Schemas

Pydantic models for request/response validation.
"""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "ok"
    service: str = "DriftLens Control Center"
    version: str = "0.1.0"


class EnvironmentListResponse(BaseModel):
    """List of available environments."""
    environments: List[str] = Field(..., example=["dev", "staging", "prod"])
    count: int


class DriftComparisonRequest(BaseModel):
    """Request to compare two environments."""
    env_a: str = Field(..., example="dev", description="First environment")
    env_b: str = Field(..., example="prod", description="Second environment")
    mode: str = Field("full", example="full", description="'full' or 'keys_only'")


class OverallDriftMetrics(BaseModel):
    """Overall drift metrics between two environments."""
    similarity_score: float
    similarity_percentage: float
    drift_percentage: float
    intersection_size: int
    union_size: int
    only_in_a: List[str]
    only_in_b: List[str]
    common: List[str]
    drift_detected: bool


class DriftComparisonResponse(BaseModel):
    """Full drift comparison response."""
    environment_a: str
    environment_b: str
    mode: str
    overall: OverallDriftMetrics
    files_compared: List[str]
    files_only_in_a: List[str]
    files_only_in_b: List[str]
    per_file_reports: Dict[str, OverallDriftMetrics]


class SimilarityMatrixResponse(BaseModel):
    """Similarity matrix across all environments."""
    environments: List[str]
    matrix: Dict[str, Dict[str, float]]
