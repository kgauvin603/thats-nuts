from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import lru_cache
import re
from typing import Callable, Dict, Optional

import httpx
from app.core.config import get_settings
from app.schemas.ingredients import AllergyProfile
from app.schemas.products import NormalizedProduct, ProductLookupResponse
from app.services.persistence import get_cached_product, persist_scan_result, upsert_product
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
OPEN_FOOD_FACTS_FIELDS = (
    "code,product_name,product_name_en,generic_name,generic_name_en,"
    "brands,brands_tags,ingredients_text,ingredients_text_en,"
    "ingredients_text_with_allergens,ingredients_text_with_allergens_en,"
    "image_front_url,image_front_small_url,image_url,ingredients"
)
WEAK_TEXT_VALUES = {
    "",
    "n/a",
    "na",
    "unknown",
    "not available",
    "not provided",
    "see packaging",
    "see package",
    "see label",
}


class ProductLookupProviderError(RuntimeError):
    pass


@dataclass(frozen=True)
class ProductLookupProviderSettings:
    provider_name: str
    base_url: str
    api_key: str = ""
    user_agent: str = "thats-nuts-backend/0.1 (contact@example.com)"
    timeout_seconds: float = 5.0


class ProductLookupProvider(ABC):
    provider_name = "base"

    @abstractmethod
    def lookup_by_barcode(self, barcode: str) -> Optional[NormalizedProduct]:
        raise NotImplementedError


class StubProductLookupProvider(ProductLookupProvider):
    provider_name = "stub"

    def __init__(self, products: Optional[Dict[str, dict]] = None):
        self.products = products or {
            "0001234567890": {
                "barcode": "0001234567890",
                "brand_name": "Thats Nuts Labs",
                "product_name": "Sample Almond Body Oil",
                "image_url": "https://images.example.invalid/products/0001234567890.jpg",
                "ingredient_text": "Caprylic/Capric Triglyceride, Prunus Amygdalus Dulcis Oil",
                "ingredient_coverage_status": "complete",
                "source": self.provider_name,
            }
        }

    def lookup_by_barcode(self, barcode: str) -> Optional[NormalizedProduct]:
        product = self.products.get(barcode)
        if not product:
            return None
        return NormalizedProduct(**product)


class MockApiProductLookupProvider(ProductLookupProvider):
    provider_name = "mock_api"

    def __init__(
        self,
        settings: ProductLookupProviderSettings,
        responses: Optional[Dict[str, dict]] = None,
    ):
        self.settings = settings
        self.responses = responses or {
            "5012345678900": {
                "code": "5012345678900",
                "brand": "Future Catalog Co",
                "title": "Mock Provider Body Butter",
                "image": "https://cdn.example.invalid/products/5012345678900.png",
                "ingredients_text": "Water, Glycerin, Butyrospermum Parkii Butter",
            }
        }

    def lookup_by_barcode(self, barcode: str) -> Optional[NormalizedProduct]:
        provider_payload = self.fetch_provider_payload(barcode)
        if not provider_payload:
            return None
        return self.normalize_payload(provider_payload)

    def fetch_provider_payload(self, barcode: str) -> Optional[dict]:
        # Replace this mock payload fetch with an HTTP client call when a real provider is selected.
        return self.responses.get(barcode)

    def normalize_payload(self, payload: dict) -> NormalizedProduct:
        ingredient_text = payload.get("ingredients_text")
        if ingredient_text:
            coverage_status = "complete"
        else:
            coverage_status = "missing"

        return NormalizedProduct(
            barcode=payload["code"],
            brand_name=payload.get("brand"),
            product_name=payload.get("title"),
            image_url=payload.get("image"),
            ingredient_text=ingredient_text,
            ingredient_coverage_status=coverage_status,
            source=self.provider_name,
        )


class OpenFoodFactsProductLookupProvider(ProductLookupProvider):
    provider_name = "open_food_facts"

    def __init__(
        self,
        settings: ProductLookupProviderSettings,
        http_get: Optional[Callable[..., httpx.Response]] = None,
    ):
        self.settings = settings
        self.http_get = http_get or httpx.get

    def lookup_by_barcode(self, barcode: str) -> Optional[NormalizedProduct]:
        provider_payload = self.fetch_provider_payload(barcode)
        if not provider_payload:
            return None
        return self.normalize_payload(provider_payload)

    def fetch_provider_payload(self, barcode: str) -> Optional[dict]:
        payload = None
        for attempt in range(2):
            try:
                response = self.http_get(
                    f"{self.settings.base_url.rstrip('/')}/api/v2/product/{barcode}",
                    params={"fields": OPEN_FOOD_FACTS_FIELDS},
                    headers={"User-Agent": self.settings.user_agent},
                    timeout=self.settings.timeout_seconds,
                )
                response.raise_for_status()
                payload = response.json()
                break
            except httpx.RequestError as exc:
                if attempt == 1:
                    raise ProductLookupProviderError("Open Food Facts request failed.") from exc
            except (httpx.HTTPStatusError, ValueError) as exc:
                raise ProductLookupProviderError("Open Food Facts returned an invalid response.") from exc

        if payload is None:
            return None
        if payload.get("status") == 0:
            return None
        return payload.get("product")

    def normalize_payload(self, payload: dict) -> NormalizedProduct:
        ingredient_text, coverage_status = self.normalize_ingredient_text(payload)

        return NormalizedProduct(
            barcode=self.clean_text(payload.get("code")) or "",
            brand_name=self.normalize_brand_name(payload),
            product_name=self.normalize_product_name(payload),
            image_url=self.normalize_image_url(payload),
            ingredient_text=ingredient_text,
            ingredient_coverage_status=coverage_status,
            source=self.provider_name,
        )

    @staticmethod
    def clean_text(value: Optional[object]) -> Optional[str]:
        if value is None:
            return None
        text = re.sub(r"\s+", " ", str(value)).strip()
        if text.lower() in WEAK_TEXT_VALUES:
            return None
        return text

    def normalize_product_name(self, payload: dict) -> Optional[str]:
        for key in ("product_name", "product_name_en", "generic_name", "generic_name_en"):
            value = self.clean_text(payload.get(key))
            if value:
                return value
        return None

    def normalize_brand_name(self, payload: dict) -> Optional[str]:
        brands = self.clean_text(payload.get("brands"))
        if brands:
            parts = [part.strip() for part in brands.split(",") if part.strip()]
            deduped = list(dict.fromkeys(parts))
            if deduped:
                return ", ".join(deduped)

        tags = payload.get("brands_tags") or []
        cleaned_tags = []
        for tag in tags:
            cleaned = self.clean_text(tag)
            if cleaned:
                cleaned_tags.append(cleaned.replace("-", " ").title())
        cleaned_tags = list(dict.fromkeys(cleaned_tags))
        return ", ".join(cleaned_tags) if cleaned_tags else None

    def normalize_image_url(self, payload: dict) -> Optional[str]:
        for key in ("image_front_url", "image_front_small_url", "image_url"):
            value = self.clean_text(payload.get(key))
            if value:
                return value
        return None

    def normalize_ingredient_text(self, payload: dict) -> tuple[Optional[str], str]:
        for key in (
            "ingredients_text",
            "ingredients_text_en",
            "ingredients_text_with_allergens",
            "ingredients_text_with_allergens_en",
        ):
            value = self.clean_text(payload.get(key))
            if value:
                return value, "complete"

        ingredients = payload.get("ingredients") or []
        normalized_ingredients = []
        for ingredient in ingredients:
            if not isinstance(ingredient, dict):
                continue
            candidate = self.clean_text(ingredient.get("text"))
            if not candidate:
                ingredient_id = self.clean_text(ingredient.get("id"))
                if ingredient_id and ":" in ingredient_id:
                    candidate = ingredient_id.split(":", 1)[1].replace("-", " ").title()
            if candidate and candidate not in normalized_ingredients:
                normalized_ingredients.append(candidate)

        if normalized_ingredients:
            return ", ".join(normalized_ingredients), "partial"

        return None, "missing"


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


def build_provider_settings() -> ProductLookupProviderSettings:
    settings = get_settings()
    return ProductLookupProviderSettings(
        provider_name=settings.product_lookup_provider,
        base_url=settings.product_lookup_base_url,
        api_key=settings.product_lookup_api_key,
        user_agent=settings.product_lookup_user_agent,
        timeout_seconds=settings.product_lookup_timeout_seconds,
    )


def build_product_lookup_provider(
    provider_name: str,
    provider_settings: Optional[ProductLookupProviderSettings] = None,
) -> ProductLookupProvider:
    settings = provider_settings or build_provider_settings()
    if provider_name == StubProductLookupProvider.provider_name:
        return StubProductLookupProvider()
    if provider_name == MockApiProductLookupProvider.provider_name:
        return MockApiProductLookupProvider(settings=settings)
    if provider_name == OpenFoodFactsProductLookupProvider.provider_name:
        return OpenFoodFactsProductLookupProvider(settings=settings)
    raise ValueError(f"Unsupported product lookup provider: {provider_name}")


@lru_cache(maxsize=1)
def get_product_lookup_service() -> ProductLookupService:
    provider_settings = build_provider_settings()
    provider = build_product_lookup_provider(
        provider_settings.provider_name,
        provider_settings=provider_settings,
    )
    return ProductLookupService(provider)
