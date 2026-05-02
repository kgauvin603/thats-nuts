from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from app.schemas.products import NormalizedProduct
from app.core.product_lookup_constants import DEFAULT_PRODUCT_LOOKUP_USER_AGENT


class ProductLookupProviderError(RuntimeError):
    pass


@dataclass(frozen=True)
class ProductLookupProviderSettings:
    provider_name: str
    base_url: str
    api_key: str = ""
    user_agent: str = DEFAULT_PRODUCT_LOOKUP_USER_AGENT
    timeout_seconds: float = 5.0
    beauty_base_url: str = ""
    food_base_url: str = ""


class ProductLookupProvider(ABC):
    provider_name = "base"

    @abstractmethod
    def lookup_by_barcode(self, barcode: str) -> Optional[NormalizedProduct]:
        raise NotImplementedError
