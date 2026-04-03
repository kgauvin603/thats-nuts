from fastapi import APIRouter

from app.schemas.ingredients import IngredientCheckRequest, IngredientCheckResponse
from app.services.rules_engine import check_ingredient_text

router = APIRouter()


@router.post("/check-ingredients", response_model=IngredientCheckResponse)
def check_ingredients(payload: IngredientCheckRequest) -> dict:
    return check_ingredient_text(payload.ingredient_text)
