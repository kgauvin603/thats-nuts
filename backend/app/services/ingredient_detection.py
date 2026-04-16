import logging
import re
from collections import defaultdict
from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, Iterable, List, Optional, Tuple

from app.services.detection_rules import (
    ALLERGEN_RULES,
    POSSIBLE_RULES,
    RULESET_VERSION,
    AllergenRule,
    PossibleRule,
)
from app.services.ingredient_parser import normalize_text, parse_ingredients

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class IngredientAllergenMatch:
    key: str
    original_text: str
    normalized_name: str
    matched_terms: Tuple[str, ...]
    category: str
    notes: Optional[str] = None


@dataclass(frozen=True)
class PossibleIngredientMatch:
    label: str
    original_text: str
    normalized_name: str
    matched_terms: Tuple[str, ...]
    confidence: str
    reason: str


@dataclass(frozen=True)
class MatchedAllergen:
    key: str
    matched_terms: Tuple[str, ...]
    category: str
    notes: Optional[str] = None


@dataclass(frozen=True)
class IngredientDetectionResult:
    ruleset_version: str
    normalized_text: str
    detected: bool
    status: str
    matched_allergens: Tuple[MatchedAllergen, ...]
    ingredient_matches: Tuple[IngredientAllergenMatch, ...]
    possible_matches: Tuple[PossibleIngredientMatch, ...]
    parsed_ingredients: Tuple[dict, ...]

    def to_dict(self) -> dict:
        return {
            "ruleset_version": self.ruleset_version,
            "normalized_text": self.normalized_text,
            "detected": self.detected,
            "status": self.status,
            "matched_allergens": [
                {
                    "key": match.key,
                    "matched_terms": list(match.matched_terms),
                    "category": match.category,
                    "notes": match.notes,
                }
                for match in self.matched_allergens
            ],
        }


def detect_ingredient_text(ingredient_text: str) -> IngredientDetectionResult:
    normalized_text = normalize_text(ingredient_text or "")
    parsed_ingredients = tuple(parse_ingredients(ingredient_text)) if ingredient_text else ()

    ingredient_matches: List[IngredientAllergenMatch] = []
    possible_matches: List[PossibleIngredientMatch] = []
    matched_terms_by_key: Dict[str, set[str]] = defaultdict(set)
    matched_category_by_key: Dict[str, str] = {}
    matched_notes_by_key: Dict[str, Optional[str]] = {}

    for ingredient in parsed_ingredients:
        normalized_name = ingredient["normalized_name"]
        if ingredient["is_unusable"]:
            continue

        direct_matches = _match_allergen_rules(normalized_name)
        if direct_matches:
            for rule, matched_terms in direct_matches:
                ingredient_matches.append(
                    IngredientAllergenMatch(
                        key=rule.key,
                        original_text=ingredient["original_text"],
                        normalized_name=normalized_name,
                        matched_terms=matched_terms,
                        category=rule.category,
                        notes=rule.notes,
                    )
                )
                matched_terms_by_key[rule.key].update(matched_terms)
                matched_category_by_key[rule.key] = rule.category
                matched_notes_by_key[rule.key] = rule.notes
            continue

        possible_match = _match_possible_rule(normalized_name)
        if possible_match is not None:
            rule, matched_terms = possible_match
            possible_matches.append(
                PossibleIngredientMatch(
                    label=rule.label,
                    original_text=ingredient["original_text"],
                    normalized_name=normalized_name,
                    matched_terms=matched_terms,
                    confidence=rule.confidence,
                    reason=rule.reason,
                )
            )

    matched_allergens = tuple(
        MatchedAllergen(
            key=key,
            matched_terms=tuple(sorted(matched_terms_by_key[key])),
            category=matched_category_by_key[key],
            notes=matched_notes_by_key[key],
        )
        for key in sorted(matched_terms_by_key.keys())
    )
    detected = bool(matched_allergens)
    result = IngredientDetectionResult(
        ruleset_version=RULESET_VERSION,
        normalized_text=normalized_text,
        detected=detected,
        status="nut_detected" if detected else "clear",
        matched_allergens=matched_allergens,
        ingredient_matches=tuple(ingredient_matches),
        possible_matches=tuple(possible_matches),
        parsed_ingredients=parsed_ingredients,
    )
    logger.info(
        "ingredient detection invoked ruleset=%s detected=%s matched_keys=%s",
        result.ruleset_version,
        result.detected,
        [match.key for match in result.matched_allergens],
    )
    return result


def _match_allergen_rules(
    normalized_name: str,
) -> List[Tuple[AllergenRule, Tuple[str, ...]]]:
    matches: List[Tuple[AllergenRule, Tuple[str, ...]]] = []
    for rule in _normalized_allergen_rules():
        matched_terms = _find_matching_terms(normalized_name, rule.aliases)
        if matched_terms:
            matches.append((rule, matched_terms))
    return matches


def _match_possible_rule(
    normalized_name: str,
) -> Optional[Tuple[PossibleRule, Tuple[str, ...]]]:
    for rule in _normalized_possible_rules():
        matched_terms = _find_matching_terms(normalized_name, rule.aliases)
        if matched_terms:
            return rule, matched_terms
    return None


def _find_matching_terms(normalized_text: str, aliases: Iterable[str]) -> Tuple[str, ...]:
    matches = []
    for alias in aliases:
        if _contains_phrase(normalized_text, alias):
            matches.append(alias)
    if not matches:
        return ()
    return tuple(sorted(set(matches), key=lambda value: (-len(value), value)))


def _contains_phrase(normalized_text: str, phrase: str) -> bool:
    return re.search(rf"(^|\s){re.escape(phrase)}($|\s)", normalized_text) is not None


@lru_cache(maxsize=1)
def _normalized_allergen_rules() -> Tuple[AllergenRule, ...]:
    return tuple(
        AllergenRule(
            key=rule.key,
            aliases=tuple(normalize_text(alias) for alias in rule.aliases),
            category=rule.category,
            notes=rule.notes,
        )
        for rule in ALLERGEN_RULES
    )


@lru_cache(maxsize=1)
def _normalized_possible_rules() -> Tuple[PossibleRule, ...]:
    return tuple(
        PossibleRule(
            label=rule.label,
            aliases=tuple(normalize_text(alias) for alias in rule.aliases),
            confidence=rule.confidence,
            reason=rule.reason,
        )
        for rule in POSSIBLE_RULES
    )
