# Product Spec

## Working name
Thats Nuts

## Problem
Consumers with peanut or tree nut allergies have limited tools for checking skincare and cosmetic ingredient labels quickly and consistently.

## MVP goal
Allow a user to paste an ingredient list and receive a nut-risk result.

## Output states
- contains_nut_ingredient
- possible_nut_derived_ingredient
- no_nut_ingredient_found
- cannot_verify

## Initial user flow
1. User submits ingredient text
2. Backend parses ingredients
3. Rules engine checks known nut mappings
4. API returns result and matched ingredients

## Out of scope for first commit
- barcode scanning
- OCR
- external product APIs
- user accounts
- mobile app
