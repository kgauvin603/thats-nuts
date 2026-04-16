from dataclasses import dataclass
from typing import Optional, Tuple


RULESET_VERSION = "2026.04.1"


@dataclass(frozen=True)
class AllergenRule:
    key: str
    aliases: Tuple[str, ...]
    category: str
    notes: Optional[str] = None


@dataclass(frozen=True)
class PossibleRule:
    label: str
    aliases: Tuple[str, ...]
    confidence: str
    reason: str


ALLERGEN_RULES: Tuple[AllergenRule, ...] = (
    AllergenRule(
        key="peanut",
        aliases=("peanut", "peanut oil", "arachis hypogaea", "arachis hypogaea oil"),
        category="legume",
    ),
    AllergenRule(
        key="almond",
        aliases=(
            "almond",
            "almond oil",
            "sweet almond oil",
            "prunus amygdalus",
            "prunus amygdalus dulcis",
            "prunus amygdalus dulcis oil",
            "prunus dulcis",
            "prunus dulcis oil",
        ),
        category="tree_nut",
    ),
    AllergenRule(
        key="walnut",
        aliases=(
            "walnut",
            "walnut oil",
            "walnut seed oil",
            "walnut shell powder",
            "juglans regia",
            "juglans regia seed oil",
            "juglans regia kernel oil",
        ),
        category="tree_nut",
    ),
    AllergenRule(
        key="cashew",
        aliases=(
            "cashew",
            "cashew oil",
            "cashew nut oil",
            "anacardium occidentale",
            "anacardium occidentale seed oil",
        ),
        category="tree_nut",
    ),
    AllergenRule(
        key="pistachio",
        aliases=(
            "pistachio",
            "pistachio oil",
            "pistacia vera",
            "pistacia vera seed oil",
        ),
        category="tree_nut",
    ),
    AllergenRule(
        key="hazelnut",
        aliases=(
            "hazelnut",
            "hazelnut oil",
            "hazelnut seed oil",
            "corylus avellana",
            "corylus avellana seed oil",
            "corylus avellana kernel oil",
        ),
        category="tree_nut",
    ),
    AllergenRule(
        key="macadamia",
        aliases=(
            "macadamia",
            "macadamia oil",
            "macadamia seed oil",
            "macadamia integrifolia",
            "macadamia integrifolia seed oil",
            "macadamia tetraphylla",
            "macadamia tetraphylla seed oil",
            "macadamia ternifolia",
            "macadamia ternifolia seed oil",
        ),
        category="tree_nut",
    ),
    AllergenRule(
        key="brazil_nut",
        aliases=(
            "brazil nut",
            "brazil nut oil",
            "bertholletia excelsa",
            "bertholletia excelsa seed oil",
        ),
        category="tree_nut",
    ),
    AllergenRule(
        key="pecan",
        aliases=("pecan", "pecan oil", "carya illinoinensis", "carya illinoinensis oil"),
        category="tree_nut",
    ),
    AllergenRule(
        key="coconut",
        aliases=("coconut", "coconut oil", "cocos nucifera", "cocos nucifera oil"),
        category="tree_nut",
        notes="Included because coconut is part of the current supported allergy profile scope.",
    ),
    AllergenRule(
        key="shea",
        aliases=("shea", "shea butter", "butyrospermum parkii", "butyrospermum parkii butter"),
        category="seed_or_kernel",
    ),
    AllergenRule(
        key="argan",
        aliases=("argan", "argan oil", "argania spinosa", "argania spinosa kernel oil"),
        category="seed_or_kernel",
    ),
    AllergenRule(
        key="kukui",
        aliases=("kukui", "kukui nut", "aleurites moluccanus", "aleurites moluccanus seed oil"),
        category="seed_or_kernel",
    ),
)


POSSIBLE_RULES: Tuple[PossibleRule, ...] = (
    PossibleRule(
        label="botanical oil blend",
        aliases=("botanical oil blend", "nutrient oil blend"),
        confidence="medium",
        reason="Blend naming is too generic to verify botanical source with confidence.",
    ),
    PossibleRule(
        label="vegetable oil",
        aliases=("vegetable oil", "plant oil"),
        confidence="possible",
        reason="Generic oil naming may hide peanut or tree nut oils, but the source is unspecified.",
    ),
)
