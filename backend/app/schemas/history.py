from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from app.schemas.ingredients import IngredientCheckStatus


ScanType = Literal["manual_ingredient_check", "barcode_lookup"]


class ScanHistoryEntry(BaseModel):
    scan_type: ScanType
    barcode: Optional[str] = None
    product_name: Optional[str] = None
    brand_name: Optional[str] = None
    product_source: Optional[str] = None
    submitted_ingredient_text: Optional[str] = None
    assessment_status: IngredientCheckStatus
    explanation: Optional[str] = None
    matched_ingredient_summary: Optional[str] = None
    created_at: datetime


class ScanHistoryResponse(BaseModel):
    items: List[ScanHistoryEntry] = Field(default_factory=list)
