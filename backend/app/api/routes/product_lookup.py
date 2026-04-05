from fastapi import APIRouter

from app.schemas.products import (
    ProductEnrichmentRequest,
    ProductLookupRequest,
    ProductLookupResponse,
)
from app.services.product_lookup import get_product_lookup_service

router = APIRouter()


@router.post("/lookup-product", response_model=ProductLookupResponse)
def lookup_product(payload: ProductLookupRequest) -> ProductLookupResponse:
    service = get_product_lookup_service()
    return service.lookup_by_barcode(
        payload.barcode,
        allergy_profile=payload.allergy_profile,
    )


@router.post("/enrich-product", response_model=ProductLookupResponse)
def enrich_product(payload: ProductEnrichmentRequest) -> ProductLookupResponse:
    service = get_product_lookup_service()
    return service.enrich_barcode_with_ingredients(
        payload.barcode,
        payload.ingredient_text,
        product_name=payload.product_name,
        brand_name=payload.brand_name,
        source=payload.source,
        allergy_profile=payload.allergy_profile,
    )
