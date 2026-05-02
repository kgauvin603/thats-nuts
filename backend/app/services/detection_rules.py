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
            common_alias("almonds"),
            common_alias("almond oil"),
            common_alias("sweet almond oil"),
            common_alias("amande"),
            common_alias("amandes"),
            common_alias("almendra"),
            common_alias("almendras"),
            common_alias("mandorla"),
            common_alias("mandorle"),
            common_alias("mandorla dolce"),
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
            common_alias("walnuts"),
            common_alias("walnut oil"),
            common_alias("walnut seed oil"),
            common_alias("walnut shell powder"),
            common_alias("noix"),
            common_alias("noix de grenoble"),
            common_alias("nuez"),
            common_alias("nueces"),
            common_alias("noce"),
            common_alias("noci"),
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
            common_alias("cashews"),
            common_alias("cashew oil"),
            common_alias("cashew nut oil"),
            common_alias("noix de cajou"),
            common_alias("cajou"),
            common_alias("anacardo"),
            common_alias("anacardos"),
            common_alias("anacardi"),
            common_alias("marañón"),
            common_alias("maranon"),
            inci_alias("anacardium occidentale"),
            inci_alias("anacardium occidentale seed oil"),
        ),
        category="tree_nut",
    ),
    AllergenRule(
        key="pistachio",
        aliases=(
            common_alias("pistachio"),
            common_alias("pistachios"),
            common_alias("pistachio oil"),
            common_alias("pistache"),
            common_alias("pistaches"),
            common_alias("pistacho"),
            common_alias("pistachos"),
            common_alias("pistacchio"),
            common_alias("pistacchi"),
            inci_alias("pistacia vera"),
            inci_alias("pistacia vera seed oil"),
        ),
        category="tree_nut",
    ),
    AllergenRule(
        key="hazelnut",
        aliases=(
            common_alias("hazelnut"),
            common_alias("hazelnuts"),
            common_alias("filbert"),
            common_alias("filberts"),
            common_alias("hazelnut oil"),
            common_alias("hazelnut seed oil"),
            common_alias("noisette"),
            common_alias("noisettes"),
            common_alias("avellana"),
            common_alias("avellanas"),
            common_alias("nocciola"),
            common_alias("nocciole"),
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
            common_alias("macadamia nut"),
            common_alias("macadamia nuts"),
            common_alias("macadamia oil"),
            common_alias("macadamia seed oil"),
            common_alias("noix de macadamia"),
            common_alias("nuez de macadamia"),
            common_alias("nueces de macadamia"),
            common_alias("noce di macadamia"),
            common_alias("noci di macadamia"),
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
            common_alias("brazil nuts"),
            common_alias("brazil nut oil"),
            common_alias("noix du brésil"),
            common_alias("noix du bresil"),
            common_alias("nuez de brasil"),
            common_alias("nueces de brasil"),
            common_alias("noce del brasile"),
            common_alias("noci del brasile"),
            inci_alias("bertholletia excelsa"),
            inci_alias("bertholletia excelsa seed oil"),
        ),
        category="tree_nut",
    ),
    AllergenRule(
        key="pecan",
        aliases=(
            common_alias("pecan"),
            common_alias("pecans"),
            common_alias("pecan oil"),
            common_alias("noix de pecan"),
            common_alias("noix de pécan"),
            common_alias("pacana"),
            common_alias("pacanas"),
            common_alias("nuez pecana"),
            common_alias("nueces pecanas"),
            common_alias("noce pecan"),
            common_alias("noci pecan"),
            inci_alias("carya illinoinensis"),
            inci_alias("carya illinoinensis oil"),
        ),
        category="tree_nut",
    ),
    AllergenRule(
        key="pine_nut",
        aliases=(
            common_alias("pine nut"),
            common_alias("pine nuts"),
            common_alias("pignoli"),
            common_alias("pignon"),
            common_alias("pignons"),
            common_alias("pignon de pin"),
            common_alias("piñon"),
            common_alias("pinon"),
            common_alias("piñones"),
            common_alias("pinones"),
            common_alias("pinolo"),
            common_alias("pinoli"),
            inci_alias("pinus pinea"),
        ),
        category="tree_nut",
    ),
    AllergenRule(
        key="chestnut",
        aliases=(
            common_alias("chestnut"),
            common_alias("chestnuts"),
            common_alias("chataigne"),
            common_alias("chataignes"),
            common_alias("marron"),
            common_alias("marrons"),
            common_alias("castaña"),
            common_alias("castana"),
            common_alias("castañas"),
            common_alias("castanas"),
            common_alias("castagna"),
            common_alias("castagne"),
            common_alias("marrone"),
            common_alias("marroni"),
            inci_alias("castanea sativa"),
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
