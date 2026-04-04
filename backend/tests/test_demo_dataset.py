import json
from pathlib import Path


def test_demo_barcode_dataset_covers_all_expected_statuses():
    dataset_path = Path("backend/app/data/demo_barcodes.json")
    entries = json.loads(dataset_path.read_text(encoding="utf-8"))

    statuses = {entry["expected_status"] for entry in entries}

    assert statuses == {
        "contains_nut_ingredient",
        "possible_nut_derived_ingredient",
        "no_nut_ingredient_found",
        "cannot_verify",
    }

    for entry in entries:
        assert entry["barcode"].isdigit()
        assert len(entry["barcode"]) >= 8
        assert entry["product_name"]
        assert entry["brand_name"]
        assert entry["reason"]
        assert entry["ingredient_coverage_status"] in {"complete", "missing"}
