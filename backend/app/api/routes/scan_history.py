from fastapi import APIRouter, Query

from app.schemas.history import (
    GroupedScanHistoryResponse,
    InconsistentBarcodeSummaryResponse,
    MissedBarcodeSummaryResponse,
    ScanHistoryResponse,
)
from app.services.persistence import (
    list_grouped_useful_scan_history,
    list_inconsistent_barcodes,
    list_missed_barcodes,
    list_recent_scan_history,
)

router = APIRouter()


@router.get("/scan-history", response_model=ScanHistoryResponse)
def recent_scan_history(
    limit: int = Query(default=20, ge=1, le=100),
    include_misses: bool = False,
    include_inconsistent: bool = False,
) -> ScanHistoryResponse:
    return ScanHistoryResponse(
        items=list_recent_scan_history(
            limit=limit,
            include_misses=include_misses,
            include_inconsistent=include_inconsistent,
        )
    )


@router.get("/scan-history/grouped", response_model=GroupedScanHistoryResponse)
def grouped_scan_history(limit: int = Query(default=20, ge=1, le=100)) -> GroupedScanHistoryResponse:
    return GroupedScanHistoryResponse(items=list_grouped_useful_scan_history(limit=limit))


@router.get(
    "/scan-history/inconsistent-barcodes",
    response_model=InconsistentBarcodeSummaryResponse,
)
def inconsistent_barcode_summary(
    limit: int = Query(default=20, ge=1, le=100),
) -> InconsistentBarcodeSummaryResponse:
    return InconsistentBarcodeSummaryResponse(items=list_inconsistent_barcodes(limit=limit))


@router.get("/scan-history/missed-barcodes", response_model=MissedBarcodeSummaryResponse)
def missed_barcode_summary(limit: int = Query(default=20, ge=1, le=100)) -> MissedBarcodeSummaryResponse:
    return MissedBarcodeSummaryResponse(items=list_missed_barcodes(limit=limit))
