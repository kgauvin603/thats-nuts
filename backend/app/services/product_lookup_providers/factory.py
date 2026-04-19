from app.core.config import get_settings
from app.services.product_lookup_providers.base import ProductLookupProvider, ProductLookupProviderSettings
from app.services.product_lookup_providers.chain import ChainedProductLookupProvider
from app.services.product_lookup_providers.mock_api import MockApiProductLookupProvider
from app.services.product_lookup_providers.open_facts import (
    OpenBeautyFactsProductLookupProvider,
    OpenFoodFactsProductLookupProvider,
)
from app.services.product_lookup_providers.stub import StubProductLookupProvider


def build_provider_settings() -> ProductLookupProviderSettings:
    settings = get_settings()
    return ProductLookupProviderSettings(
        provider_name=settings.product_lookup_provider,
        base_url=settings.product_lookup_food_base_url,
        api_key=settings.product_lookup_api_key,
        user_agent=settings.product_lookup_user_agent,
        timeout_seconds=settings.product_lookup_timeout_seconds,
        beauty_base_url=settings.product_lookup_beauty_base_url,
        food_base_url=settings.product_lookup_food_base_url,
    )


def build_product_lookup_provider(
    provider_name: str,
    provider_settings: ProductLookupProviderSettings | None = None,
) -> ProductLookupProvider:
    settings = provider_settings or build_provider_settings()
    if provider_name == StubProductLookupProvider.provider_name:
        return StubProductLookupProvider()
    if provider_name == MockApiProductLookupProvider.provider_name:
        return MockApiProductLookupProvider(settings=settings)
    if provider_name == OpenBeautyFactsProductLookupProvider.provider_name:
        return OpenBeautyFactsProductLookupProvider(
            settings=_copy_settings(settings, provider_name, settings.beauty_base_url or settings.base_url)
        )
    if provider_name == OpenFoodFactsProductLookupProvider.provider_name:
        return OpenFoodFactsProductLookupProvider(
            settings=_copy_settings(settings, provider_name, settings.food_base_url or settings.base_url)
        )
    if provider_name == ChainedProductLookupProvider.provider_name:
        beauty_provider = build_product_lookup_provider(
            OpenBeautyFactsProductLookupProvider.provider_name,
            provider_settings=settings,
        )
        food_provider = build_product_lookup_provider(
            OpenFoodFactsProductLookupProvider.provider_name,
            provider_settings=settings,
        )
        return ChainedProductLookupProvider((beauty_provider, food_provider))
    raise ValueError(f"Unsupported product lookup provider: {provider_name}")


def _copy_settings(
    settings: ProductLookupProviderSettings,
    provider_name: str,
    base_url: str,
) -> ProductLookupProviderSettings:
    return ProductLookupProviderSettings(
        provider_name=provider_name,
        base_url=base_url,
        api_key=settings.api_key,
        user_agent=settings.user_agent,
        timeout_seconds=settings.timeout_seconds,
        beauty_base_url=settings.beauty_base_url,
        food_base_url=settings.food_base_url,
    )
