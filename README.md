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
- seed ingredient dictionary
- health endpoint
- ingredient check endpoint
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
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Ingredient check example:

```bash
curl -X POST http://127.0.0.1:8000/check-ingredients \
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

## Next build target

- persist rules in PostgreSQL
- add product lookup cache
- add barcode lookup service
- scaffold Flutter mobile app
