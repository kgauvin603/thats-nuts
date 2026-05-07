import importlib
from pathlib import Path

from fastapi.testclient import TestClient

from app.api.routes.product_lookup import enrich_product
from app.api.routes.scan_history import recent_scan_history
from app.schemas.products import ProductEnrichmentRequest, ProductLookupRequest
from app.services.persistence import prepare_persistence

PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc````\x00\x00"
    b"\x00\x05\x00\x01\xa5\xf6E@\x00\x00\x00\x00IEND\xaeB`\x82"
)


def _build_client() -> TestClient:
    import app.core.config as config_module
    import app.main as main_module

    importlib.reload(config_module)
    importlib.reload(main_module)
    return TestClient(main_module.app)


def test_product_photo_upload_rejects_non_image_content(temp_database):
    assert prepare_persistence() is True
    enrich_product(
        ProductEnrichmentRequest(
            barcode="5555555555555",
            product_name="Demo Lotion",
            brand_name="Demo Brand",
            ingredient_text="Water, Sweet Almond Oil",
            source="text_scan",
        )
    )

    client = _build_client()
    response = client.post(
        "/products/5555555555555/photo",
        files={"photo": ("notes.txt", b"not-an-image", "text/plain")},
    )

    assert response.status_code == 415
    assert response.json()["detail"] == "Only JPEG, PNG, and WebP images are supported."


def test_product_photo_upload_rejects_oversized_files(temp_database):
    assert prepare_persistence() is True
    enrich_product(
        ProductEnrichmentRequest(
            barcode="5555555555555",
            product_name="Demo Lotion",
            brand_name="Demo Brand",
            ingredient_text="Water, Sweet Almond Oil",
            source="text_scan",
        )
    )

    client = _build_client()
    response = client.post(
        "/products/5555555555555/photo",
        files={
            "photo": (
                "large.png",
                b"\x89PNG" + b"x" * (8 * 1024 * 1024),
                "image/png",
            )
        },
    )

    assert response.status_code == 413
    assert "8 MB or smaller" in response.json()["detail"]


def test_product_photo_upload_saves_valid_image_and_updates_history(temp_database):
    assert prepare_persistence() is True
    enrich_product(
        ProductEnrichmentRequest(
            barcode="5555555555555",
            product_name="Demo Lotion",
            brand_name="Demo Brand",
            ingredient_text="Water, Sweet Almond Oil",
            source="text_scan",
        )
    )

    client = _build_client()
    response = client.post(
        "/products/5555555555555/photo",
        files={"photo": ("photo.png", PNG_BYTES, "image/png")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["barcode"] == "5555555555555"
    assert payload["updated"] is True
    assert payload["message"] == "Product photo saved."
    assert payload["image_url"].startswith(
        "https://api.thatsnuts.activeadvantage.co/uploads/product_photos/5555555555555-"
    )

    uploaded_path = Path(temp_database.parent / "uploads" / "product_photos")
    assert len(list(uploaded_path.iterdir())) == 1

    history = recent_scan_history(limit=10)
    assert len(history.items) == 1
    assert history.items[0].image_url == payload["image_url"]


def test_product_photo_upload_does_not_overwrite_existing_image_without_flag(temp_database):
    assert prepare_persistence() is True

    client = _build_client()
    lookup_response = client.post(
        "/lookup-product",
        json={"barcode": "0001234567890"},
    )
    assert lookup_response.status_code == 200
    original_image_url = lookup_response.json()["product"]["image_url"]

    response = client.post(
        "/products/0001234567890/photo",
        files={"photo": ("photo.png", PNG_BYTES, "image/png")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["updated"] is False
    assert payload["image_url"] == original_image_url

    history = recent_scan_history(limit=10)
    assert history.items[0].image_url == original_image_url


def test_product_photo_upload_overwrites_existing_image_when_requested(temp_database):
    assert prepare_persistence() is True

    client = _build_client()
    lookup_response = client.post(
        "/lookup-product",
        json={"barcode": "0001234567890"},
    )
    assert lookup_response.status_code == 200
    original_image_url = lookup_response.json()["product"]["image_url"]

    response = client.post(
        "/products/0001234567890/photo?overwrite=true",
        files={"photo": ("photo.png", PNG_BYTES, "image/png")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["updated"] is True
    assert payload["image_url"] != original_image_url

    history = recent_scan_history(limit=10)
    assert history.items[0].image_url == payload["image_url"]


def test_product_photo_upload_normalizes_barcode(temp_database):
    assert prepare_persistence() is True
    enrich_product(
        ProductEnrichmentRequest(
            barcode="5555555555555",
            product_name="Demo Lotion",
            brand_name="Demo Brand",
            ingredient_text="Water, Sweet Almond Oil",
            source="text_scan",
        )
    )

    client = _build_client()
    response = client.post(
        "/products/5555 5555-55555/photo",
        files={"photo": ("photo.png", PNG_BYTES, "image/png")},
    )

    assert response.status_code == 200
    assert response.json()["barcode"] == "5555555555555"


def test_product_photo_upload_preflight_allows_companion_site_origin(temp_database):
    assert prepare_persistence() is True

    client = _build_client()
    response = client.options(
        "/products/5555555555555/photo",
        headers={
            "Origin": "https://thatsnuts.activeadvantage.co",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code == 200
    assert (
        response.headers.get("access-control-allow-origin")
        == "https://thatsnuts.activeadvantage.co"
    )
