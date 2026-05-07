from pathlib import Path
from uuid import uuid4

from typing import Optional

from fastapi import APIRouter, File, HTTPException, Query, UploadFile, status

from app.core.config import get_settings
from app.schemas.products import ProductPhotoUploadResponse, SavedProductsResponse
from app.services.persistence import list_saved_products, save_product_photo
from app.services.product_lookup import normalize_barcode

router = APIRouter()

SUPPORTED_IMAGE_TYPES = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
}
HEIC_IMAGE_TYPES = {"image/heic", "image/heif"}


@router.get("/saved-products", response_model=SavedProductsResponse)
def recent_saved_products(
    limit: int = Query(default=20, ge=1, le=100),
    q: Optional[str] = Query(default=None),
) -> SavedProductsResponse:
    query = q if isinstance(q, str) else None
    return SavedProductsResponse(items=list_saved_products(limit=limit, query=query))


@router.post("/products/{barcode}/photo", response_model=ProductPhotoUploadResponse)
async def upload_product_photo(
    barcode: str,
    photo: UploadFile = File(...),
    overwrite: bool = Query(default=False),
) -> ProductPhotoUploadResponse:
    settings = get_settings()
    normalized_barcode = normalize_barcode(barcode)
    content_type = (photo.content_type or "").lower()

    if content_type in HEIC_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="HEIC uploads are not supported yet. Please upload JPEG, PNG, or WebP.",
        )

    extension = SUPPORTED_IMAGE_TYPES.get(content_type)
    if extension is None:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only JPEG, PNG, and WebP images are supported.",
        )

    file_bytes = await photo.read(settings.product_photo_max_bytes + 1)
    if len(file_bytes) > settings.product_photo_max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Product photos must be {settings.product_photo_max_bytes // (1024 * 1024)} MB or smaller.",
        )

    upload_dir = Path(settings.product_photo_upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{normalized_barcode}-{uuid4().hex}.{extension}"
    destination = upload_dir / filename
    destination.write_bytes(file_bytes)

    image_url = (
        f"{settings.public_api_base_url.rstrip('/')}{settings.product_photo_upload_url_path}/{filename}"
    )
    result = save_product_photo(
        barcode=normalized_barcode,
        image_url=image_url,
        overwrite=overwrite,
    )
    if result is None:
        destination.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No saved product or scan history was found for this barcode.",
        )

    if not result.updated:
        destination.unlink(missing_ok=True)

    return ProductPhotoUploadResponse(
        barcode=result.barcode,
        image_url=result.image_url,
        updated=result.updated,
        message=result.message,
    )
