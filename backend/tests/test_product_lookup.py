import httpx
import pytest
from sqlmodel import Session, select

from app.api.routes.product_lookup import enrich_product, lookup_product
from app.db.session import get_engine
from app.models import AllergyProfileRecord, Product, ScanHistory
from app.schemas.ingredients import AllergyProfile
from app.schemas.products import ProductEnrichmentRequest, ProductLookupRequest
from app.services.product_lookup import (
    MockApiProductLookupProvider,
    OpenFoodFactsProductLookupProvider,
    ProductLookupProvider,
    ProductLookupProviderSettings,
    ProductLookupService,
    StubProductLookupProvider,
    build_product_lookup_provider,
)
from app.services.persistence import prepare_persistence


class FailingProductLookupProvider(ProductLookupProvider):
    provider_name = "failing"

    def lookup_by_barcode(self, barcode: str):
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
        "No product record was found for this barcode in the local cache or from the configured "
        "lookup provider."
    )


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


def test_lookup_product_route_returns_normalized_product():
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
    assert "Matched 1 ingredient linked to nut allergy risk." in response.explanation


def test_lookup_product_route_accepts_allergy_profile_without_breaking_clients():
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
    assert first_response.explanation == (
        "Product data was returned by the configured stub provider. "
        "No nut-derived ingredients were matched in the provided ingredient list."
    )
    assert second_response.found is True
    assert second_response.assessment_result == "no_nut_ingredient_found"
    assert second_response.explanation == (
        "Product data was returned from the local product cache. "
        "No nut-derived ingredients were matched in the provided ingredient list."
    )
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


def test_product_lookup_service_returns_cannot_verify_when_ingredients_are_missing(temp_database):
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

    assert response.found is True
    assert response.product is not None
    assert response.ingredient_text is None
    assert response.assessment_result == "cannot_verify"
    assert response.matched_ingredients == []
    assert response.explanation == (
        "Product data was returned by the configured stub provider. "
        "A product record was found, but it did not include a usable ingredient list. This product "
        "cannot be verified until a full ingredient list is available."
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
    assert response.explanation == (
        "Product data was saved from a locally submitted ingredient list for this barcode. "
        "Matched 1 ingredient linked to nut allergy risk."
    )
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
    assert lookup_response.explanation == (
        "Product data was returned from the local barcode enrichment cache. "
        "No nut-derived ingredients were matched in the provided ingredient list."
    )


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

    assert initial_lookup.found is True
    assert initial_lookup.assessment_result == "cannot_verify"
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
