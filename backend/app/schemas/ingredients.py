from typing import List, Literal, Optional

from pydantic import BaseModel, Field

IngredientCheckStatus = Literal[
    "contains_nut_ingredient",
    "possible_nut_derived_ingredient",
    "no_nut_ingredient_found",
    "cannot_verify",
]
IngredientConfidence = Literal["high", "medium", "possible"]
DetectionBasis = Literal["common_name", "inci_name", "multiple"]
MatchStrength = Literal["exact_alias", "phrase_match", "multiple_matches"]


class AllergyProfile(BaseModel):
    peanut: bool = False
    tree_nuts: bool = False
    almond: bool = False
    walnut: bool = False
    cashew: bool = False
    pistachio: bool = False
    hazelnut: bool = False
    macadamia: bool = False
    brazil_nut: bool = False
    pecan: bool = False
    coconut: bool = False
    shea: bool = False
    argan: bool = False
    kukui: bool = False

    def has_selected_allergies(self) -> bool:
        return any(self.model_dump().values())


class IngredientCheckRequest(BaseModel):
    ingredient_text: str = Field(..., min_length=1)
    allergy_profile: Optional[AllergyProfile] = None


class MatchedIngredient(BaseModel):
    original_text: str
    normalized_name: str
    nut_source: str
    confidence: IngredientConfidence
    reason: str
    display_name: Optional[str] = None
    detection_basis: Optional[DetectionBasis] = None
    match_strength: Optional[MatchStrength] = None
    review_recommended: Optional[bool] = None


class IngredientCheckResponse(BaseModel):
    status: IngredientCheckStatus
    matched_ingredients: List[MatchedIngredient]
    explanation: str
    ruleset_version: Optional[str] = None
    unknown_terms: List[str] = Field(default_factory=list)
