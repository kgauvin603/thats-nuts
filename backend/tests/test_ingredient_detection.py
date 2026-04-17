from app.services.ingredient_detection import detect_ingredient_text
from app.services.ingredient_parser import normalize_text


def test_normalize_text_handles_inci_punctuation_and_whitespace():
    normalized = normalize_text('INCI: "Juglans Regia Seed Oil";\nWater (Aqua)')
    assert normalized == "juglans regia seed oil water"


def test_detection_result_includes_ruleset_and_matches():
    result = detect_ingredient_text("Water, Juglans Regia Seed Oil")

    assert result.ruleset_version == "2026.04.1"
    assert result.detected is True
    assert result.status == "nut_detected"
    assert len(result.matched_allergens) == 1
    assert result.matched_allergens[0].key == "walnut"
    assert "juglans regia" in result.matched_allergens[0].matched_terms
    assert result.matched_allergens[0].detection_basis == "inci_name"
    assert result.matched_allergens[0].match_strength == "multiple_matches"
    assert result.matched_allergens[0].review_recommended is True


def test_detects_multiline_walnut_input():
    result = detect_ingredient_text("Water\nGlycerin\nJuglans Regia Seed Oil")

    assert result.detected is True
    assert {match.key for match in result.matched_allergens} == {"walnut"}


def test_detects_required_direct_cases():
    cases = {
        "Walnut Oil": "walnut",
        "Juglans Regia Seed Oil": "walnut",
        "Prunus Amygdalus Dulcis Oil": "almond",
        "Macadamia Seed Oil": "macadamia",
    }

    for ingredient_text, expected_key in cases.items():
        result = detect_ingredient_text(ingredient_text)
        assert result.detected is True
        assert {match.key for match in result.matched_allergens} == {expected_key}


def test_clear_case_returns_structured_clear_result():
    result = detect_ingredient_text("Glycerin")

    assert result.detected is False
    assert result.status == "clear"
    assert result.matched_allergens == ()
    assert result.unknown_terms == ()


def test_regression_water_glycerin_and_juglans_regia_detects_walnut():
    result = detect_ingredient_text("Water, Glycerin, Juglans Regia Seed Oil")

    assert result.detected is True
    assert {match.key for match in result.matched_allergens} == {"walnut"}


def test_unknown_terms_surface_unmapped_ingredient_like_phrases():
    result = detect_ingredient_text(
        "Water, Glycerin, Orbignya Oleifera Seed Oil, Cetyl Alcohol"
    )

    assert result.detected is False
    assert "orbignya oleifera seed oil" in result.unknown_terms
    assert "glycerin" not in result.unknown_terms
    assert "cetyl alcohol" not in result.unknown_terms


def test_mapped_terms_do_not_appear_in_unknown_terms():
    result = detect_ingredient_text("Water, Walnut Oil, Glycerin")

    assert result.detected is True
    assert "walnut oil" not in result.unknown_terms
