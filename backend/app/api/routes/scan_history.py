from fastapi import APIRouter, Query

from app.schemas.history import ScanHistoryResponse
from app.services.persistence import list_recent_scan_history

router = APIRouter()


@router.get("/scan-history", response_model=ScanHistoryResponse)
def recent_scan_history(limit: int = Query(default=20, ge=1, le=100)) -> ScanHistoryResponse:
    return ScanHistoryResponse(items=list_recent_scan_history(limit=limit))
