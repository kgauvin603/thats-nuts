import logging
from typing import Iterable, Optional

from app.schemas.products import NormalizedProduct
from app.services.product_lookup_providers.base import (
    ProductLookupProvider,
    ProductLookupProviderError,
)

logger = logging.getLogger(__name__)


class ChainedProductLookupProvider(ProductLookupProvider):
    provider_name = "food_then_beauty"
    legacy_provider_name = "beauty_then_food"

    def __init__(self, providers: Iterable[ProductLookupProvider]):
        self.providers = tuple(providers)

    def lookup_by_barcode(self, barcode: str) -> Optional[NormalizedProduct]:
        last_error: Optional[Exception] = None
        incomplete_product: Optional[NormalizedProduct] = None

        for provider in self.providers:
            logger.info(
                "Barcode lookup: %s attempted for normalized barcode %s",
                provider.provider_name,
                barcode,
            )
            try:
                product = provider.lookup_by_barcode(barcode)
            except ProductLookupProviderError as exc:
                logger.info(
                    "Barcode lookup: %s failed for normalized barcode %s",
                    provider.provider_name,
                    barcode,
                )
                last_error = exc
                continue
            except Exception as exc:
                logger.info(
                    "Barcode lookup: %s failed unexpectedly for normalized barcode %s",
                    provider.provider_name,
                    barcode,
                )
                last_error = exc
                continue

            if product is None:
                logger.info(
                    "Barcode lookup: %s failed for normalized barcode %s",
                    provider.provider_name,
                    barcode,
                )
                continue

            if _has_usable_ingredient_text(product):
                logger.info(
                    "Barcode lookup: %s succeeded for normalized barcode %s",
                    provider.provider_name,
                    barcode,
                )
                return product

            if incomplete_product is None:
                incomplete_product = product

            logger.info(
                "Barcode lookup: %s failed for normalized barcode %s; product data was incomplete",
                provider.provider_name,
                barcode,
            )

        if incomplete_product is not None:
            return incomplete_product

        if last_error is not None:
            raise ProductLookupProviderError(
                "All configured lookup providers failed before returning usable product data."
            ) from last_error
        return None


def _has_usable_ingredient_text(product: NormalizedProduct) -> bool:
    return bool(product.ingredient_text and product.ingredient_text.strip()) and (
        product.ingredient_coverage_status in {"complete", "partial"}
    )


def product_lookup_has_usable_ingredient_text(product: NormalizedProduct) -> bool:
    return _has_usable_ingredient_text(product)
