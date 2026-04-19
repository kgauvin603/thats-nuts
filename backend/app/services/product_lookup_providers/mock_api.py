from typing import Dict, Optional

from app.schemas.products import NormalizedProduct
from app.services.product_lookup_providers.base import (
    ProductLookupProvider,
    ProductLookupProviderSettings,
)


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
