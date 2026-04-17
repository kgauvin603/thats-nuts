from dataclasses import dataclass
from typing import Optional, Tuple


RULESET_VERSION = "2026.04.1"


@dataclass(frozen=True)
class DetectionAlias:
    term: str
    basis: str


@dataclass(frozen=True)
class AllergenRule:
    key: str
    aliases: Tuple[DetectionAlias, ...]
    category: str
    notes: Optional[str] = None


@dataclass(frozen=True)
class PossibleRule:
    label: str
    aliases: Tuple[str, ...]
    confidence: str
    reason: str


def common_alias(term: str) -> DetectionAlias:
    return DetectionAlias(term=term, basis="common_name")


def inci_alias(term: str) -> DetectionAlias:
    return DetectionAlias(term=term, basis="inci_name")


ALLERGEN_RULES: Tuple[AllergenRule, ...] = (
    AllergenRule(
        key="peanut",
        aliases=(
            common_alias("peanut"),
            common_alias("peanut oil"),
            inci_alias("arachis hypogaea"),
            inci_alias("arachis hypogaea oil"),
        ),
        category="legume",
    ),
    AllergenRule(
        key="almond",
        aliases=(
            common_alias("almond"),
            common_alias("almond oil"),
            common_alias("sweet almond oil"),
            inci_alias("prunus amygdalus"),
            inci_alias("prunus amygdalus dulcis"),
            inci_alias("prunus amygdalus dulcis oil"),
            inci_alias("prunus dulcis"),
            inci_alias("prunus dulcis oil"),
        ),
        category="tree_nut",
    ),
    AllergenRule(
        key="walnut",
        aliases=(
            common_alias("walnut"),
            common_alias("walnut oil"),
            common_alias("walnut seed oil"),
            common_alias("walnut shell powder"),
            inci_alias("juglans regia"),
            inci_alias("juglans regia seed oil"),
            inci_alias("juglans regia kernel oil"),
        ),
        category="tree_nut",
    ),
    AllergenRule(
        key="cashew",
        aliases=(
            common_alias("cashew"),
            common_alias("cashew oil"),
            common_alias("cashew nut oil"),
            inci_alias("anacardium occidentale"),
            inci_alias("anacardium occidentale seed oil"),
        ),
        category="tree_nut",
    ),
    AllergenRule(
        key="pistachio",
        aliases=(
            common_alias("pistachio"),
            common_alias("pistachio oil"),
            inci_alias("pistacia vera"),
            inci_alias("pistacia vera seed oil"),
        ),
        category="tree_nut",
    ),
    AllergenRule(
        key="hazelnut",
        aliases=(
            common_alias("hazelnut"),
            common_alias("hazelnut oil"),
            common_alias("hazelnut seed oil"),
            inci_alias("corylus avellana"),
            inci_alias("corylus avellana seed oil"),
            inci_alias("corylus avellana kernel oil"),
        ),
        category="tree_nut",
    ),
    AllergenRule(
        key="macadamia",
        aliases=(
            common_alias("macadamia"),
            common_alias("macadamia oil"),
            common_alias("macadamia seed oil"),
            inci_alias("macadamia integrifolia"),
            inci_alias("macadamia integrifolia seed oil"),
            inci_alias("macadamia tetraphylla"),
            inci_alias("macadamia tetraphylla seed oil"),
            inci_alias("macadamia ternifolia"),
            inci_alias("macadamia ternifolia seed oil"),
        ),
        category="tree_nut",
    ),
    AllergenRule(
        key="brazil_nut",
        aliases=(
            common_alias("brazil nut"),
            common_alias("brazil nut oil"),
            inci_alias("bertholletia excelsa"),
            inci_alias("bertholletia excelsa seed oil"),
        ),
        category="tree_nut",
    ),
    AllergenRule(
        key="pecan",
        aliases=(
            common_alias("pecan"),
            common_alias("pecan oil"),
            inci_alias("carya illinoinensis"),
            inci_alias("carya illinoinensis oil"),
        ),
        category="tree_nut",
    ),
    AllergenRule(
        key="coconut",
        aliases=(
            common_alias("coconut"),
            common_alias("coconut oil"),
            inci_alias("cocos nucifera"),
            inci_alias("cocos nucifera oil"),
        ),
        category="tree_nut",
        notes="Included because coconut is part of the current supported allergy profile scope.",
    ),
    AllergenRule(
        key="shea",
        aliases=(
            common_alias("shea"),
            common_alias("shea butter"),
            inci_alias("butyrospermum parkii"),
            inci_alias("butyrospermum parkii butter"),
        ),
        category="seed_or_kernel",
    ),
    AllergenRule(
        key="argan",
        aliases=(
            common_alias("argan"),
            common_alias("argan oil"),
            inci_alias("argania spinosa"),
            inci_alias("argania spinosa kernel oil"),
        ),
        category="seed_or_kernel",
    ),
    AllergenRule(
        key="kukui",
        aliases=(
            common_alias("kukui"),
            common_alias("kukui nut"),
            inci_alias("aleurites moluccanus"),
            inci_alias("aleurites moluccanus seed oil"),
        ),
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
