from typing import List

from pydantic import BaseModel, Field


class IngredientCheckRequest(BaseModel):
    ingredient_text: str = Field(..., min_length=1)


class MatchedIngredient(BaseModel):
    original_text: str
    normalized_name: str
    nut_source: str
    confidence: str
    reason: str


class IngredientCheckResponse(BaseModel):
    status: str
    matched_ingredients: List[MatchedIngredient]
    explanation: str
