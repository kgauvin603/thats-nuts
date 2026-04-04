from app.schemas.ingredients import AllergyProfile, IngredientCheckRequest, IngredientCheckResponse
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


def test_returns_possible_for_generic_vegetable_oil():
    result = check_ingredient_text("Water, Vegetable Oil, Glycerin")
    assert result["status"] == "possible_nut_derived_ingredient"
    assert len(result["matched_ingredients"]) == 1
    assert result["matched_ingredients"][0]["confidence"] == "possible"


def test_preserves_legacy_behavior_when_no_profile_is_provided():
    result = check_ingredient_text("Water, Glycerin, Prunus Amygdalus Dulcis Oil")
    assert result["status"] == "contains_nut_ingredient"
    assert result["matched_ingredients"][0]["nut_source"] == "almond"


def test_filters_out_non_relevant_ingredients_for_specific_profile():
    result = check_ingredient_text(
        "Water, Prunus Amygdalus Dulcis Oil, Argania Spinosa Kernel Oil",
        allergy_profile=AllergyProfile(peanut=True),
    )
    assert result["status"] == "no_nut_ingredient_found"
    assert result["matched_ingredients"] == []


def test_matches_direct_ingredient_for_specific_profile():
    result = check_ingredient_text(
        "Water, Prunus Amygdalus Dulcis Oil, Argania Spinosa Kernel Oil",
        allergy_profile=AllergyProfile(argan=True),
    )
    assert result["status"] == "contains_nut_ingredient"
    assert len(result["matched_ingredients"]) == 1
    assert result["matched_ingredients"][0]["nut_source"] == "argan"


def test_tree_nuts_profile_matches_tree_nut_ingredients():
    result = check_ingredient_text(
        "Water, Prunus Amygdalus Dulcis Oil, Glycerin",
        allergy_profile=AllergyProfile(tree_nuts=True),
    )
    assert result["status"] == "contains_nut_ingredient"
    assert len(result["matched_ingredients"]) == 1
    assert result["matched_ingredients"][0]["nut_source"] == "almond"


def test_possible_unknown_match_requires_some_selected_profile():
    result = check_ingredient_text(
        "Water, Botanical Oil Blend, Glycerin",
        allergy_profile=AllergyProfile(),
    )
    assert result["status"] == "no_nut_ingredient_found"
    assert result["matched_ingredients"] == []


def test_possible_unknown_match_is_retained_for_relevant_profile():
    result = check_ingredient_text(
        "Water, Botanical Oil Blend, Glycerin",
        allergy_profile=AllergyProfile(tree_nuts=True),
    )
    assert result["status"] == "possible_nut_derived_ingredient"
    assert len(result["matched_ingredients"]) == 1
    assert result["matched_ingredients"][0]["nut_source"] == "unknown"


def test_direct_match_takes_priority_over_possible_match():
    result = check_ingredient_text(
        "Water, Botanical Oil Blend, Prunus Amygdalus Dulcis Oil, Glycerin"
    )
    assert result["status"] == "contains_nut_ingredient"
    assert len(result["matched_ingredients"]) == 1
    assert result["matched_ingredients"][0]["normalized_name"] == "prunus amygdalus dulcis oil"


def test_response_model_accepts_possible_status():
    response = IngredientCheckResponse(
        status="possible_nut_derived_ingredient",
        matched_ingredients=[
            {
                "original_text": "Vegetable Oil",
                "normalized_name": "vegetable oil",
                "nut_source": "unknown",
                "confidence": "possible",
                "reason": "Generic oil naming may hide peanut or tree nut oils, but the source is unspecified",
            }
        ],
        explanation="Matched 1 ingredient that may be nut-derived or too generic to verify confidently.",
    )
    assert response.status == "possible_nut_derived_ingredient"


def test_request_model_accepts_optional_allergy_profile():
    payload = IngredientCheckRequest(
        ingredient_text="Water, Prunus Amygdalus Dulcis Oil",
        allergy_profile={"almond": True},
    )
    assert payload.allergy_profile is not None
    assert payload.allergy_profile.almond is True


def test_returns_cannot_verify_for_blank_input():
    result = check_ingredient_text("   ")
    assert result["status"] == "cannot_verify"
    assert (
        result["explanation"]
        == "The ingredient input could not be verified because it was blank, incomplete, or not usable "
        "as an ingredient list."
    )


def test_returns_cannot_verify_for_placeholder_input():
    result = check_ingredient_text("N/A")
    assert result["status"] == "cannot_verify"
    assert (
        result["explanation"]
        == "The ingredient input could not be verified because it was blank, incomplete, or not usable "
        "as an ingredient list."
    )


def test_returns_cannot_verify_for_punctuation_only_input():
    result = check_ingredient_text("??? , !!!")
    assert result["status"] == "cannot_verify"
    assert (
        result["explanation"]
        == "The ingredient input could not be verified because it was blank, incomplete, or not usable "
        "as an ingredient list."
    )


def test_returns_cannot_verify_for_all_ambiguous_input():
    result = check_ingredient_text("Fragrance, Parfum")
    assert result["status"] == "cannot_verify"
    assert result["explanation"] == (
        "The ingredient input could not be verified because every parsed ingredient was too vague "
        "to assess confidently."
    )
