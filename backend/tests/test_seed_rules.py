from app.services.seed_rules import (
    CONTAINS_STATUS,
    POSSIBLE_STATUS,
    SeedIngredientRule,
    SeedRuleSet,
)


def test_seed_rule_derives_status_from_confidence_when_missing():
    rule = SeedIngredientRule.from_dict(
        {
            "aliases": ["sweet almond oil"],
            "nut_source": "almond",
            "confidence": "high",
            "reason": "Known almond-derived cosmetic ingredient",
        }
    )
    assert rule.status == CONTAINS_STATUS


def test_seed_rule_set_indexes_aliases_and_keeps_explicit_status():
    rule_set = SeedRuleSet.from_payload(
        [
            {
                "aliases": ["vegetable oil", "plant oil"],
                "nut_source": "unknown",
                "confidence": "possible",
                "status": POSSIBLE_STATUS,
                "reason": "Generic oil naming may hide peanut or tree nut oils, but the source is unspecified",
            }
        ]
    )
    matched_rule = rule_set.find_by_alias("plant oil")
    assert matched_rule is not None
    assert matched_rule.status == POSSIBLE_STATUS
