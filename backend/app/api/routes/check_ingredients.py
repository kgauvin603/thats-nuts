from fastapi import APIRouter

from app.schemas.ingredients import IngredientCheckRequest, IngredientCheckResponse
from app.services.persistence import persist_scan_result
from app.services.rules_engine import check_ingredient_text

router = APIRouter()


@router.post("/check-ingredients", response_model=IngredientCheckResponse)
def check_ingredients(payload: IngredientCheckRequest) -> dict:
    result = check_ingredient_text(
        payload.ingredient_text,
        allergy_profile=payload.allergy_profile,
    )
    persist_scan_result(
        payload.ingredient_text,
        result,
        allergy_profile=payload.allergy_profile,
    )
    return result
