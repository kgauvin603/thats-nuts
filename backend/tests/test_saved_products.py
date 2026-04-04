from app.api.routes.product_lookup import lookup_product
from app.api.routes.saved_products import recent_saved_products
from app.schemas.products import NormalizedProduct, ProductLookupRequest
from app.services.persistence import prepare_persistence, upsert_product


def test_recent_saved_products_returns_persisted_products_with_latest_assessment(temp_database):
    assert prepare_persistence() is True

    lookup_product(ProductLookupRequest(barcode="0001234567890"))
    upsert_product(
        NormalizedProduct(
            barcode="1112223334445",
            brand_name="Filter Brand",
            product_name="Saved Product Without Scan",
            image_url=None,
            ingredient_text="Water, Glycerin",
            ingredient_coverage_status="complete",
            source="demo_dataset",
        )
    )

    response = recent_saved_products(limit=10)

    assert len(response.items) == 2

    items_by_barcode = {item.barcode: item for item in response.items}
    scanned_item = items_by_barcode["0001234567890"]
    saved_only_item = items_by_barcode["1112223334445"]

    assert scanned_item.product_name == "Sample Almond Body Oil"
    assert scanned_item.brand_name == "Thats Nuts Labs"
    assert scanned_item.source == "stub"
    assert scanned_item.ingredient_coverage_status == "complete"
    assert scanned_item.ingredient_text == "Caprylic/Capric Triglyceride, Prunus Amygdalus Dulcis Oil"
    assert scanned_item.latest_assessment_status == "contains_nut_ingredient"
    assert scanned_item.latest_matched_ingredient_summary == "Prunus Amygdalus Dulcis Oil"
    assert scanned_item.latest_assessment_explanation is not None
    assert scanned_item.latest_scan_created_at is not None
    assert scanned_item.created_at is not None
    assert scanned_item.updated_at is not None

    assert saved_only_item.product_name == "Saved Product Without Scan"
    assert saved_only_item.brand_name == "Filter Brand"
    assert saved_only_item.source == "demo_dataset"
    assert saved_only_item.latest_assessment_status is None
    assert saved_only_item.latest_assessment_explanation is None
    assert saved_only_item.latest_matched_ingredient_summary is None
    assert saved_only_item.latest_scan_created_at is None


def test_recent_saved_products_supports_simple_query_filter(temp_database):
    assert prepare_persistence() is True

    upsert_product(
        NormalizedProduct(
            barcode="1112223334445",
            brand_name="Filter Brand",
            product_name="Searchable Lotion",
            image_url=None,
            ingredient_text="Water, Glycerin",
            ingredient_coverage_status="complete",
            source="manual",
        )
    )
    upsert_product(
        NormalizedProduct(
            barcode="9998887776665",
            brand_name="Other Brand",
            product_name="Unrelated Serum",
            image_url=None,
            ingredient_text=None,
            ingredient_coverage_status="missing",
            source="manual",
        )
    )

    brand_response = recent_saved_products(limit=10, q="Filter")
    barcode_response = recent_saved_products(limit=10, q="999888")

    assert len(brand_response.items) == 1
    assert brand_response.items[0].barcode == "1112223334445"
    assert brand_response.items[0].product_name == "Searchable Lotion"

    assert len(barcode_response.items) == 1
    assert barcode_response.items[0].barcode == "9998887776665"
    assert barcode_response.items[0].product_name == "Unrelated Serum"
