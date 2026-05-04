import re
from typing import Optional

from app.schemas.ingredients import AllergyProfile
from app.services.ingredient_detection import detect_ingredient_text

CANNOT_VERIFY_STATUS = "cannot_verify"
CONTAINS_STATUS = "contains_nut_ingredient"
POSSIBLE_STATUS = "possible_nut_derived_ingredient"

NONE_STATUS = "no_nut_ingredient_found"

BLANK_OR_UNUSABLE_EXPLANATION = (
    "A full, usable ingredient list is required to verify this product safely."
)
AMBIGUOUS_EXPLANATION = (
    "The available ingredient list is too vague to verify safely. A full, usable ingredient list is required."
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


def _nut_source_label(nut_source: str) -> str:
    return nut_source.replace("_", " ")


def _clean_display_name(
    value: str,
    *,
    normalized_name: str,
    nut_source: str,
) -> str:
    cleaned = re.sub(r"\s+", " ", value).strip(" \t\r\n,;:.[]{}")
    while cleaned.count("(") > cleaned.count(")"):
        if "(" not in cleaned:
            break
        cleaned = cleaned.rsplit("(", 1)[0].rstrip(" ,;:-")
    while cleaned.count(")") > cleaned.count("("):
        cleaned = cleaned.replace(")", "", 1)
    cleaned = cleaned.strip(" \t\r\n,;:.()[]{}")

    trailing_parenthetical = re.search(r"\(([^()]*)\)\s*$", cleaned)
    if trailing_parenthetical:
        inner = trailing_parenthetical.group(1).strip().lower()
        normalized = normalized_name.strip().lower()
        nut_label = _nut_source_label(nut_source).lower()
        if inner in {normalized, nut_label}:
            cleaned = cleaned[: trailing_parenthetical.start()].rstrip(" ,;:-")

    return cleaned or value.strip()


def _display_name(original_text: str, normalized_name: str, nut_source: str) -> str:
    original = original_text.strip()
    if original:
        return _clean_display_name(
            original,
            normalized_name=normalized_name,
            nut_source=nut_source,
        )

    normalized = normalized_name.strip()
    if normalized:
        return normalized

    return _nut_source_label(nut_source)


def _matched_label(match: dict) -> str:
    return match.get("display_name") or match.get("original_text") or match.get("normalized_name") or _nut_source_label(match["nut_source"])


def _indefinite_article(value: str) -> str:
    return "an" if value[:1].lower() in {"a", "e", "i", "o", "u"} else "a"


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
                    "display_name": _display_name(
                        match.original_text,
                        match.normalized_name,
                        match.key,
                    ),
                    "reason": (
                        f"Matched to known {_nut_source_label(match.key)}-linked ingredient terms: "
                        f"{', '.join(match.matched_terms)}."
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
                    "display_name": _display_name(
                        ingredient_possible_match.original_text,
                        ingredient_possible_match.normalized_name,
                        "unknown",
                    ),
                    "reason": ingredient_possible_match.reason,
                }
            )

    if direct_matches:
        count = len(direct_matches)
        matched_descriptions = ", ".join(_matched_label(match) for match in direct_matches[:3])
        first_nut_source = _nut_source_label(direct_matches[0]["nut_source"])
        return {
            "status": CONTAINS_STATUS,
            "matched_ingredients": direct_matches,
            "explanation": (
                f"Detected {_indefinite_article(first_nut_source)} {first_nut_source}-linked ingredient in this product: {matched_descriptions}."
                if count == 1
                else f"Detected {count} nut-linked ingredients in this product: {matched_descriptions}."
            ),
            "ruleset_version": detection_result.ruleset_version,
            "unknown_terms": list(detection_result.unknown_terms),
        }

    if possible_matches:
        count = len(possible_matches)
        matched_descriptions = ", ".join(_matched_label(match) for match in possible_matches[:3])
        return {
            "status": POSSIBLE_STATUS,
            "matched_ingredients": possible_matches,
            "explanation": (
                f"One ingredient may be nut-derived or too generic to verify confidently: {matched_descriptions}."
                if count == 1
                else f"{count} ingredients may be nut-derived or too generic to verify confidently: {matched_descriptions}."
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
        "explanation": "No nut-linked ingredients were identified in the ingredient list provided.",
        "ruleset_version": detection_result.ruleset_version,
        "unknown_terms": list(detection_result.unknown_terms),
    }
