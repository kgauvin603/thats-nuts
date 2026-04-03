import json
from pathlib import Path
from typing import Dict, List

from app.services.ingredient_parser import parse_ingredients

SEED_PATH = Path(__file__).resolve().parent.parent / "data" / "nut_ingredients_seed.json"


CONTAINS_STATUS = "contains_nut_ingredient"
POSSIBLE_STATUS = "possible_nut_derived_ingredient"
NONE_STATUS = "no_nut_ingredient_found"
CANNOT_VERIFY_STATUS = "cannot_verify"


def load_seed_rules() -> List[Dict]:
    with open(SEED_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def check_ingredient_text(ingredient_text: str) -> dict:
    if not ingredient_text or not ingredient_text.strip():
        return {
            "status": CANNOT_VERIFY_STATUS,
            "matched_ingredients": [],
            "explanation": "No ingredient text was provided.",
        }

    parsed = parse_ingredients(ingredient_text)
    if not parsed:
        return {
            "status": CANNOT_VERIFY_STATUS,
            "matched_ingredients": [],
            "explanation": "The ingredient list could not be parsed.",
        }

    rules = load_seed_rules()
    direct_matches = []
    possible_matches = []
    ambiguous_count = 0

    for ingredient in parsed:
        normalized = ingredient["normalized_name"]
        if ingredient["is_ambiguous"]:
            ambiguous_count += 1

        for rule in rules:
            if normalized in rule["aliases"]:
                match = {
                    "original_text": ingredient["original_text"],
                    "normalized_name": normalized,
                    "nut_source": rule["nut_source"],
                    "confidence": rule["confidence"],
                    "reason": rule["reason"],
                }
                if rule["confidence"] == "high":
                    direct_matches.append(match)
                else:
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

    if ambiguous_count and len(parsed) <= ambiguous_count:
        return {
            "status": CANNOT_VERIFY_STATUS,
            "matched_ingredients": [],
            "explanation": "The ingredient list is too ambiguous to verify confidently.",
        }

    return {
        "status": NONE_STATUS,
        "matched_ingredients": [],
        "explanation": "No nut-derived ingredients were matched in the provided ingredient list.",
    }
