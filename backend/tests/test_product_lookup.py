import httpx
import pytest
from sqlmodel import Session, select

from app.api.routes.product_lookup import enrich_product, lookup_product
from app.core.config import get_settings
from app.db.session import get_engine
from app.models import AllergyProfileRecord, Product, ScanHistory
from app.schemas.ingredients import AllergyProfile
from app.schemas.products import NormalizedProduct, ProductEnrichmentRequest, ProductLookupRequest
from app.services.product_lookup import (
    ChainedProductLookupProvider,
    MockApiProductLookupProvider,
    OpenBeautyFactsProductLookupProvider,
    OpenFoodFactsProductLookupProvider,
    ProductLookupProvider,
    ProductLookupProviderSettings,
    ProductLookupService,
    StubProductLookupProvider,
    build_product_lookup_provider,
    get_product_lookup_service,
)
from app.services.persistence import prepare_persistence


class FailingProductLookupProvider(ProductLookupProvider):
    provider_name = "failing"

    def lookup_by_barcode(self, barcode: str):
        raise RuntimeError("provider unavailable")


_DEFAULT_PRODUCT = object()


class RecordingProductLookupProvider(ProductLookupProvider):
    def __init__(self, provider_name: str, product: dict | None | object = _DEFAULT_PRODUCT):
        self.provider_name = provider_name
        self.product = product
        self.calls = []

    def lookup_by_barcode(self, barcode: str):
        self.calls.append(barcode)
        if self.product is None:
            return None
        return self._normalized_product(barcode)

    def _normalized_product(self, barcode: str):
        payload = {
            "barcode": barcode,
            "brand_name": f"{self.provider_name} Brand",
            "product_name": f"{self.provider_name} Product",
            "image_url": None,
            "ingredient_text": "Water, Glycerin",
            "ingredient_coverage_status": "complete",
            "source": self.provider_name,
        }
        if self.product is not _DEFAULT_PRODUCT:
            payload.update(self.product)
        return NormalizedProduct(**payload)


class ErrorRecordingProductLookupProvider(ProductLookupProvider):
    def __init__(self, provider_name: str):
        self.provider_name = provider_name
        self.calls = []

    def lookup_by_barcode(self, barcode: str):
        self.calls.append(barcode)
        raise RuntimeError("provider unavailable")


class FakeHttpResponse:
    def __init__(self, payload: dict, status_code: int = 200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"http error {self.status_code}")

    def json(self):
        return self._payload


class FakeInvalidJsonResponse:
    status_code = 200

    def raise_for_status(self):
        return None

    def json(self):
        raise ValueError("empty or invalid JSON")


def test_stub_provider_returns_normalized_product():
    provider = StubProductLookupProvider(
        products={
            "12345": {
                "barcode": "12345",
                "brand_name": "Test Brand",
                "product_name": "Test Product",
                "image_url": "https://images.example.invalid/test-product.jpg",
                "ingredient_text": "Water, Glycerin",
                "ingredient_coverage_status": "partial",
                "source": "stub",
            }
        }
    )

    product = provider.lookup_by_barcode("12345")

    assert product is not None
    assert product.barcode == "12345"
    assert product.product_name == "Test Product"
    assert product.brand_name == "Test Brand"
    assert product.ingredient_coverage_status == "partial"
    assert product.source == "stub"


def test_product_lookup_service_returns_not_found_response():
    service = ProductLookupService(StubProductLookupProvider(products={}))

    result = service.lookup_by_barcode("99999")

    assert result.found is False
    assert result.product is None
    assert result.ingredient_text is None
    assert result.assessment_result is None
    assert result.matched_ingredients == []
    assert result.explanation == (
        "No usable product record was found for this barcode from Open Food Facts, Open Beauty "
        "Facts, or the enrichment fallback."
    )
    assert result.lookup_path == [
        "normalized:99999",
        "stub:attempted",
        "stub:failed",
        "enrichment:attempted",
        "enrichment:failed",
    ]


def test_mock_provider_normalizes_provider_payload():
    provider = MockApiProductLookupProvider(
        settings=ProductLookupProviderSettings(
            provider_name="mock_api",
            base_url="https://provider.example.invalid",
            api_key="secret-token",
        ),
        responses={
            "5012345678900": {
                "code": "5012345678900",
                "brand": "Future Catalog Co",
                "title": "Mock Provider Body Butter",
                "image": "https://cdn.example.invalid/products/5012345678900.png",
                "ingredients_text": "Water, Glycerin, Butyrospermum Parkii Butter",
            }
        },
    )

    product = provider.lookup_by_barcode("5012345678900")

    assert product is not None
    assert product.barcode == "5012345678900"
    assert product.brand_name == "Future Catalog Co"
    assert product.product_name == "Mock Provider Body Butter"
    assert product.image_url == "https://cdn.example.invalid/products/5012345678900.png"
    assert product.ingredient_coverage_status == "complete"
    assert product.source == "mock_api"


def test_open_food_facts_provider_normalizes_provider_payload():
    captured = {}

    def fake_http_get(url, params, headers, timeout):
        captured["url"] = url
        captured["params"] = params
        captured["headers"] = headers
        captured["timeout"] = timeout
        return FakeHttpResponse(
            {
                "status": 1,
                "product": {
                    "code": "737628064502",
                    "product_name": "Almond Butter",
                    "brands": "Example Brand",
                    "ingredients_text": "Almonds, Sea Salt",
                    "image_front_url": "https://images.openfoodfacts.org/front.jpg",
                },
            }
        )

    provider = OpenFoodFactsProductLookupProvider(
        settings=ProductLookupProviderSettings(
            provider_name="open_food_facts",
            base_url="https://world.openfoodfacts.org",
            api_key="",
            user_agent="thats-nuts-tests/1.0 (test@example.com)",
            timeout_seconds=7.5,
        ),
        http_get=fake_http_get,
    )

    product = provider.lookup_by_barcode("737628064502")

    assert product is not None
    assert product.barcode == "737628064502"
    assert product.product_name == "Almond Butter"
    assert product.brand_name == "Example Brand"
    assert product.ingredient_text == "Almonds, Sea Salt"
    assert product.image_url == "https://images.openfoodfacts.org/front.jpg"
    assert product.ingredient_coverage_status == "complete"
    assert product.source == "open_food_facts"
    assert captured["url"] == "https://world.openfoodfacts.org/api/v2/product/737628064502"
    assert "ingredients_text" in captured["params"]["fields"]
    assert captured["headers"]["User-Agent"] == "thats-nuts-tests/1.0 (test@example.com)"
    assert captured["timeout"] == 7.5


def test_open_food_facts_provider_uses_required_default_user_agent():
    captured = {}

    def fake_http_get(url, params, headers, timeout):
        captured["headers"] = headers
        return FakeHttpResponse({"status": 0})

    provider = OpenFoodFactsProductLookupProvider(
        settings=ProductLookupProviderSettings(
            provider_name="open_food_facts",
            base_url="https://world.openfoodfacts.org",
        ),
        http_get=fake_http_get,
    )

    provider.lookup_by_barcode("3017620422003")

    assert captured["headers"]["User-Agent"] == (
        "ThatsNuts/1.0 - contact: support@activeadvantage.co"
    )


def test_open_food_facts_provider_uses_required_user_agent_when_setting_is_blank():
    captured = {}

    def fake_http_get(url, params, headers, timeout):
        captured["headers"] = headers
        return FakeHttpResponse({"status": 0})

    provider = OpenFoodFactsProductLookupProvider(
        settings=ProductLookupProviderSettings(
            provider_name="open_food_facts",
            base_url="https://world.openfoodfacts.org",
            user_agent="",
        ),
        http_get=fake_http_get,
    )

    provider.lookup_by_barcode("3017620422003")

    assert captured["headers"]["User-Agent"] == (
        "ThatsNuts/1.0 - contact: support@activeadvantage.co"
    )


def test_open_food_facts_provider_appends_api_v2_product_path_once():
    captured = {}

    def fake_http_get(url, params, headers, timeout):
        captured["url"] = url
        return FakeHttpResponse({"status": 0})

    provider = OpenFoodFactsProductLookupProvider(
        settings=ProductLookupProviderSettings(
            provider_name="open_food_facts",
            base_url="https://world.openfoodfacts.org/",
        ),
        http_get=fake_http_get,
    )

    provider.lookup_by_barcode("3017620422003")

    assert captured["url"] == "https://world.openfoodfacts.org/api/v2/product/3017620422003"
    assert captured["url"].count("/api/v2/product/") == 1
    assert "/api/v0/" not in captured["url"]


def test_open_beauty_facts_provider_normalizes_provider_payload():
    captured = {}

    def fake_http_get(url, params, headers, timeout):
        captured["url"] = url
        captured["params"] = params
        captured["headers"] = headers
        captured["timeout"] = timeout
        return FakeHttpResponse(
            {
                "status": 1,
                "product": {
                    "code": "3701129800015",
                    "product_name": "Nourishing Face Oil",
                    "brands": "Beauty Brand",
                    "ingredients_text_from_image": "Helianthus Annuus Seed Oil, Juglans Regia Seed Oil",
                    "image_front_small_url": "https://images.openbeautyfacts.org/front-small.jpg",
                },
            }
        )

    provider = OpenBeautyFactsProductLookupProvider(
        settings=ProductLookupProviderSettings(
            provider_name="open_beauty_facts",
            base_url="https://world.openbeautyfacts.org",
            api_key="",
            user_agent="thats-nuts-tests/1.0 (test@example.com)",
            timeout_seconds=6.0,
        ),
        http_get=fake_http_get,
    )

    product = provider.lookup_by_barcode("3701129800015")

    assert product is not None
    assert product.barcode == "3701129800015"
    assert product.product_name == "Nourishing Face Oil"
    assert product.brand_name == "Beauty Brand"
    assert product.ingredient_text == "Helianthus Annuus Seed Oil, Juglans Regia Seed Oil"
    assert product.image_url == "https://images.openbeautyfacts.org/front-small.jpg"
    assert product.ingredient_coverage_status == "complete"
    assert product.source == "open_beauty_facts"
    assert captured["url"] == "https://world.openbeautyfacts.org/api/v2/product/3701129800015"
    assert "ingredients_text_from_image" in captured["params"]["fields"]


def test_open_beauty_facts_provider_uses_required_default_user_agent():
    captured = {}

    def fake_http_get(url, params, headers, timeout):
        captured["headers"] = headers
        return FakeHttpResponse({"status": 0})

    provider = OpenBeautyFactsProductLookupProvider(
        settings=ProductLookupProviderSettings(
            provider_name="open_beauty_facts",
            base_url="https://world.openbeautyfacts.org",
        ),
        http_get=fake_http_get,
    )

    provider.lookup_by_barcode("3017620422003")

    assert captured["headers"]["User-Agent"] == (
        "ThatsNuts/1.0 - contact: support@activeadvantage.co"
    )


def test_open_food_facts_provider_returns_none_when_product_is_missing():
    provider = OpenFoodFactsProductLookupProvider(
        settings=ProductLookupProviderSettings(
            provider_name="open_food_facts",
            base_url="https://world.openfoodfacts.org",
            api_key="",
            user_agent="thats-nuts-tests/1.0 (test@example.com)",
            timeout_seconds=5.0,
        ),
        http_get=lambda *args, **kwargs: FakeHttpResponse({"status": 0}),
    )

    product = provider.lookup_by_barcode("0000000000000")

    assert product is None


def test_open_food_facts_provider_status_one_returns_product_source():
    provider = OpenFoodFactsProductLookupProvider(
        settings=ProductLookupProviderSettings(
            provider_name="open_food_facts",
            base_url="https://world.openfoodfacts.org",
            api_key="",
            timeout_seconds=5.0,
        ),
        http_get=lambda *args, **kwargs: FakeHttpResponse(
            {
                "status": 1,
                "product": {
                    "code": "3017620422003",
                    "product_name": "Nutella",
                    "brands": "Nutella",
                    "ingredients_text": "Sugar, Palm Oil, Hazelnuts, Cocoa",
                },
            }
        ),
    )

    product = provider.lookup_by_barcode("3017620422003")

    assert product is not None
    assert product.barcode == "3017620422003"
    assert product.product_name == "Nutella"
    assert product.brand_name == "Nutella"
    assert product.source == "open_food_facts"
    assert product.ingredient_text == "Sugar, Palm Oil, Hazelnuts, Cocoa"


def test_open_food_facts_empty_non_json_response_falls_through_cleanly():
    food_provider = OpenFoodFactsProductLookupProvider(
        settings=ProductLookupProviderSettings(
            provider_name="open_food_facts",
            base_url="https://world.openfoodfacts.org",
        ),
        http_get=lambda *args, **kwargs: FakeInvalidJsonResponse(),
    )
    beauty_provider = RecordingProductLookupProvider("open_beauty_facts")
    service = ProductLookupService(ChainedProductLookupProvider((food_provider, beauty_provider)))

    response = service.lookup_by_barcode("3017620422003")

    assert response.found is True
    assert response.source == "open_beauty_facts"
    assert beauty_provider.calls == ["3017620422003"]


def test_open_food_facts_provider_falls_back_to_partial_ingredient_list():
    provider = OpenFoodFactsProductLookupProvider(
        settings=ProductLookupProviderSettings(
            provider_name="open_food_facts",
            base_url="https://world.openfoodfacts.org",
            api_key="",
            user_agent="thats-nuts-tests/1.0 (test@example.com)",
            timeout_seconds=5.0,
        ),
        http_get=lambda *args, **kwargs: FakeHttpResponse(
            {
                "status": 1,
                "product": {
                    "code": "1234567890123",
                    "generic_name": " Repair Lotion ",
                    "brands": " Brand A, Brand B, Brand A ",
                    "ingredients_text": "N/A",
                    "image_front_url": "   ",
                    "image_front_small_url": "https://images.openfoodfacts.org/front-small.jpg",
                    "ingredients": [
                        {"text": "Water"},
                        {"text": "Glycerin"},
                        {"id": "en:almond-oil"},
                        {"id": "en:almond-oil"},
                    ],
                },
            }
        ),
    )

    product = provider.lookup_by_barcode("1234567890123")

    assert product is not None
    assert product.product_name == "Repair Lotion"
    assert product.brand_name == "Brand A, Brand B"
    assert product.image_url == "https://images.openfoodfacts.org/front-small.jpg"
    assert product.ingredient_text == "Water, Glycerin, Almond Oil"
    assert product.ingredient_coverage_status == "partial"


def test_product_lookup_service_explains_partial_ingredient_coverage():
    service = ProductLookupService(
        StubProductLookupProvider(
            products={
                "partial-123": {
                    "barcode": "partial-123",
                    "brand_name": "Partial Brand",
                    "product_name": "Partial Product",
                    "image_url": None,
                    "ingredient_text": "Water, Vegetable Oil",
                    "ingredient_coverage_status": "partial",
                    "source": "stub",
                }
            }
        )
    )

    response = service.lookup_by_barcode("partial-123")

    assert response.found is True
    assert response.assessment_result == "possible_nut_derived_ingredient"
    assert response.explanation == (
        "Product data was returned by the configured stub provider. "
        "Only part of the ingredient list was available, so this assessment may be incomplete and "
        "could miss nut-related ingredients that were not returned by the product record. "
        "Matched 1 ingredient that may be nut-derived or too generic to verify confidently."
    )


def test_open_food_facts_provider_retries_transient_request_failure():
    attempts = {"count": 0}

    def fake_http_get(*args, **kwargs):
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise httpx.ReadTimeout("timed out")
        return FakeHttpResponse(
            {
                "status": 1,
                "product": {
                    "code": "9876543210987",
                    "product_name": "Retry Product",
                    "brands_tags": ["example-brand"],
                    "ingredients_text_en": "Water, Glycerin",
                },
            }
        )

    provider = OpenFoodFactsProductLookupProvider(
        settings=ProductLookupProviderSettings(
            provider_name="open_food_facts",
            base_url="https://world.openfoodfacts.org",
            api_key="",
            user_agent="thats-nuts-tests/1.0 (test@example.com)",
            timeout_seconds=5.0,
        ),
        http_get=fake_http_get,
    )

    product = provider.lookup_by_barcode("9876543210987")

    assert attempts["count"] == 2
    assert product is not None
    assert product.product_name == "Retry Product"
    assert product.brand_name == "Example Brand"
    assert product.ingredient_text == "Water, Glycerin"


def test_open_food_facts_provider_raises_after_repeated_request_failure():
    provider = OpenFoodFactsProductLookupProvider(
        settings=ProductLookupProviderSettings(
            provider_name="open_food_facts",
            base_url="https://world.openfoodfacts.org",
            api_key="",
            user_agent="thats-nuts-tests/1.0 (test@example.com)",
            timeout_seconds=5.0,
        ),
        http_get=lambda *args, **kwargs: (_ for _ in ()).throw(httpx.ConnectError("connect failed")),
    )

    with pytest.raises(RuntimeError):
        provider.lookup_by_barcode("1111111111111")


def test_build_product_lookup_provider_supports_mock_api():
    provider = build_product_lookup_provider(
        "mock_api",
        provider_settings=ProductLookupProviderSettings(
            provider_name="mock_api",
            base_url="https://provider.example.invalid",
            api_key="secret-token",
        ),
    )

    assert isinstance(provider, MockApiProductLookupProvider)


def test_build_product_lookup_provider_supports_open_food_facts():
    provider = build_product_lookup_provider(
        "open_food_facts",
        provider_settings=ProductLookupProviderSettings(
            provider_name="open_food_facts",
            base_url="https://world.openfoodfacts.org",
            api_key="",
            user_agent="thats-nuts-tests/1.0 (test@example.com)",
            timeout_seconds=5.0,
        ),
    )

    assert isinstance(provider, OpenFoodFactsProductLookupProvider)


def test_build_product_lookup_provider_supports_open_beauty_facts():
    provider = build_product_lookup_provider(
        "open_beauty_facts",
        provider_settings=ProductLookupProviderSettings(
            provider_name="open_beauty_facts",
            base_url="https://world.openbeautyfacts.org",
            beauty_base_url="https://world.openbeautyfacts.org",
            food_base_url="https://world.openfoodfacts.org",
        ),
    )

    assert isinstance(provider, OpenBeautyFactsProductLookupProvider)


def test_build_product_lookup_provider_supports_food_then_beauty():
    provider = build_product_lookup_provider(
        "food_then_beauty",
        provider_settings=ProductLookupProviderSettings(
            provider_name="food_then_beauty",
            base_url="https://world.openfoodfacts.org",
            beauty_base_url="https://world.openbeautyfacts.org",
            food_base_url="https://world.openfoodfacts.org",
        ),
    )

    assert isinstance(provider, ChainedProductLookupProvider)
    assert [item.provider_name for item in provider.providers] == [
        "open_food_facts",
        "open_beauty_facts",
    ]


def test_build_product_lookup_provider_supports_legacy_beauty_then_food_alias():
    provider = build_product_lookup_provider(
        "beauty_then_food",
        provider_settings=ProductLookupProviderSettings(
            provider_name="beauty_then_food",
            base_url="https://world.openfoodfacts.org",
            beauty_base_url="https://world.openbeautyfacts.org",
            food_base_url="https://world.openfoodfacts.org",
        ),
    )

    assert isinstance(provider, ChainedProductLookupProvider)
    assert [item.provider_name for item in provider.providers] == [
        "open_food_facts",
        "open_beauty_facts",
    ]


def test_runtime_service_maps_single_open_facts_provider_to_food_then_beauty_chain(monkeypatch):
    monkeypatch.setenv("PRODUCT_LOOKUP_PROVIDER", "open_food_facts")
    get_settings.cache_clear()
    get_product_lookup_service.cache_clear()

    service = get_product_lookup_service()

    assert isinstance(service.provider, ChainedProductLookupProvider)
    assert [item.provider_name for item in service.provider.providers] == [
        "open_food_facts",
        "open_beauty_facts",
    ]

    get_product_lookup_service.cache_clear()
    get_settings.cache_clear()


def test_barcode_lookup_open_food_facts_success_does_not_call_enrichment():
    food_provider = RecordingProductLookupProvider("open_food_facts")
    beauty_provider = RecordingProductLookupProvider("open_beauty_facts")
    provider = ChainedProductLookupProvider((food_provider, beauty_provider))
    service = ProductLookupService(provider)

    response = service.lookup_by_barcode(" 737-628-064502 ")

    assert response.found is True
    assert response.source == "open_food_facts"
    assert response.lookup_path == [
        "normalized:737628064502",
        "open_food_facts:attempted",
        "open_food_facts:succeeded",
        "open_beauty_facts:skipped",
        "enrichment:skipped",
    ]
    assert response.product is not None
    assert response.product.source == "open_food_facts"
    assert food_provider.calls == ["737628064502"]
    assert beauty_provider.calls == []


def test_barcode_lookup_nutella_open_food_facts_success_skips_enrichment(temp_database):
    assert prepare_persistence() is True

    food_provider = OpenFoodFactsProductLookupProvider(
        settings=ProductLookupProviderSettings(
            provider_name="open_food_facts",
            base_url="https://world.openfoodfacts.org",
        ),
        http_get=lambda *args, **kwargs: FakeHttpResponse(
            {
                "status": 1,
                "product": {
                    "code": "3017620422003",
                    "product_name": "Nutella",
                    "brands": "Nutella",
                    "ingredients_text": "Sugar, Palm Oil, Hazelnuts, Cocoa",
                },
            }
        ),
    )
    beauty_provider = RecordingProductLookupProvider("open_beauty_facts")
    service = ProductLookupService(ChainedProductLookupProvider((food_provider, beauty_provider)))
    service.enrich_barcode_with_ingredients(
        "3017620422003",
        "Water, Juglans Regia Seed Oil",
        product_name="Validation Product",
        brand_name="Validation Brand",
        source="manual_entry",
    )

    response = service.lookup_by_barcode("3017620422003")

    assert response.found is True
    assert response.source == "open_food_facts"
    assert response.product is not None
    assert response.product.brand_name == "Nutella"
    assert response.product.product_name == "Nutella"
    assert response.ingredient_text == "Sugar, Palm Oil, Hazelnuts, Cocoa"
    assert beauty_provider.calls == []
    assert "enrichment:skipped" in response.lookup_path


def test_barcode_lookup_food_failure_then_beauty_success_does_not_call_enrichment():
    food_provider = RecordingProductLookupProvider("open_food_facts", product=None)
    beauty_provider = RecordingProductLookupProvider("open_beauty_facts")
    provider = ChainedProductLookupProvider((food_provider, beauty_provider))
    service = ProductLookupService(provider)

    response = service.lookup_by_barcode(" 3701129800015 ")

    assert response.found is True
    assert response.source == "open_beauty_facts"
    assert response.lookup_path == [
        "normalized:3701129800015",
        "open_food_facts:attempted",
        "open_food_facts:failed",
        "open_beauty_facts:attempted",
        "open_beauty_facts:succeeded",
        "enrichment:skipped",
    ]
    assert response.product is not None
    assert response.product.source == "open_beauty_facts"
    assert food_provider.calls == ["3701129800015"]
    assert beauty_provider.calls == ["3701129800015"]


def test_barcode_lookup_food_error_then_beauty_success_does_not_call_enrichment():
    food_provider = ErrorRecordingProductLookupProvider("open_food_facts")
    beauty_provider = RecordingProductLookupProvider("open_beauty_facts")
    provider = ChainedProductLookupProvider((food_provider, beauty_provider))
    service = ProductLookupService(provider)

    response = service.lookup_by_barcode("3701129800015")

    assert response.found is True
    assert response.source == "open_beauty_facts"
    assert response.lookup_path == [
        "normalized:3701129800015",
        "open_food_facts:attempted",
        "open_food_facts:failed",
        "open_beauty_facts:attempted",
        "open_beauty_facts:succeeded",
        "enrichment:skipped",
    ]
    assert food_provider.calls == ["3701129800015"]
    assert beauty_provider.calls == ["3701129800015"]


def test_barcode_lookup_source_failures_call_enrichment_cache(temp_database):
    assert prepare_persistence() is True

    service = ProductLookupService(
        ChainedProductLookupProvider(
            (
                RecordingProductLookupProvider("open_food_facts", product=None),
                RecordingProductLookupProvider("open_beauty_facts", product=None),
            )
        )
    )
    service.enrich_barcode_with_ingredients(
        "737628064502",
        "Water, Glycerin, Prunus Amygdalus Dulcis Oil",
        source="manual_entry",
    )

    response = service.lookup_by_barcode("737628064502")

    assert response.found is True
    assert response.source == "enrichment"
    assert response.lookup_path == [
        "normalized:737628064502",
        "open_food_facts:attempted",
        "open_food_facts:failed",
        "open_beauty_facts:attempted",
        "open_beauty_facts:failed",
        "enrichment:attempted",
        "enrichment:succeeded",
    ]
    assert response.product is not None
    assert response.product.source == "manual_entry"
    assert response.ingredient_text == "Water, Glycerin, Prunus Amygdalus Dulcis Oil"


def test_barcode_lookup_ignores_validation_manual_cache_for_real_barcode(temp_database):
    assert prepare_persistence() is True

    service = ProductLookupService(
        ChainedProductLookupProvider(
            (
                RecordingProductLookupProvider("open_food_facts", product=None),
                RecordingProductLookupProvider("open_beauty_facts", product=None),
            )
        )
    )
    service.enrich_barcode_with_ingredients(
        "3017620422003",
        "Water, Juglans Regia Seed Oil",
        product_name="Validation Product",
        brand_name="Validation Brand",
        source="manual_entry",
    )

    response = service.lookup_by_barcode("3017620422003")

    assert response.found is False
    assert response.source == "not_found"
    assert response.product is None
    assert response.ingredient_text is None
    assert "enrichment:failed" in response.lookup_path


def test_barcode_lookup_failed_enrichment_returns_clean_not_found_response():
    service = ProductLookupService(
        ChainedProductLookupProvider(
            (
                RecordingProductLookupProvider("open_food_facts", product=None),
                RecordingProductLookupProvider("open_beauty_facts", product=None),
            )
        )
    )

    response = service.lookup_by_barcode("0000000000000")

    assert response.found is False
    assert response.source == "not_found"
    assert response.lookup_path == [
        "normalized:0000000000000",
        "open_food_facts:attempted",
        "open_food_facts:failed",
        "open_beauty_facts:attempted",
        "open_beauty_facts:failed",
        "enrichment:attempted",
        "enrichment:failed",
    ]
    assert response.product is None
    assert response.ingredient_text is None
    assert response.assessment_result is None
    assert response.matched_ingredients == []


def test_barcode_normalization_happens_before_provider_lookup():
    food_provider = RecordingProductLookupProvider("open_food_facts", product=None)
    beauty_provider = RecordingProductLookupProvider("open_beauty_facts", product=None)
    service = ProductLookupService(ChainedProductLookupProvider((food_provider, beauty_provider)))

    service.lookup_by_barcode(" 0-001234567890 ")

    assert food_provider.calls == ["0001234567890"]
    assert beauty_provider.calls == ["0001234567890"]


def test_lookup_product_route_returns_normalized_product(monkeypatch):
    monkeypatch.setenv("PRODUCT_LOOKUP_PROVIDER", "stub")
    get_settings.cache_clear()
    get_product_lookup_service.cache_clear()
    response = lookup_product(ProductLookupRequest(barcode="0001234567890"))

    assert response.found is True
    assert response.product is not None
    assert response.product.barcode == "0001234567890"
    assert response.product.brand_name == "Thats Nuts Labs"
    assert response.product.product_name == "Sample Almond Body Oil"
    assert response.product.ingredient_coverage_status == "complete"
    assert response.product.source == "stub"
    assert response.ingredient_text == "Caprylic/Capric Triglyceride, Prunus Amygdalus Dulcis Oil"
    assert response.assessment_result == "contains_nut_ingredient"
    assert len(response.matched_ingredients) == 1
    assert "Detected 1 nut-linked ingredient" in response.explanation


def test_lookup_product_route_accepts_allergy_profile_without_breaking_clients(monkeypatch):
    monkeypatch.setenv("PRODUCT_LOOKUP_PROVIDER", "stub")
    get_settings.cache_clear()
    get_product_lookup_service.cache_clear()
    response = lookup_product(
        ProductLookupRequest(
            barcode="0001234567890",
            allergy_profile={"argan": True},
        )
    )

    assert response.found is True
    assert response.assessment_result == "no_nut_ingredient_found"
    assert response.matched_ingredients == []


def test_lookup_product_route_filters_assessment_by_allergy_profile():
    service = ProductLookupService(
        StubProductLookupProvider(
            products={
                "789": {
                    "barcode": "789",
                    "brand_name": "Profile Brand",
                    "product_name": "Profile Product",
                    "image_url": None,
                    "ingredient_text": (
                        "Water, Prunus Amygdalus Dulcis Oil, Argania Spinosa Kernel Oil"
                    ),
                    "ingredient_coverage_status": "complete",
                    "source": "stub",
                }
            }
        )
    )

    response = service.lookup_by_barcode(
        "789",
        allergy_profile=AllergyProfile(argan=True),
    )

    assert response.found is True
    assert response.assessment_result == "contains_nut_ingredient"
    assert len(response.matched_ingredients) == 1
    assert response.matched_ingredients[0].nut_source == "argan"


def test_product_lookup_service_caches_provider_results_and_persists_assessment(temp_database):
    assert prepare_persistence() is True

    service = ProductLookupService(
        StubProductLookupProvider(
            products={
                "321": {
                    "barcode": "321",
                    "brand_name": "Cache Brand",
                    "product_name": "Cache Product",
                    "image_url": "https://images.example.invalid/cache-product.jpg",
                    "ingredient_text": "Water, Glycerin",
                    "ingredient_coverage_status": "complete",
                    "source": "stub",
                }
            }
        )
    )

    first_response = service.lookup_by_barcode("321")
    second_response = service.lookup_by_barcode("321")

    with Session(get_engine()) as session:
        products = session.exec(select(Product).where(Product.barcode == "321")).all()
        scan_history = session.exec(select(ScanHistory).where(ScanHistory.product_id == products[0].id)).all()

    assert first_response.found is True
    assert first_response.assessment_result == "no_nut_ingredient_found"
    assert "Product data was returned by the configured stub provider." in first_response.explanation
    assert "No known nut-linked ingredients from ruleset" in first_response.explanation
    assert second_response.found is True
    assert second_response.assessment_result == "no_nut_ingredient_found"
    assert "Product data was returned by the configured stub provider." in second_response.explanation
    assert "No known nut-linked ingredients from ruleset" in second_response.explanation
    assert len(products) == 1
    assert products[0].product_name == "Cache Product"
    assert len(scan_history) == 2
    assert all(row.result_status == "no_nut_ingredient_found" for row in scan_history)


def test_product_lookup_service_persists_allergy_profile_for_barcode_scan(temp_database):
    assert prepare_persistence() is True

    service = ProductLookupService(
        StubProductLookupProvider(
            products={
                "852": {
                    "barcode": "852",
                    "brand_name": "Profile Brand",
                    "product_name": "Argan Lotion",
                    "image_url": None,
                    "ingredient_text": (
                        "Water, Prunus Amygdalus Dulcis Oil, Argania Spinosa Kernel Oil"
                    ),
                    "ingredient_coverage_status": "complete",
                    "source": "stub",
                }
            }
        )
    )

    response = service.lookup_by_barcode(
        "852",
        allergy_profile=AllergyProfile(argan=True),
    )

    with Session(get_engine()) as session:
        product = session.exec(select(Product).where(Product.barcode == "852")).first()
        scan_history = session.exec(select(ScanHistory).where(ScanHistory.product_id == product.id)).all()
        allergy_profiles = session.exec(select(AllergyProfileRecord)).all()

    assert response.found is True
    assert response.assessment_result == "contains_nut_ingredient"
    assert len(response.matched_ingredients) == 1
    assert response.matched_ingredients[0].nut_source == "argan"
    assert len(scan_history) == 1
    assert scan_history[0].result_status == "contains_nut_ingredient"
    assert len(allergy_profiles) == 1
    assert allergy_profiles[0].argan is True
    assert allergy_profiles[0].almond is False


def test_product_lookup_service_returns_not_found_when_provider_ingredients_are_missing(temp_database):
    assert prepare_persistence() is True

    service = ProductLookupService(
        StubProductLookupProvider(
            products={
                "654": {
                    "barcode": "654",
                    "brand_name": "Sparse Brand",
                    "product_name": "Sparse Product",
                    "image_url": None,
                    "ingredient_text": None,
                    "ingredient_coverage_status": "missing",
                    "source": "stub",
                }
            }
        )
    )

    response = service.lookup_by_barcode("654")

    with Session(get_engine()) as session:
        product = session.exec(select(Product).where(Product.barcode == "654")).first()
        scan_history = session.exec(select(ScanHistory).where(ScanHistory.product_id == product.id)).all()

    assert response.found is False
    assert response.source == "not_found"
    assert response.product is None
    assert response.ingredient_text is None
    assert response.assessment_result is None
    assert response.matched_ingredients == []
    assert response.explanation == (
        "No usable product record was found for this barcode from Open Food Facts, Open Beauty "
        "Facts, or the enrichment fallback."
    )
    assert product is not None
    assert len(scan_history) == 1
    assert scan_history[0].result_status == "cannot_verify"
    assert scan_history[0].submitted_ingredient_text == ""


def test_product_lookup_service_handles_provider_failure_cleanly():
    service = ProductLookupService(FailingProductLookupProvider())

    response = service.lookup_by_barcode("500")

    assert response.found is False
    assert response.product is None
    assert response.ingredient_text is None
    assert response.assessment_result is None
    assert response.matched_ingredients == []
    assert response.explanation == (
        "Product lookup could not be completed because the configured provider did not return "
        "reliable product data for this barcode. Try again in a moment or enter ingredients manually."
    )


def test_enrich_product_route_persists_manual_ingredient_data_and_assessment(temp_database):
    assert prepare_persistence() is True

    response = enrich_product(
        ProductEnrichmentRequest(
            barcode="1112223334445",
            product_name="Manual Rescue Lotion",
            brand_name="Operator Brand",
            ingredient_text="Water, Glycerin, Prunus Amygdalus Dulcis Oil",
            source="text_scan",
        )
    )

    with Session(get_engine()) as session:
        product = session.exec(select(Product).where(Product.barcode == "1112223334445")).first()
        scan_history = session.exec(select(ScanHistory).where(ScanHistory.product_id == product.id)).all()

    assert response.found is True
    assert response.product is not None
    assert response.product.barcode == "1112223334445"
    assert response.product.product_name == "Manual Rescue Lotion"
    assert response.product.brand_name == "Operator Brand"
    assert response.product.ingredient_text == "Water, Glycerin, Prunus Amygdalus Dulcis Oil"
    assert response.product.ingredient_coverage_status == "complete"
    assert response.product.source == "text_scan"
    assert response.ingredient_text == "Water, Glycerin, Prunus Amygdalus Dulcis Oil"
    assert response.assessment_result == "contains_nut_ingredient"
    assert len(response.matched_ingredients) == 1
    assert response.matched_ingredients[0].nut_source == "almond"
    assert "Product data was saved from a locally submitted ingredient list for this barcode." in response.explanation
    assert "Detected 1 nut-linked ingredient" in response.explanation
    assert response.ruleset_version == "2026.04.1"
    assert product is not None
    assert product.source == "text_scan"
    assert product.ingredient_text == "Water, Glycerin, Prunus Amygdalus Dulcis Oil"
    assert len(scan_history) == 1
    assert scan_history[0].result_status == "contains_nut_ingredient"
    assert scan_history[0].submitted_barcode == "1112223334445"
    assert scan_history[0].submitted_ingredient_text == "Water, Glycerin, Prunus Amygdalus Dulcis Oil"


def test_future_lookup_returns_saved_enriched_barcode_data(temp_database):
    assert prepare_persistence() is True

    service = ProductLookupService(StubProductLookupProvider(products={}))

    enrichment_response = service.enrich_barcode_with_ingredients(
        "5556667778881",
        "Water, Glycerin",
        product_name="Saved Product",
        brand_name="Saved Brand",
        source="manual_entry",
    )
    lookup_response = service.lookup_by_barcode("5556667778881")

    assert enrichment_response.found is True
    assert lookup_response.found is True
    assert lookup_response.product is not None
    assert lookup_response.product.barcode == "5556667778881"
    assert lookup_response.product.product_name == "Saved Product"
    assert lookup_response.product.brand_name == "Saved Brand"
    assert lookup_response.product.source == "manual_entry"
    assert lookup_response.ingredient_text == "Water, Glycerin"
    assert lookup_response.assessment_result == "no_nut_ingredient_found"
    assert "Product data was returned from the local barcode enrichment cache." in lookup_response.explanation
    assert "No known nut-linked ingredients from ruleset" in lookup_response.explanation


def test_manual_enrichment_updates_cached_product_with_missing_ingredients(temp_database):
    assert prepare_persistence() is True

    service = ProductLookupService(
        StubProductLookupProvider(
            products={
                "654": {
                    "barcode": "654",
                    "brand_name": "Sparse Brand",
                    "product_name": "Sparse Product",
                    "image_url": None,
                    "ingredient_text": None,
                    "ingredient_coverage_status": "missing",
                    "source": "stub",
                }
            }
        )
    )

    initial_lookup = service.lookup_by_barcode("654")
    enriched_lookup = service.enrich_barcode_with_ingredients(
        "654",
        "Water, Glycerin, Prunus Amygdalus Dulcis Oil",
        source="manual_entry",
    )
    future_lookup = service.lookup_by_barcode("654")

    with Session(get_engine()) as session:
        product = session.exec(select(Product).where(Product.barcode == "654")).first()

    assert initial_lookup.found is False
    assert initial_lookup.assessment_result is None
    assert enriched_lookup.found is True
    assert enriched_lookup.assessment_result == "contains_nut_ingredient"
    assert len(enriched_lookup.matched_ingredients) == 1
    assert future_lookup.found is True
    assert future_lookup.product is not None
    assert future_lookup.product.product_name == "Sparse Product"
    assert future_lookup.product.brand_name == "Sparse Brand"
    assert future_lookup.product.ingredient_text == "Water, Glycerin, Prunus Amygdalus Dulcis Oil"
    assert future_lookup.product.ingredient_coverage_status == "complete"
    assert future_lookup.product.source == "manual_entry"
    assert future_lookup.assessment_result == "contains_nut_ingredient"
    assert product is not None
    assert product.product_name == "Sparse Product"
    assert product.brand_name == "Sparse Brand"
    assert product.ingredient_text == "Water, Glycerin, Prunus Amygdalus Dulcis Oil"
    assert product.ingredient_coverage_status == "complete"
