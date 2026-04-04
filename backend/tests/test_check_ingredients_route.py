from sqlmodel import Session, select

from app.api.routes.check_ingredients import check_ingredients
from app.db.session import get_engine
from app.models import AllergyProfileRecord, ScanHistory
from app.schemas.ingredients import IngredientCheckRequest
from app.services.persistence import prepare_persistence


def test_check_ingredients_route_preserves_legacy_behavior_without_profile():
    response = check_ingredients(
        IngredientCheckRequest(
            ingredient_text="Water, Glycerin, Prunus Amygdalus Dulcis Oil",
        )
    )

    assert response["status"] == "contains_nut_ingredient"
    assert len(response["matched_ingredients"]) == 1
    assert response["matched_ingredients"][0]["nut_source"] == "almond"


def test_check_ingredients_route_filters_by_allergy_profile():
    response = check_ingredients(
        IngredientCheckRequest(
            ingredient_text="Water, Prunus Amygdalus Dulcis Oil, Argania Spinosa Kernel Oil",
            allergy_profile={"argan": True},
        )
    )

    assert response["status"] == "contains_nut_ingredient"
    assert len(response["matched_ingredients"]) == 1
    assert response["matched_ingredients"][0]["nut_source"] == "argan"


def test_check_ingredients_route_persists_scan_history(temp_database):
    assert prepare_persistence() is True

    response = check_ingredients(
        IngredientCheckRequest(
            ingredient_text="Water, Glycerin, Prunus Amygdalus Dulcis Oil",
            allergy_profile={"almond": True},
        )
    )

    with Session(get_engine()) as session:
        scan_history = session.exec(select(ScanHistory)).all()
        allergy_profiles = session.exec(select(AllergyProfileRecord)).all()

    assert response["status"] == "contains_nut_ingredient"
    assert len(scan_history) == 1
    assert scan_history[0].result_status == "contains_nut_ingredient"
    assert scan_history[0].submitted_ingredient_text == "Water, Glycerin, Prunus Amygdalus Dulcis Oil"
    assert len(scan_history[0].matched_ingredients) == 1
    assert len(allergy_profiles) == 1
    assert allergy_profiles[0].almond is True
