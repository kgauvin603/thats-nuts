import re
from typing import Callable, Optional

import httpx

from app.schemas.products import NormalizedProduct
from app.services.product_lookup_providers.base import (
    ProductLookupProvider,
    ProductLookupProviderError,
    ProductLookupProviderSettings,
)

OPEN_FACTS_FIELDS = (
    "code,product_name,product_name_en,generic_name,generic_name_en,"
    "brands,brands_tags,ingredients_text,ingredients_text_en,"
    "ingredients_text_with_allergens,ingredients_text_with_allergens_en,"
    "ingredients_text_from_image,ingredients_text_from_image_en,"
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


class OpenFactsProductLookupProvider(ProductLookupProvider):
    provider_name = "open_facts"

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
                    params={"fields": OPEN_FACTS_FIELDS},
                    headers={"User-Agent": self.settings.user_agent},
                    timeout=self.settings.timeout_seconds,
                )
                response.raise_for_status()
                payload = response.json()
                break
            except httpx.RequestError as exc:
                if attempt == 1:
                    raise ProductLookupProviderError(
                        f"{self.provider_name.replace('_', ' ').title()} request failed."
                    ) from exc
            except (httpx.HTTPStatusError, ValueError) as exc:
                raise ProductLookupProviderError(
                    f"{self.provider_name.replace('_', ' ').title()} returned an invalid response."
                ) from exc

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
            "ingredients_text_from_image",
            "ingredients_text_from_image_en",
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


class OpenBeautyFactsProductLookupProvider(OpenFactsProductLookupProvider):
    provider_name = "open_beauty_facts"


class OpenFoodFactsProductLookupProvider(OpenFactsProductLookupProvider):
    provider_name = "open_food_facts"
