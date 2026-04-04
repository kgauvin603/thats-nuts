from app.api.routes.check_ingredients import check_ingredients
from app.api.routes.product_lookup import lookup_product
from app.api.routes.scan_history import recent_scan_history
from app.schemas.ingredients import IngredientCheckRequest
from app.schemas.products import ProductLookupRequest
from app.services.persistence import prepare_persistence


def test_recent_scan_history_returns_manual_and_barcode_checks(temp_database):
    assert prepare_persistence() is True

    check_ingredients(
        IngredientCheckRequest(
            ingredient_text="Water, Glycerin, Prunus Amygdalus Dulcis Oil",
        )
    )
    lookup_product(ProductLookupRequest(barcode="0001234567890"))

    response = recent_scan_history(limit=10)

    assert len(response.items) == 2

    newest_item = response.items[0]
    older_item = response.items[1]

    assert newest_item.barcode == "0001234567890"
    assert newest_item.scan_type == "barcode_lookup"
    assert newest_item.product_name == "Sample Almond Body Oil"
    assert newest_item.brand_name == "Thats Nuts Labs"
    assert newest_item.assessment_status == "contains_nut_ingredient"
    assert newest_item.matched_ingredient_summary == "Prunus Amygdalus Dulcis Oil"
    assert newest_item.created_at is not None
    assert "Matched 1 ingredient linked to nut allergy risk." in newest_item.explanation

    assert older_item.scan_type == "manual_ingredient_check"
    assert older_item.barcode is None
    assert older_item.product_name is None
    assert older_item.brand_name is None
    assert older_item.assessment_status == "contains_nut_ingredient"
    assert older_item.matched_ingredient_summary == "Prunus Amygdalus Dulcis Oil"
    assert older_item.created_at is not None
    assert older_item.explanation == "Matched 1 ingredient linked to nut allergy risk."


def test_recent_scan_history_respects_limit(temp_database):
    assert prepare_persistence() is True

    check_ingredients(
        IngredientCheckRequest(
            ingredient_text="Water, Glycerin, Prunus Amygdalus Dulcis Oil",
        )
    )
    check_ingredients(
        IngredientCheckRequest(
            ingredient_text="Water, Glycerin",
        )
    )

    response = recent_scan_history(limit=1)

    assert len(response.items) == 1
    assert response.items[0].scan_type == "manual_ingredient_check"
