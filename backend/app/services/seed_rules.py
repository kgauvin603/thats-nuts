import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

SEED_PATH = Path(__file__).resolve().parent.parent / "data" / "nut_ingredients_seed.json"

CONTAINS_STATUS = "contains_nut_ingredient"
POSSIBLE_STATUS = "possible_nut_derived_ingredient"
CANNOT_VERIFY_STATUS = "cannot_verify"

HIGH_CONFIDENCE = "high"
POSSIBLE_CONFIDENCE_LEVELS = {"medium", "possible"}


def status_for_confidence(confidence: str) -> str:
    if confidence == HIGH_CONFIDENCE:
        return CONTAINS_STATUS
    if confidence in POSSIBLE_CONFIDENCE_LEVELS:
        return POSSIBLE_STATUS
    return CANNOT_VERIFY_STATUS


@dataclass(frozen=True)
class SeedIngredientRule:
    aliases: Tuple[str, ...]
    nut_source: str
    confidence: str
    status: str
    reason: str

    @classmethod
    def from_dict(cls, payload: Dict) -> "SeedIngredientRule":
        confidence = payload["confidence"]
        return cls(
            aliases=tuple(payload["aliases"]),
            nut_source=payload["nut_source"],
            confidence=confidence,
            status=payload.get("status", status_for_confidence(confidence)),
            reason=payload["reason"],
        )

    def to_match(self, ingredient: Dict) -> Dict:
        return {
            "original_text": ingredient["original_text"],
            "normalized_name": ingredient["normalized_name"],
            "nut_source": self.nut_source,
            "confidence": self.confidence,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class SeedRuleSet:
    rules: Tuple[SeedIngredientRule, ...]
    alias_lookup: Dict[str, SeedIngredientRule]

    @classmethod
    def from_payload(cls, payload: Iterable[Dict]) -> "SeedRuleSet":
        rules = tuple(SeedIngredientRule.from_dict(item) for item in payload)
        alias_lookup: Dict[str, SeedIngredientRule] = {}
        for rule in rules:
            for alias in rule.aliases:
                alias_lookup[alias] = rule
        return cls(rules=rules, alias_lookup=alias_lookup)

    def find_by_alias(self, normalized_name: str) -> Optional[SeedIngredientRule]:
        return self.alias_lookup.get(normalized_name)


def load_seed_payload(path: Path = SEED_PATH) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def load_seed_rule_set(path: Path = SEED_PATH) -> SeedRuleSet:
    return SeedRuleSet.from_payload(load_seed_payload(path))
