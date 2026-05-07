from fastapi import APIRouter, Query

from app.schemas.history import MissedBarcodeSummaryResponse, ScanHistoryResponse
from app.services.persistence import list_missed_barcodes, list_recent_scan_history

router = APIRouter()


@router.get("/scan-history", response_model=ScanHistoryResponse)
def recent_scan_history(
    limit: int = Query(default=20, ge=1, le=100),
    include_misses: bool = False,
) -> ScanHistoryResponse:
    return ScanHistoryResponse(items=list_recent_scan_history(limit=limit, include_misses=include_misses))


@router.get("/scan-history/missed-barcodes", response_model=MissedBarcodeSummaryResponse)
def missed_barcode_summary(limit: int = Query(default=20, ge=1, le=100)) -> MissedBarcodeSummaryResponse:
    return MissedBarcodeSummaryResponse(items=list_missed_barcodes(limit=limit))
