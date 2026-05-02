import re
import unicodedata
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

UNUSABLE_TERMS = {
    "n/a",
    "na",
    "none",
    "unknown",
    "not provided",
    "not available",
    "ingredients unavailable",
    "see packaging",
    "see package",
    "see label",
}


def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(character for character in value if not unicodedata.combining(character))
    value = value.lower().strip()
    value = re.sub(r"\binci\s*:", " ", value)
    value = re.sub(r"\bn\s*/\s*a\b", "na", value)
    value = re.sub(r"\([^)]*\)", "", value)
    value = re.sub(r"[^a-z0-9\s/-]", " ", value)
    value = value.replace("/", " ")
    value = value.replace("-", " ")
    value = re.sub(r"\s+", " ", value).strip()
    return value


def split_ingredients(ingredient_text: str) -> List[str]:
    normalized_input = ingredient_text.replace("\r", "\n")
    raw_parts = re.split(r"[,;\n]+", normalized_input)
    return [part.strip() for part in raw_parts if part.strip()]


def is_unusable_term(normalized_value: str) -> bool:
    return not normalized_value or normalized_value in UNUSABLE_TERMS


def parse_ingredients(ingredient_text: str) -> List[dict]:
    ingredients = split_ingredients(ingredient_text)
    parsed = []
    for ingredient in ingredients:
        normalized = normalize_text(ingredient)
        parsed.append(
            {
                "original_text": ingredient,
                "normalized_name": normalized,
                "is_ambiguous": normalized in AMBIGUOUS_TERMS,
                "is_unusable": is_unusable_term(normalized),
            }
        )
    return parsed
