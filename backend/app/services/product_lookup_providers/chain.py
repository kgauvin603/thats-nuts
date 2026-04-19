from typing import Iterable, Optional

from app.schemas.products import IngredientCoverageStatus, NormalizedProduct
from app.services.product_lookup_providers.base import (
    ProductLookupProvider,
    ProductLookupProviderError,
)

_COVERAGE_SCORE: dict[IngredientCoverageStatus, int] = {
    "complete": 3,
    "partial": 2,
    "unknown": 1,
    "missing": 0,
}


class ChainedProductLookupProvider(ProductLookupProvider):
    provider_name = "beauty_then_food"

    def __init__(self, providers: Iterable[ProductLookupProvider]):
        self.providers = tuple(providers)

    def lookup_by_barcode(self, barcode: str) -> Optional[NormalizedProduct]:
        best_product: Optional[NormalizedProduct] = None
        last_error: Optional[Exception] = None

        for provider in self.providers:
            try:
                product = provider.lookup_by_barcode(barcode)
            except ProductLookupProviderError as exc:
                last_error = exc
                continue

            if product is None:
                continue

            if best_product is None or _product_score(product) > _product_score(best_product):
                best_product = product

            if _has_usable_ingredient_text(product):
                return product

        if best_product is not None:
            return best_product
        if last_error is not None:
            raise ProductLookupProviderError(
                "All configured lookup providers failed before returning usable product data."
            ) from last_error
        return None


def _has_usable_ingredient_text(product: NormalizedProduct) -> bool:
    return bool(product.ingredient_text and product.ingredient_text.strip()) and (
        product.ingredient_coverage_status in {"complete", "partial"}
    )


def _product_score(product: NormalizedProduct) -> int:
    return _COVERAGE_SCORE.get(product.ingredient_coverage_status, 0)
