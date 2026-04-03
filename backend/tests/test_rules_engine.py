from app.services.rules_engine import check_ingredient_text


def test_detects_almond_oil():
    result = check_ingredient_text("Water, Glycerin, Prunus Amygdalus Dulcis Oil, Fragrance")
    assert result["status"] == "contains_nut_ingredient"
    assert len(result["matched_ingredients"]) == 1
    assert result["matched_ingredients"][0]["nut_source"] == "almond"


def test_returns_no_match_for_simple_non_nut_list():
    result = check_ingredient_text("Water, Glycerin, Cetyl Alcohol, Fragrance")
    assert result["status"] == "no_nut_ingredient_found"
    assert result["matched_ingredients"] == []


def test_returns_possible_for_generic_oil_blend():
    result = check_ingredient_text("Water, Botanical Oil Blend, Glycerin")
    assert result["status"] == "possible_nut_derived_ingredient"
    assert len(result["matched_ingredients"]) == 1
    assert result["matched_ingredients"][0]["confidence"] == "medium"


def test_returns_cannot_verify_for_blank_input():
    result = check_ingredient_text("   ")
    assert result["status"] == "cannot_verify"
