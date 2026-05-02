from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from app.schemas.ingredients import AllergyProfile, IngredientCheckStatus, MatchedIngredient

IngredientCoverageStatus = Literal["complete", "partial", "missing", "unknown"]
ProductEnrichmentSource = Literal["manual_entry", "text_scan"]


class ProductLookupRequest(BaseModel):
    barcode: str = Field(..., min_length=3)
    allergy_profile: Optional[AllergyProfile] = None


class ProductEnrichmentRequest(BaseModel):
    barcode: str = Field(..., min_length=3)
    ingredient_text: str = Field(..., min_length=1)
    product_name: Optional[str] = None
    brand_name: Optional[str] = None
    source: Optional[ProductEnrichmentSource] = None
    allergy_profile: Optional[AllergyProfile] = None


class NormalizedProduct(BaseModel):
    barcode: str
    brand_name: Optional[str] = None
    product_name: Optional[str] = None
    image_url: Optional[str] = None
    ingredient_text: Optional[str] = None
    ingredient_coverage_status: IngredientCoverageStatus = "unknown"
    source: str


class ProductLookupResponse(BaseModel):
    found: bool
    source: str = "not_found"
    lookup_path: List[str] = Field(default_factory=list)
    product: Optional[NormalizedProduct] = None
    ingredient_text: Optional[str] = None
    assessment_result: Optional[IngredientCheckStatus] = None
    matched_ingredients: List[MatchedIngredient] = Field(default_factory=list)
    explanation: str
    ruleset_version: Optional[str] = None
    unknown_terms: List[str] = Field(default_factory=list)


class SavedProductEntry(BaseModel):
    barcode: str
    product_name: Optional[str] = None
    brand_name: Optional[str] = None
    image_url: Optional[str] = None
    ingredient_text: Optional[str] = None
    ingredient_coverage_status: IngredientCoverageStatus = "unknown"
    source: str
    created_at: datetime
    updated_at: datetime
    latest_assessment_status: Optional[IngredientCheckStatus] = None
    latest_assessment_explanation: Optional[str] = None
    latest_matched_ingredient_summary: Optional[str] = None
    latest_scan_created_at: Optional[datetime] = None


class SavedProductsResponse(BaseModel):
    items: List[SavedProductEntry] = Field(default_factory=list)
