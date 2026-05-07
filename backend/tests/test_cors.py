from fastapi.testclient import TestClient

from app.main import app


def test_scan_history_preflight_allows_companion_site_origin():
    client = TestClient(app)

    response = client.options(
        "/scan-history",
        headers={
            "Origin": "https://thatsnuts.activeadvantage.co",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert (
        response.headers.get("access-control-allow-origin")
        == "https://thatsnuts.activeadvantage.co"
    )
    allow_methods = response.headers.get("access-control-allow-methods", "")
    assert "GET" in allow_methods
    assert "POST" in allow_methods
    assert "OPTIONS" in allow_methods
