from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from app.schemas.ingredients import IngredientCheckStatus


ScanType = Literal[
    "manual_ingredient_check",
    "barcode_lookup",
    "barcode_enrichment",
]


class ScanHistoryEntry(BaseModel):
    scan_type: ScanType
    barcode: Optional[str] = None
    product_name: Optional[str] = None
    brand_name: Optional[str] = None
    image_url: Optional[str] = None
    product_source: Optional[str] = None
    submitted_ingredient_text: Optional[str] = None
    assessment_status: IngredientCheckStatus
    explanation: Optional[str] = None
    matched_ingredient_summary: Optional[str] = None
    created_at: datetime


class ScanHistoryResponse(BaseModel):
    items: List[ScanHistoryEntry] = Field(default_factory=list)


class MissedBarcodeSummaryEntry(BaseModel):
    barcode: str
    miss_count: int
    first_seen_at: datetime
    last_seen_at: datetime
    latest_explanation: Optional[str] = None


class MissedBarcodeSummaryResponse(BaseModel):
    items: List[MissedBarcodeSummaryEntry] = Field(default_factory=list)


class InconsistentBarcodeSummaryEntry(BaseModel):
    barcode: str
    count: int
    first_seen_at: datetime
    last_seen_at: datetime
    latest_explanation: Optional[str] = None
    latest_source: Optional[str] = None
    product_quality_status: Literal["inconsistent"] = "inconsistent"


class InconsistentBarcodeSummaryResponse(BaseModel):
    items: List[InconsistentBarcodeSummaryEntry] = Field(default_factory=list)
