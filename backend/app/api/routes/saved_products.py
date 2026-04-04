from typing import Optional

from fastapi import APIRouter, Query

from app.schemas.products import SavedProductsResponse
from app.services.persistence import list_saved_products

router = APIRouter()


@router.get("/saved-products", response_model=SavedProductsResponse)
def recent_saved_products(
    limit: int = Query(default=20, ge=1, le=100),
    q: Optional[str] = Query(default=None),
) -> SavedProductsResponse:
    query = q if isinstance(q, str) else None
    return SavedProductsResponse(items=list_saved_products(limit=limit, query=query))
