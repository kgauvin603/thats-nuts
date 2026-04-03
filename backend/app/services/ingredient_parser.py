import re
from typing import List


AMBIGUOUS_TERMS = {
    "fragrance",
    "parfum",
    "flavor",
    "aroma",
    "natural extracts",
    "botanical complex",
    "plant lipid concentrate",
}


def normalize_text(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"\([^)]*\)", "", value)
    value = re.sub(r"[^a-z0-9\s/-]", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def split_ingredients(ingredient_text: str) -> List[str]:
    raw_parts = ingredient_text.split(",")
    return [part.strip() for part in raw_parts if part.strip()]


def parse_ingredients(ingredient_text: str) -> List[dict]:
    ingredients = split_ingredients(ingredient_text)
    return [
        {
            "original_text": ingredient,
            "normalized_name": normalize_text(ingredient),
            "is_ambiguous": normalize_text(ingredient) in AMBIGUOUS_TERMS,
        }
        for ingredient in ingredients
    ]
