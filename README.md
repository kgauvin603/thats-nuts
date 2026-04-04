# Thats Nuts

A nut-allergy ingredient checker for skincare and cosmetic products.

## What it is

Thats Nuts is a mobile-first project that helps people identify whether a skincare or cosmetic product contains nut-derived ingredients.

The long-term goal is a barcode-scanning app similar in spirit to Yuka, but focused specifically on nut allergy risk in beauty and personal care products.

## MVP focus

The first milestone is not barcode scanning.

The first milestone is a working ingredient intelligence engine that can:

- accept a pasted ingredient list
- normalize cosmetic ingredient names
- check those ingredients against a nut-risk dictionary
- return one of four results:
  - contains_nut_ingredient
  - possible_nut_derived_ingredient
  - no_nut_ingredient_found
  - cannot_verify

## Why this order

Barcode scanning is only the front door.

The real product value is the rules engine and ingredient normalization layer. If that logic is weak, the scanner does not help.

## Current scope

This repository currently includes:

- FastAPI backend scaffold
- ingredient parsing service
- starter nut rules engine
- PostgreSQL-ready persistence layer with SQLModel
- product lookup cache and scan history persistence
- seed ingredient dictionary
- health endpoint
- ingredient check endpoint
- product lookup endpoint
- unit tests
- basic CI workflow

## Planned phases

### Phase 1
Manual ingredient checker API

### Phase 2
Product lookup by UPC / EAN

### Phase 3
Mobile scanner flow

### Phase 4
Admin review tools and correction workflow

## Project structure

- `backend/` FastAPI service and tests
- `docs/` product and architecture notes
- `mobile/` reserved for future Flutter app
- `scripts/` local helper scripts

## Local backend quick start

```bash
cp backend/.env.example backend/.env
./scripts/run_backend.sh
```

For database-backed local development, use [backend/.env.example](/mnt/apps/ThatsNuts/backend/.env.example) as the reference configuration. The backend defaults to `sqlite:///./thatsnuts.db`, and PostgreSQL can be enabled with `DATABASE_URL=postgresql+psycopg://...`.

For Oracle Linux 9 service-style deployment, see [backend/README.md](/mnt/apps/ThatsNuts/backend/README.md) for exact startup steps and a `systemd` unit example.

For deterministic product lookup demos, the backend also ships a small barcode dataset plus a preload helper. See the `Demo barcodes` section in [backend/README.md](/mnt/apps/ThatsNuts/backend/README.md).

For backend operator testing without a separate frontend build, open `http://127.0.0.1:8002/test-ui` after starting the API. The page exposes health, ingredient checks, barcode lookups, and recent scan history using the live backend routes; see the `Internal test UI` section in [backend/README.md](/mnt/apps/ThatsNuts/backend/README.md).

## Demo barcodes

The current lookup flow checks the local product cache before calling the configured provider. That makes the checked-in demo barcode dataset reliable for local demos and test runs without changing provider behavior.

The dataset lives at [demo_barcodes.json](/mnt/apps/ThatsNuts/backend/app/data/demo_barcodes.json). Each entry includes:

- `barcode`
- `product_name`
- `expected_status`
- `reason`

Recommended demo flow:

```bash
cp backend/.env.example backend/.env
./scripts/run_backend.sh
backend/.venv/bin/python scripts/load_demo_barcodes.py
```

That seeds the local product cache with four known cases:

- `9900000000001` -> `contains_nut_ingredient`
- `9900000000002` -> `possible_nut_derived_ingredient`
- `9900000000003` -> `no_nut_ingredient_found`
- `9900000000004` -> `cannot_verify`

You can then test them in either of these ways:

```bash
backend/.venv/bin/python scripts/load_demo_barcodes.py --list-only
```

```bash
curl -X POST http://127.0.0.1:8002/lookup-product \
  -H "Content-Type: application/json" \
  -d '{"barcode":"9900000000001"}'
```

Or open `http://127.0.0.1:8002/test-ui` and paste one of the demo barcodes into the `Barcode Lookup` panel.

Health check:

```bash
curl http://127.0.0.1:8002/health
```

Ingredient check example:

```bash
curl -X POST http://127.0.0.1:8002/check-ingredients \
  -H "Content-Type: application/json" \
  -d '{
    "ingredient_text": "Water, Glycerin, Prunus Amygdalus Dulcis Oil, Fragrance"
  }'
```

## Example response

```json
{
  "status": "contains_nut_ingredient",
  "matched_ingredients": [
    {
      "original_text": "Prunus Amygdalus Dulcis Oil",
      "normalized_name": "prunus amygdalus dulcis oil",
      "nut_source": "almond",
      "confidence": "high",
      "reason": "Known almond-derived cosmetic ingredient"
    }
  ],
  "explanation": "Matched 1 ingredient linked to nut allergy risk."
}
```

## Safety note

This project is intended to help identify nut-related ingredients from available label data. It does not guarantee medical safety, cross-contact safety, or completeness of manufacturer disclosures.

## Persistence notes

- `POST /check-ingredients` keeps the existing seed-rule behavior and now writes scan history and allergy-profile records when the database is available.
- `POST /lookup-product` now caches normalized products in the database by barcode.
- Startup creates tables automatically when `DATABASE_AUTO_CREATE=true` and seeds normalized ingredient tables when `DATABASE_SEED_DATA=true`.
- `POST /lookup-product` can now use a real provider-backed integration when `PRODUCT_LOOKUP_PROVIDER=open_food_facts`.

## Next build target

- improve the first real barcode provider with retries, better normalization, and refresh rules
- add admin workflows for reviewing ingredient mappings in the database
- scaffold Flutter mobile app
