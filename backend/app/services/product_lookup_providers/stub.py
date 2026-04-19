from typing import Dict, Optional

from app.schemas.products import NormalizedProduct
from app.services.product_lookup_providers.base import ProductLookupProvider


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
