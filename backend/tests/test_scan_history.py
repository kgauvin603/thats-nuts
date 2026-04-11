import json
import sqlite3

from app.api.routes.check_ingredients import check_ingredients
from app.api.routes.product_lookup import enrich_product, lookup_product
from app.core.config import get_settings
from app.db.session import get_engine
from app.api.routes.scan_history import recent_scan_history
from app.schemas.ingredients import IngredientCheckRequest
from app.schemas.products import ProductEnrichmentRequest, ProductLookupRequest
from app.services.product_lookup import get_product_lookup_service
from app.services.persistence import prepare_persistence


def test_recent_scan_history_returns_manual_and_barcode_checks(temp_database):
    assert prepare_persistence() is True

    check_ingredients(
        IngredientCheckRequest(
            ingredient_text="Water, Glycerin, Prunus Amygdalus Dulcis Oil",
        )
    )
    lookup_product(ProductLookupRequest(barcode="0001234567890"))

    response = recent_scan_history(limit=10)

    assert len(response.items) == 2

    newest_item = response.items[0]
    older_item = response.items[1]

    assert newest_item.barcode == "0001234567890"
    assert newest_item.scan_type == "barcode_lookup"
    assert newest_item.product_name == "Sample Almond Body Oil"
    assert newest_item.brand_name == "Thats Nuts Labs"
    assert newest_item.product_source == "stub"
    assert newest_item.assessment_status == "contains_nut_ingredient"
    assert newest_item.matched_ingredient_summary == "Prunus Amygdalus Dulcis Oil"
    assert newest_item.created_at is not None
    assert "Matched 1 ingredient linked to nut allergy risk." in newest_item.explanation

    assert older_item.scan_type == "manual_ingredient_check"
    assert older_item.barcode is None
    assert older_item.product_name is None
    assert older_item.brand_name is None
    assert older_item.product_source is None
    assert older_item.submitted_ingredient_text == "Water, Glycerin, Prunus Amygdalus Dulcis Oil"
    assert older_item.assessment_status == "contains_nut_ingredient"
    assert older_item.matched_ingredient_summary == "Prunus Amygdalus Dulcis Oil"
    assert older_item.created_at is not None
    assert older_item.explanation == "Matched 1 ingredient linked to nut allergy risk."


def test_recent_scan_history_respects_limit(temp_database):
    assert prepare_persistence() is True

    check_ingredients(
        IngredientCheckRequest(
            ingredient_text="Water, Glycerin, Prunus Amygdalus Dulcis Oil",
        )
    )
    check_ingredients(
        IngredientCheckRequest(
            ingredient_text="Water, Glycerin",
        )
    )

    response = recent_scan_history(limit=1)

    assert len(response.items) == 1
    assert response.items[0].scan_type == "manual_ingredient_check"


def test_recent_scan_history_includes_unsuccessful_barcode_lookups(temp_database):
    assert prepare_persistence() is True

    lookup_product(ProductLookupRequest(barcode="9999999999999"))

    response = recent_scan_history(limit=10)

    assert len(response.items) == 1
    item = response.items[0]
    assert item.scan_type == "barcode_enrichment"
    assert item.barcode == "9999999999999"
    assert item.product_name is None
    assert item.brand_name is None
    assert item.product_source is None
    assert item.submitted_ingredient_text is None
    assert item.assessment_status == "cannot_verify"
    assert item.explanation == (
        "No product record was found for this barcode in the local cache or from the configured "
        "lookup provider."
    )


def test_recent_scan_history_marks_manual_barcode_enrichment(temp_database):
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

    response = recent_scan_history(limit=10)

    assert len(response.items) == 1
    item = response.items[0]
    assert item.scan_type == "barcode_lookup"
    assert item.barcode == "5555555555555"
    assert item.product_name == "Demo Lotion"
    assert item.brand_name == "Demo Brand"
    assert item.product_source == "text_scan"
    assert item.submitted_ingredient_text == "Water, Sweet Almond Oil"


def test_recent_scan_history_migrates_legacy_database_rows(monkeypatch, tmp_path):
    database_path = tmp_path / "legacy.db"
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    cursor.execute(
        """
        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            name VARCHAR NOT NULL,
            brand VARCHAR,
            barcode VARCHAR,
            ingredient_text TEXT,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE scan_history (
            id INTEGER PRIMARY KEY,
            product_id INTEGER,
            submitted_ingredient_text TEXT NOT NULL,
            result_status VARCHAR NOT NULL,
            explanation TEXT,
            matched_ingredients JSON NOT NULL,
            created_at DATETIME NOT NULL,
            scan_type TEXT NOT NULL DEFAULT 'manual_ingredient_check',
            submitted_barcode TEXT
        )
        """
    )
    cursor.execute(
        """
        INSERT INTO products (
            id,
            name,
            brand,
            barcode,
            ingredient_text,
            created_at,
            updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            1,
            "Legacy Lotion",
            "Legacy Brand",
            "1234567890123",
            "Water, Almond Oil",
            "2026-04-01 08:00:00",
            "2026-04-01 08:00:00",
        ),
    )
    cursor.execute(
        """
        INSERT INTO scan_history (
            id,
            product_id,
            submitted_ingredient_text,
            result_status,
            explanation,
            matched_ingredients,
            created_at,
            scan_type,
            submitted_barcode
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            1,
            1,
            "Water, Almond Oil",
            "contains_nut_ingredient",
            "Matched almond oil.",
            json.dumps([{"original_text": "Almond Oil"}]),
            "2026-04-02 08:00:00",
            "barcode_lookup",
            "1234567890123",
        ),
    )
    cursor.execute(
        """
        INSERT INTO scan_history (
            id,
            product_id,
            submitted_ingredient_text,
            result_status,
            explanation,
            matched_ingredients,
            created_at,
            scan_type,
            submitted_barcode
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            2,
            None,
            "Water, Glycerin, Walnut Shell Powder",
            "contains_nut_ingredient",
            "Matched walnut shell powder.",
            json.dumps([{"original_text": "Walnut Shell Powder"}]),
            "2026-04-02 07:00:00",
            "manual_ingredient_check",
            None,
        ),
    )
    connection.commit()
    connection.close()

    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{database_path}")
    monkeypatch.setenv("DATABASE_AUTO_CREATE", "true")
    monkeypatch.setenv("DATABASE_SEED_DATA", "false")

    get_product_lookup_service.cache_clear()
    get_engine.cache_clear()
    get_settings.cache_clear()

    try:
        assert prepare_persistence() is True

        enrich_product(
            ProductEnrichmentRequest(
                barcode="5555555555555",
                product_name="Migrated Demo Lotion",
                brand_name="Demo Brand",
                ingredient_text="Water, Sweet Almond Oil",
                source="text_scan",
            )
        )

        response = recent_scan_history(limit=10)

        assert [item.barcode for item in response.items] == [
            "5555555555555",
            "1234567890123",
            None,
        ]
        assert response.items[0].product_name == "Migrated Demo Lotion"
        assert response.items[0].brand_name == "Demo Brand"
        assert response.items[0].scan_type == "barcode_enrichment"
        assert response.items[0].product_source == "text_scan"
        assert response.items[1].product_name == "Legacy Lotion"
        assert response.items[1].brand_name == "Legacy Brand"
        assert response.items[1].product_source == "manual"
        assert response.items[2].submitted_ingredient_text == (
            "Water, Glycerin, Walnut Shell Powder"
        )
    finally:
        get_product_lookup_service.cache_clear()
        get_engine.cache_clear()
        get_settings.cache_clear()
