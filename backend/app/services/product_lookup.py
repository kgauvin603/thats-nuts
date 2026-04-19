from functools import lru_cache
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
from app.services.rules_engine import check_ingredient_text

MISSING_INGREDIENTS_EXPLANATION = (
    "A product record was found, but it did not include a usable ingredient list. This product "
    "cannot be verified until a full ingredient list is available."
)
PARTIAL_INGREDIENT_COVERAGE_EXPLANATION = (
    "Only part of the ingredient list was available, so this assessment may be incomplete and "
    "could miss nut-related ingredients that were not returned by the product record."
)
PROVIDER_FAILURE_EXPLANATION = (
    "Product lookup could not be completed because the configured provider did not return "
    "reliable product data for this barcode. Try again in a moment or enter ingredients manually."
)
PRODUCT_NOT_FOUND_EXPLANATION = (
    "No product record was found for this barcode in the local cache or from the configured "
    "lookup provider."
)
MANUAL_ENRICHMENT_EXPLANATION = (
    "Product data was saved from a locally submitted ingredient list for this barcode."
)


class ProductLookupService:
    def __init__(self, provider: ProductLookupProvider):
        self.provider = provider

    def lookup_by_barcode(
        self,
        barcode: str,
        allergy_profile: Optional[AllergyProfile] = None,
    ) -> ProductLookupResponse:
        product = get_cached_product(barcode)
        if product:
            return self._build_assessed_response(
                product,
                source_explanation=self._build_cached_source_explanation(product),
                allergy_profile=allergy_profile,
            )

        try:
            product = self.provider.lookup_by_barcode(barcode)
        except ProductLookupProviderError:
            self._persist_unsuccessful_lookup(
                barcode,
                PROVIDER_FAILURE_EXPLANATION,
                allergy_profile=allergy_profile,
            )
            return ProductLookupResponse(
                found=False,
                product=None,
                ingredient_text=None,
                assessment_result=None,
                matched_ingredients=[],
                explanation=PROVIDER_FAILURE_EXPLANATION,
            )
        except Exception:
            self._persist_unsuccessful_lookup(
                barcode,
                PROVIDER_FAILURE_EXPLANATION,
                allergy_profile=allergy_profile,
            )
            return ProductLookupResponse(
                found=False,
                product=None,
                ingredient_text=None,
                assessment_result=None,
                matched_ingredients=[],
                explanation=PROVIDER_FAILURE_EXPLANATION,
            )
        if not product:
            self._persist_unsuccessful_lookup(
                barcode,
                PRODUCT_NOT_FOUND_EXPLANATION,
                allergy_profile=allergy_profile,
            )
            return ProductLookupResponse(
                found=False,
                product=None,
                ingredient_text=None,
                assessment_result=None,
                matched_ingredients=[],
                explanation=PRODUCT_NOT_FOUND_EXPLANATION,
            )
        return self._build_assessed_response(
            product,
            source_explanation=f"Product data was returned by the configured {product.source} provider.",
            allergy_profile=allergy_profile,
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
        existing_product = get_cached_product(barcode)
        normalized_source = (source or "manual_entry").strip() or "manual_entry"
        cleaned_ingredient_text = ingredient_text.strip()

        product = NormalizedProduct(
            barcode=barcode,
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
        )

    def _build_assessed_response(
        self,
        product: NormalizedProduct,
        source_explanation: str,
        allergy_profile: Optional[AllergyProfile] = None,
        scan_type: str = "barcode_lookup",
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
            product=product,
            ingredient_text=ingredient_text,
            assessment_result=assessment["status"],
            matched_ingredients=[],
            ruleset_version=assessment.get("ruleset_version"),
            unknown_terms=assessment.get("unknown_terms", []),
            explanation=f"{source_explanation} {MISSING_INGREDIENTS_EXPLANATION}",
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
    ) -> None:
        persist_scan_result(
            "",
            {
                "status": "cannot_verify",
                "matched_ingredients": [],
                "explanation": explanation,
            },
            allergy_profile=allergy_profile,
            scan_type="barcode_lookup",
            submitted_barcode=barcode,
        )

    @staticmethod
    def _build_cached_source_explanation(product: NormalizedProduct) -> str:
        if product.source in {"manual_entry", "text_scan"}:
            return "Product data was returned from the local barcode enrichment cache."
        return "Product data was returned from the local product cache."


@lru_cache(maxsize=1)
def get_product_lookup_service() -> ProductLookupService:
    provider_settings = build_provider_settings()
    provider = build_product_lookup_provider(
        provider_settings.provider_name,
        provider_settings=provider_settings,
    )
    return ProductLookupService(provider)
