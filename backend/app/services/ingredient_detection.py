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
    DetectionAlias,
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
    detection_basis: str
    match_strength: str
    review_recommended: bool
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
    detection_basis: str
    match_strength: str
    review_recommended: bool
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
    unknown_terms: Tuple[str, ...]

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
                    "detection_basis": match.detection_basis,
                    "match_strength": match.match_strength,
                    "review_recommended": match.review_recommended,
                    "category": match.category,
                    "notes": match.notes,
                }
                for match in self.matched_allergens
            ],
            "unknown_terms": list(self.unknown_terms),
        }


def detect_ingredient_text(ingredient_text: str) -> IngredientDetectionResult:
    normalized_text = normalize_text(ingredient_text or "")
    parsed_ingredients = tuple(parse_ingredients(ingredient_text)) if ingredient_text else ()

    ingredient_matches: List[IngredientAllergenMatch] = []
    possible_matches: List[PossibleIngredientMatch] = []
    matched_terms_by_key: Dict[str, set[str]] = defaultdict(set)
    matched_basis_by_key: Dict[str, set[str]] = defaultdict(set)
    matched_category_by_key: Dict[str, str] = {}
    matched_notes_by_key: Dict[str, Optional[str]] = {}
    unknown_terms: List[str] = []

    for ingredient in parsed_ingredients:
        normalized_name = ingredient["normalized_name"]
        if ingredient["is_unusable"] or ingredient["is_ambiguous"]:
            continue

        direct_matches = _match_allergen_rules(normalized_name)
        if direct_matches:
            for rule, matched_aliases in direct_matches:
                matched_terms = tuple(alias.term for alias in matched_aliases)
                detection_basis = _detection_basis(matched_aliases)
                match_strength = _match_strength(normalized_name, matched_aliases)
                review_recommended = detection_basis != "common_name"
                ingredient_matches.append(
                    IngredientAllergenMatch(
                        key=rule.key,
                        original_text=ingredient["original_text"],
                        normalized_name=normalized_name,
                        matched_terms=matched_terms,
                        detection_basis=detection_basis,
                        match_strength=match_strength,
                        review_recommended=review_recommended,
                        category=rule.category,
                        notes=rule.notes,
                    )
                )
                matched_terms_by_key[rule.key].update(matched_terms)
                matched_basis_by_key[rule.key].update(alias.basis for alias in matched_aliases)
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
            continue

        unknown_candidate = _unknown_term_candidate(normalized_name)
        if unknown_candidate is not None:
            unknown_terms.append(unknown_candidate)

    matched_allergens = tuple(
        MatchedAllergen(
            key=key,
            matched_terms=tuple(sorted(matched_terms_by_key[key])),
            detection_basis=_aggregate_detection_basis(matched_basis_by_key[key]),
            match_strength=_aggregate_match_strength(
                tuple(
                    match.match_strength
                    for match in ingredient_matches
                    if match.key == key
                )
            ),
            review_recommended=_aggregate_detection_basis(matched_basis_by_key[key]) != "common_name",
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
        unknown_terms=tuple(sorted(set(unknown_terms), key=lambda value: (-len(value), value))),
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
) -> List[Tuple[AllergenRule, Tuple[DetectionAlias, ...]]]:
    matches: List[Tuple[AllergenRule, Tuple[DetectionAlias, ...]]] = []
    for rule in _normalized_allergen_rules():
        matched_terms = _find_matching_terms(normalized_name, rule.aliases)
        matched_terms = _filter_contextual_overbroad_aliases(
            normalized_name,
            rule.key,
            matched_terms,
        )
        if matched_terms:
            matches.append((rule, matched_terms))
    return matches


def _match_possible_rule(
    normalized_name: str,
) -> Optional[Tuple[PossibleRule, Tuple[str, ...]]]:
    for rule in _normalized_possible_rules():
        matched_terms = _find_matching_text_terms(normalized_name, rule.aliases)
        if matched_terms:
            return rule, matched_terms
    return None


def _find_matching_terms(
    normalized_text: str,
    aliases: Iterable[DetectionAlias],
) -> Tuple[DetectionAlias, ...]:
    matches: List[DetectionAlias] = []
    for alias in aliases:
        if _contains_phrase(normalized_text, alias.term):
            matches.append(alias)
    if not matches:
        return ()
    unique = {
        (alias.term, alias.basis): alias
        for alias in matches
    }
    return tuple(
        sorted(unique.values(), key=lambda value: (-len(value.term), value.term, value.basis))
    )


def _find_matching_text_terms(
    normalized_text: str,
    aliases: Iterable[str],
) -> Tuple[str, ...]:
    matches: List[str] = []
    for alias in aliases:
        if _contains_phrase(normalized_text, alias):
            matches.append(alias)
    if not matches:
        return ()
    return tuple(sorted(set(matches), key=lambda value: (-len(value), value)))


def _contains_phrase(normalized_text: str, phrase: str) -> bool:
    return re.search(rf"(^|\s){re.escape(phrase)}($|\s)", normalized_text) is not None


def _filter_contextual_overbroad_aliases(
    normalized_text: str,
    rule_key: str,
    matched_aliases: Tuple[DetectionAlias, ...],
) -> Tuple[DetectionAlias, ...]:
    if rule_key != "walnut":
        return matched_aliases

    blocked_contexts = (
        "noix de cajou",
        "noix de pecan",
        "noix du bresil",
        "noix de macadamia",
        "nuez de macadamia",
        "nueces de macadamia",
        "nuez de brasil",
        "nueces de brasil",
        "nuez pecana",
        "nueces pecanas",
        "noce pecan",
        "noci pecan",
        "noce di macadamia",
        "noci di macadamia",
        "noce del brasile",
        "noci del brasile",
    )
    if not any(_contains_phrase(normalized_text, context) for context in blocked_contexts):
        return matched_aliases

    overbroad_terms = {"noix", "nuez", "nueces", "noce", "noci"}
    return tuple(alias for alias in matched_aliases if alias.term not in overbroad_terms)


def _detection_basis(matched_aliases: Tuple[DetectionAlias, ...]) -> str:
    bases = {alias.basis for alias in matched_aliases}
    return _aggregate_detection_basis(bases)


def _aggregate_detection_basis(bases: Iterable[str]) -> str:
    basis_set = set(bases)
    if len(basis_set) > 1:
        return "multiple"
    return next(iter(basis_set), "common_name")


def _match_strength(normalized_name: str, matched_aliases: Tuple[DetectionAlias, ...]) -> str:
    if len(matched_aliases) > 1:
        return "multiple_matches"
    alias = matched_aliases[0]
    if normalized_name == alias.term:
        return "exact_alias"
    return "phrase_match"


def _aggregate_match_strength(match_strengths: Tuple[str, ...]) -> str:
    if any(strength == "multiple_matches" for strength in match_strengths) or len(match_strengths) > 1:
        return "multiple_matches"
    if any(strength == "phrase_match" for strength in match_strengths):
        return "phrase_match"
    return "exact_alias"


UNKNOWN_STOP_TERMS = {
    "water",
    "aqua",
    "glycerin",
    "fragrance",
    "parfum",
    "alcohol",
    "cetyl alcohol",
}


def _unknown_term_candidate(normalized_name: str) -> Optional[str]:
    if not normalized_name or normalized_name in UNKNOWN_STOP_TERMS:
        return None
    if len(normalized_name) < 10:
        return None
    if " " not in normalized_name and not _looks_ingredient_like(normalized_name):
        return None
    if not _looks_ingredient_like(normalized_name):
        return None
    return normalized_name


def _looks_ingredient_like(normalized_name: str) -> bool:
    ingredient_markers = (
        "oil",
        "extract",
        "butter",
        "powder",
        "seed",
        "kernel",
        "fruit",
        "leaf",
        "root",
        "flower",
        "resin",
        "protein",
    )
    return any(marker in normalized_name.split() for marker in ingredient_markers) or len(normalized_name.split()) >= 2


@lru_cache(maxsize=1)
def _normalized_allergen_rules() -> Tuple[AllergenRule, ...]:
    return tuple(
        AllergenRule(
            key=rule.key,
            aliases=tuple(
                DetectionAlias(
                    term=normalize_text(alias.term),
                    basis=alias.basis,
                )
                for alias in rule.aliases
            ),
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
