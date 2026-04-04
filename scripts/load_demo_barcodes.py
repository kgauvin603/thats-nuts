#!/usr/bin/env python3
"""Load or list deterministic demo barcode products for local backend demos."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND_ROOT = REPO_ROOT / "backend"
DEFAULT_DATASET_PATH = BACKEND_ROOT / "app" / "data" / "demo_barcodes.json"

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.db import initialize_database  # noqa: E402
from app.schemas.products import NormalizedProduct  # noqa: E402
from app.services.persistence import upsert_product  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Load deterministic demo barcode products into the local product cache.",
    )
    parser.add_argument(
        "--dataset",
        default=str(DEFAULT_DATASET_PATH),
        help="Path to the demo barcode dataset JSON file.",
    )
    parser.add_argument(
        "--list-only",
        action="store_true",
        help="Print the dataset without writing it to the database.",
    )
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:8002",
        help="Base URL used when printing example lookup commands.",
    )
    return parser.parse_args()


def load_dataset(dataset_path: Path) -> list[dict]:
    payload = json.loads(dataset_path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("Demo barcode dataset must be a JSON array.")
    return payload


def print_dataset(entries: list[dict], base_url: str) -> None:
    print("Demo barcode dataset")
    print("====================")
    for entry in entries:
        print(
            f"{entry['barcode']}  {entry['expected_status']}  "
            f"{entry['product_name']}"
        )
        print(f"  reason: {entry['reason']}")
    print()
    print("Example lookup commands")
    print("=======================")
    for entry in entries:
        print(
            "curl -X POST "
            f"{base_url.rstrip('/')}/lookup-product "
            "-H 'Content-Type: application/json' "
            f"-d '{{\"barcode\":\"{entry['barcode']}\"}}'"
        )


def main() -> int:
    args = parse_args()
    dataset_path = Path(args.dataset).resolve()
    entries = load_dataset(dataset_path)

    if args.list_only:
        print_dataset(entries, args.base_url)
        return 0

    if not initialize_database():
        print("Database initialization failed; demo barcode cache was not loaded.", file=sys.stderr)
        return 1

    loaded_count = 0
    for entry in entries:
        product = NormalizedProduct(
            barcode=entry["barcode"],
            brand_name=entry.get("brand_name"),
            product_name=entry.get("product_name"),
            image_url=entry.get("image_url"),
            ingredient_text=entry.get("ingredient_text"),
            ingredient_coverage_status=entry.get("ingredient_coverage_status", "unknown"),
            source=entry.get("source", "demo_dataset"),
        )
        upsert_product(product)
        loaded_count += 1
        print(
            f"Loaded {product.barcode} -> {product.product_name} "
            f"(expected {entry['expected_status']})"
        )

    print()
    print(f"Loaded {loaded_count} demo barcodes into the local product cache.")
    print_dataset(entries, args.base_url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
