from typing import Optional

from app.schemas.ingredients import AllergyProfile
from app.services.ingredient_parser import parse_ingredients
from app.services.seed_rules import (
    CANNOT_VERIFY_STATUS,
    CONTAINS_STATUS,
    POSSIBLE_STATUS,
    load_seed_rule_set,
)

NONE_STATUS = "no_nut_ingredient_found"

BLANK_OR_UNUSABLE_EXPLANATION = (
    "The ingredient input could not be verified because it was blank, incomplete, or not usable "
    "as an ingredient list."
)
AMBIGUOUS_EXPLANATION = (
    "The ingredient input could not be verified because every parsed ingredient was too vague "
    "to assess confidently."
)
TREE_NUT_SOURCES = {
    "almond",
    "walnut",
    "cashew",
    "pistachio",
    "hazelnut",
    "macadamia",
    "brazil_nut",
    "pecan",
}


def cannot_verify_response(explanation: str) -> dict:
    return {
        "status": CANNOT_VERIFY_STATUS,
        "matched_ingredients": [],
        "explanation": explanation,
    }


def profile_matches_rule(profile: Optional[AllergyProfile], nut_source: str) -> bool:
    if profile is None:
        return True

    if nut_source == "unknown":
        return profile.has_selected_allergies()

    if nut_source in TREE_NUT_SOURCES and profile.tree_nuts:
        return True

    return getattr(profile, nut_source, False)


def check_ingredient_text(
    ingredient_text: str,
    allergy_profile: Optional[AllergyProfile] = None,
) -> dict:
    if not ingredient_text or not ingredient_text.strip():
        return cannot_verify_response(BLANK_OR_UNUSABLE_EXPLANATION)

    parsed = parse_ingredients(ingredient_text)
    if not parsed:
        return cannot_verify_response(BLANK_OR_UNUSABLE_EXPLANATION)

    rule_set = load_seed_rule_set()
    direct_matches = []
    possible_matches = []
    ambiguous_count = 0
    unusable_count = 0

    for ingredient in parsed:
        normalized = ingredient["normalized_name"]
        if ingredient["is_ambiguous"]:
            ambiguous_count += 1
        if ingredient["is_unusable"]:
            unusable_count += 1
            continue

        rule = rule_set.find_by_alias(normalized)
        if not rule:
            continue
        if not profile_matches_rule(allergy_profile, rule.nut_source):
            continue

        match = rule.to_match(ingredient)
        match_status = rule.status
        if match_status == CONTAINS_STATUS:
            direct_matches.append(match)
        elif match_status == POSSIBLE_STATUS:
            possible_matches.append(match)

    if direct_matches:
        count = len(direct_matches)
        return {
            "status": CONTAINS_STATUS,
            "matched_ingredients": direct_matches,
            "explanation": (
                f"Matched {count} ingredient linked to nut allergy risk."
                if count == 1
                else f"Matched {count} ingredients linked to nut allergy risk."
            ),
        }

    if possible_matches:
        count = len(possible_matches)
        return {
            "status": POSSIBLE_STATUS,
            "matched_ingredients": possible_matches,
            "explanation": (
                f"Matched {count} ingredient that may be nut-derived or too generic to verify confidently."
                if count == 1
                else f"Matched {count} ingredients that may be nut-derived or too generic to verify confidently."
            ),
        }

    if len(parsed) == unusable_count:
        return cannot_verify_response(BLANK_OR_UNUSABLE_EXPLANATION)

    if ambiguous_count + unusable_count == len(parsed):
        return cannot_verify_response(AMBIGUOUS_EXPLANATION)

    return {
        "status": NONE_STATUS,
        "matched_ingredients": [],
        "explanation": "No nut-derived ingredients were matched in the provided ingredient list.",
    }
