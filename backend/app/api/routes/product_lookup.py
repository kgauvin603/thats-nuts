from fastapi import APIRouter

from app.schemas.products import ProductLookupRequest, ProductLookupResponse
from app.services.product_lookup import get_product_lookup_service

router = APIRouter()


@router.post("/lookup-product", response_model=ProductLookupResponse)
def lookup_product(payload: ProductLookupRequest) -> ProductLookupResponse:
    service = get_product_lookup_service()
    return service.lookup_by_barcode(
        payload.barcode,
        allergy_profile=payload.allergy_profile,
    )
