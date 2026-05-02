from typing import Optional

from app.schemas.ingredients import AllergyProfile
from app.services.ingredient_detection import detect_ingredient_text

CANNOT_VERIFY_STATUS = "cannot_verify"
CONTAINS_STATUS = "contains_nut_ingredient"
POSSIBLE_STATUS = "possible_nut_derived_ingredient"

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
    "pine_nut",
    "chestnut",
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

    detection_result = detect_ingredient_text(ingredient_text)
    parsed = detection_result.parsed_ingredients
    if not parsed:
        return cannot_verify_response(BLANK_OR_UNUSABLE_EXPLANATION)

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

        ingredient_direct_matches = [
            match
            for match in detection_result.ingredient_matches
            if match.original_text == ingredient["original_text"]
            and match.normalized_name == normalized
        ]
        for match in ingredient_direct_matches:
            if not profile_matches_rule(allergy_profile, match.key):
                continue
            direct_matches.append(
                {
                    "original_text": match.original_text,
                    "normalized_name": match.normalized_name,
                    "nut_source": match.key,
                    "confidence": "high",
                    "reason": (
                        f'Known {match.key.replace("_", " ")}-derived ingredient '
                        f'matched by ruleset term(s): {", ".join(match.matched_terms)}.'
                    ),
                    "detection_basis": match.detection_basis,
                    "match_strength": match.match_strength,
                    "review_recommended": match.review_recommended,
                }
            )
        if ingredient_direct_matches:
            continue

        ingredient_possible_match = next(
            (
                match
                for match in detection_result.possible_matches
                if match.original_text == ingredient["original_text"]
                and match.normalized_name == normalized
            ),
            None,
        )
        if ingredient_possible_match and profile_matches_rule(allergy_profile, "unknown"):
            possible_matches.append(
                {
                    "original_text": ingredient_possible_match.original_text,
                    "normalized_name": ingredient_possible_match.normalized_name,
                    "nut_source": "unknown",
                    "confidence": ingredient_possible_match.confidence,
                    "reason": ingredient_possible_match.reason,
                }
            )

    if direct_matches:
        count = len(direct_matches)
        matched_descriptions = ", ".join(
            f'{match["original_text"]} ({match["nut_source"].replace("_", " ")})'
            for match in direct_matches[:3]
        )
        return {
            "status": CONTAINS_STATUS,
            "matched_ingredients": direct_matches,
            "explanation": (
                f"Detected {count} nut-linked ingredient: {matched_descriptions}."
                if count == 1
                else f"Detected {count} nut-linked ingredients: {matched_descriptions}."
            ),
            "ruleset_version": detection_result.ruleset_version,
            "unknown_terms": list(detection_result.unknown_terms),
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
            "ruleset_version": detection_result.ruleset_version,
            "unknown_terms": list(detection_result.unknown_terms),
        }

    if len(parsed) == unusable_count:
        return cannot_verify_response(BLANK_OR_UNUSABLE_EXPLANATION)

    if ambiguous_count + unusable_count == len(parsed):
        return cannot_verify_response(AMBIGUOUS_EXPLANATION)

    return {
        "status": NONE_STATUS,
        "matched_ingredients": [],
        "explanation": (
            f"No known nut-linked ingredients from ruleset "
            f"{detection_result.ruleset_version} were detected in the provided ingredient list."
        ),
        "ruleset_version": detection_result.ruleset_version,
        "unknown_terms": list(detection_result.unknown_terms),
    }
