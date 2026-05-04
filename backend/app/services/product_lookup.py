from functools import lru_cache
import logging
import re
from typing import Optional

from app.schemas.ingredients import AllergyProfile
from app.schemas.products import NormalizedProduct, ProductLookupResponse
from app.services.persistence import get_cached_product, persist_scan_result, upsert_product
from app.services.product_lookup_providers import (
    ChainedProductLookupProvider,
    MockApiProductLookupProvider,
    OpenBeautyFactsProductLookupProvider,
    OpenFoodFactsProductLookupProvider,
    ProductLookupProvider,
    ProductLookupProviderError,
    ProductLookupProviderSettings,
    StubProductLookupProvider,
    build_product_lookup_provider,
    build_provider_settings,
)
from app.services.product_lookup_providers.chain import product_lookup_has_usable_ingredient_text
from app.services.rules_engine import check_ingredient_text

MISSING_INGREDIENTS_EXPLANATION = (
    "A full, usable ingredient list is required to verify this product safely."
)
PARTIAL_INGREDIENT_COVERAGE_EXPLANATION = (
    "Only part of the ingredient list was available, so this result may be incomplete."
)
PROVIDER_FAILURE_EXPLANATION = (
    "Product lookup could not be completed because the configured provider did not return "
    "reliable product data for this barcode. Try again in a moment or enter ingredients manually."
)
PRODUCT_NOT_FOUND_EXPLANATION = (
    "No product record with a usable ingredient list was found for this barcode."
)
MANUAL_ENRICHMENT_EXPLANATION = (
    "Product data was saved from a locally submitted ingredient list for this barcode."
)
ENRICHMENT_CACHE_SOURCES = {"manual_entry", "text_scan"}
VALIDATION_CACHE_BRAND_NAMES = {"validation brand"}
VALIDATION_CACHE_PRODUCT_NAMES = {"validation product"}
VALIDATION_CACHE_INGREDIENT_TEXTS = {"water, juglans regia seed oil"}

logger = logging.getLogger(__name__)


class ProductLookupService:
    def __init__(self, provider: ProductLookupProvider):
        self.provider = provider

    def lookup_by_barcode(
        self,
        barcode: str,
        allergy_profile: Optional[AllergyProfile] = None,
    ) -> ProductLookupResponse:
        normalized_barcode = normalize_barcode(barcode)
        lookup_path = [f"normalized:{normalized_barcode}"]
        logger.info("Barcode lookup: normalized barcode %s", normalized_barcode)

        try:
            product = self.provider.lookup_by_barcode(normalized_barcode)
            provider_failed = False
        except ProductLookupProviderError:
            logger.info(
                "Barcode lookup: configured provider failed for normalized barcode %s",
                normalized_barcode,
            )
            product = None
            provider_failed = True
        except Exception:
            logger.info(
                "Barcode lookup: configured provider failed unexpectedly for normalized barcode %s",
                normalized_barcode,
            )
            product = None
            provider_failed = True
        lookup_path.extend(self._build_provider_lookup_path(product, provider_failed))
        if product and product_lookup_has_usable_ingredient_text(product):
            lookup_path.append("enrichment:skipped")
            logger.info(
                "Barcode lookup: enrichment not attempted for normalized barcode %s",
                normalized_barcode,
            )
            logger.info(
                "Barcode lookup: final provider/source selected %s for normalized barcode %s",
                product.source,
                normalized_barcode,
            )
            return self._build_assessed_response(
                product,
                source_explanation=f"Product data was returned by the configured {product.source} provider.",
                allergy_profile=allergy_profile,
                lookup_path=lookup_path,
            )

        logger.info(
            "Barcode lookup: enrichment attempted for normalized barcode %s",
            normalized_barcode,
        )
        lookup_path.append("enrichment:attempted")
        enrichment_product = get_cached_product(normalized_barcode)
        if self._has_usable_enrichment_product(enrichment_product, normalized_barcode):
            logger.info(
                "Barcode lookup: enrichment succeeded for normalized barcode %s",
                normalized_barcode,
            )
            lookup_path.append("enrichment:succeeded")
            logger.info(
                "Barcode lookup: final provider/source selected %s for normalized barcode %s",
                "enrichment",
                normalized_barcode,
            )
            return self._build_assessed_response(
                enrichment_product,
                source_explanation=self._build_cached_source_explanation(enrichment_product),
                allergy_profile=allergy_profile,
                response_source="enrichment",
                lookup_path=lookup_path,
            )

        logger.info(
            "Barcode lookup: enrichment failed for normalized barcode %s",
            normalized_barcode,
        )
        lookup_path.append("enrichment:failed")

        if product is not None:
            logger.info(
                "Barcode lookup: returning incomplete provider product %s for normalized barcode %s",
                product.source,
                normalized_barcode,
            )
            return self._build_assessed_response(
                product,
                source_explanation=f"Product data was returned by the configured {product.source} provider.",
                allergy_profile=allergy_profile,
                lookup_path=lookup_path,
            )

        logger.info(
            "Barcode lookup: final provider/source selected not_found for normalized barcode %s",
            normalized_barcode,
        )
        explanation = (
            PROVIDER_FAILURE_EXPLANATION
            if provider_failed and not isinstance(self.provider, ChainedProductLookupProvider)
            else PRODUCT_NOT_FOUND_EXPLANATION
        )
        product_id = upsert_product(product) if product else None
        self._persist_unsuccessful_lookup(
            normalized_barcode,
            explanation,
            allergy_profile=allergy_profile,
            product_id=product_id,
        )
        return ProductLookupResponse(
            found=False,
            source="not_found",
            lookup_path=lookup_path,
            product=None,
            ingredient_text=None,
            assessment_result=None,
            matched_ingredients=[],
            explanation=explanation,
        )

    def enrich_barcode_with_ingredients(
        self,
        barcode: str,
        ingredient_text: str,
        product_name: Optional[str] = None,
        brand_name: Optional[str] = None,
        source: Optional[str] = None,
        allergy_profile: Optional[AllergyProfile] = None,
    ) -> ProductLookupResponse:
        normalized_barcode = normalize_barcode(barcode)
        existing_product = get_cached_product(normalized_barcode)
        normalized_source = (source or "manual_entry").strip() or "manual_entry"
        cleaned_ingredient_text = ingredient_text.strip()

        product = NormalizedProduct(
            barcode=normalized_barcode,
            product_name=product_name or (existing_product.product_name if existing_product else None),
            brand_name=brand_name or (existing_product.brand_name if existing_product else None),
            image_url=existing_product.image_url if existing_product else None,
            ingredient_text=cleaned_ingredient_text,
            ingredient_coverage_status="complete",
            source=normalized_source,
        )

        return self._build_assessed_response(
            product,
            source_explanation=MANUAL_ENRICHMENT_EXPLANATION,
            allergy_profile=allergy_profile,
            scan_type="barcode_enrichment",
            response_source="enrichment",
        )

    def _build_assessed_response(
        self,
        product: NormalizedProduct,
        source_explanation: str,
        allergy_profile: Optional[AllergyProfile] = None,
        scan_type: str = "barcode_lookup",
        response_source: Optional[str] = None,
        lookup_path: Optional[list[str]] = None,
    ) -> ProductLookupResponse:
        ingredient_text = product.ingredient_text
        product_id = upsert_product(product)

        if ingredient_text and ingredient_text.strip():
            assessment = check_ingredient_text(
                ingredient_text,
                allergy_profile=allergy_profile,
            )
            persist_scan_result(
                ingredient_text,
                assessment,
                allergy_profile=allergy_profile,
                product_id=product_id,
                scan_type=scan_type,
                submitted_barcode=product.barcode,
            )
            return ProductLookupResponse(
                found=True,
                source=response_source or product.source,
                lookup_path=lookup_path or [],
                product=product,
                ingredient_text=ingredient_text,
                assessment_result=assessment["status"],
                matched_ingredients=assessment["matched_ingredients"],
                ruleset_version=assessment.get("ruleset_version"),
                unknown_terms=assessment.get("unknown_terms", []),
                explanation=self._build_assessment_explanation(
                    source_explanation=source_explanation,
                    coverage_status=product.ingredient_coverage_status,
                    assessment_explanation=assessment["explanation"],
                ),
            )

        assessment = {
            "status": "cannot_verify",
            "matched_ingredients": [],
            "explanation": MISSING_INGREDIENTS_EXPLANATION,
        }
        persist_scan_result(
            "",
            assessment,
            allergy_profile=allergy_profile,
            product_id=product_id,
            scan_type=scan_type,
            submitted_barcode=product.barcode,
        )
        return ProductLookupResponse(
            found=True,
            source=response_source or product.source,
            lookup_path=lookup_path or [],
            product=product,
            ingredient_text=ingredient_text,
            assessment_result=assessment["status"],
            matched_ingredients=[],
            ruleset_version=assessment.get("ruleset_version"),
            unknown_terms=assessment.get("unknown_terms", []),
            explanation=(
                f"{source_explanation} This record did not include a full, usable ingredient list. "
                "A full, usable ingredient list is required to verify this product safely."
            ),
        )

    @staticmethod
    def _build_assessment_explanation(
        source_explanation: str,
        coverage_status: str,
        assessment_explanation: str,
    ) -> str:
        parts = [source_explanation]
        if coverage_status == "partial":
            parts.append(PARTIAL_INGREDIENT_COVERAGE_EXPLANATION)
        parts.append(assessment_explanation)
        return " ".join(parts)

    @staticmethod
    def _persist_unsuccessful_lookup(
        barcode: str,
        explanation: str,
        allergy_profile: Optional[AllergyProfile] = None,
        product_id: Optional[int] = None,
    ) -> None:
        persist_scan_result(
            "",
            {
                "status": "cannot_verify",
                "matched_ingredients": [],
                "explanation": explanation,
            },
            allergy_profile=allergy_profile,
            product_id=product_id,
            scan_type="barcode_lookup",
            submitted_barcode=barcode,
        )

    @staticmethod
    def _build_cached_source_explanation(product: NormalizedProduct) -> str:
        if product.source in {"manual_entry", "text_scan"}:
            return "Product data was returned from the local barcode enrichment cache."
        return "Product data was returned from the local product cache."

    @staticmethod
    def _has_usable_enrichment_product(
        product: Optional[NormalizedProduct],
        barcode: str,
    ) -> bool:
        if product is None:
            return False
        if product.barcode != barcode:
            return False
        if product.source not in ENRICHMENT_CACHE_SOURCES:
            return False
        if ProductLookupService._is_validation_cache_product(product):
            logger.info(
                "Barcode lookup: ignored validation enrichment cache row for normalized barcode %s",
                barcode,
            )
            return False
        return product_lookup_has_usable_ingredient_text(product)

    @staticmethod
    def _is_validation_cache_product(product: NormalizedProduct) -> bool:
        brand_name = (product.brand_name or "").strip().lower()
        product_name = (product.product_name or "").strip().lower()
        ingredient_text = (product.ingredient_text or "").strip().lower()
        return (
            brand_name in VALIDATION_CACHE_BRAND_NAMES
            or product_name in VALIDATION_CACHE_PRODUCT_NAMES
            or ingredient_text in VALIDATION_CACHE_INGREDIENT_TEXTS
        )

    def _build_provider_lookup_path(
        self,
        product: Optional[NormalizedProduct],
        provider_failed: bool,
    ) -> list[str]:
        provider_names = self._provider_names()
        path = []

        if provider_failed or product is None or not product_lookup_has_usable_ingredient_text(product):
            for provider_name in provider_names:
                path.extend((f"{provider_name}:attempted", f"{provider_name}:failed"))
            return path

        product_source = product.source
        for index, provider_name in enumerate(provider_names):
            path.append(f"{provider_name}:attempted")
            if provider_name == product_source:
                path.append(f"{provider_name}:succeeded")
                for skipped_provider in provider_names[index + 1 :]:
                    path.append(f"{skipped_provider}:skipped")
                return path
            path.append(f"{provider_name}:failed")

        return path

    def _provider_names(self) -> list[str]:
        if isinstance(self.provider, ChainedProductLookupProvider):
            return [provider.provider_name for provider in self.provider.providers]
        return [self.provider.provider_name]


@lru_cache(maxsize=1)
def get_product_lookup_service() -> ProductLookupService:
    provider_settings = build_provider_settings()
    provider = build_product_lookup_provider(
        _barcode_lookup_provider_name(provider_settings.provider_name),
        provider_settings=provider_settings,
    )
    return ProductLookupService(provider)


def _barcode_lookup_provider_name(provider_name: str) -> str:
    if provider_name in {
        OpenFoodFactsProductLookupProvider.provider_name,
        OpenBeautyFactsProductLookupProvider.provider_name,
        ChainedProductLookupProvider.legacy_provider_name,
    }:
        return ChainedProductLookupProvider.provider_name
    return provider_name


def normalize_barcode(barcode: str) -> str:
    trimmed = barcode.strip()
    if re.search(r"[A-Za-z]", trimmed):
        return trimmed
    normalized = re.sub(r"\D+", "", trimmed)
    return normalized or trimmed
