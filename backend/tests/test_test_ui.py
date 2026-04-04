from app.api.routes.internal_ui import build_test_ui_html, render_test_ui
from app.core.config import settings


def test_test_ui_page_renders():
    response = render_test_ui()

    assert response.status_code == 200
    body = response.body.decode("utf-8")
    assert "Thats Nuts Internal Test UI" in body
    assert "Backend Health" in body
    assert "Active Lookup Provider" in body
    assert settings.product_lookup_provider in body
    assert "Check Ingredients" in body
    assert "Lookup Barcode" in body
    assert "Recent Scan History" in body
    assert "Saved Products" in body
    assert "/health" in body
    assert "/check-ingredients" in body
    assert "/lookup-product" in body
    assert "/scan-history?limit=10" in body
    assert "/saved-products?limit=20" in body
    assert "Manual ingredient check" in body
    assert "Matched Summary" in body
    assert "Lookup Summary" in body
    assert "Matched Ingredients" in body
    assert "Assessment Summary" in body
    assert "Inspect Product Details" in body
    assert "Raw Product JSON" in body
    assert "Raw JSON" in body


def test_build_test_ui_html_includes_config_values():
    body = build_test_ui_html()

    assert settings.environment in body
    assert settings.product_lookup_provider in body
    assert "__APP_ENVIRONMENT__" not in body
    assert "__PRODUCT_LOOKUP_PROVIDER__" not in body
