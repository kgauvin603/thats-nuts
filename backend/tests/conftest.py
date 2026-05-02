import pytest

from app.core.config import get_settings
from app.db.session import get_engine
from app.services.product_lookup import get_product_lookup_service


@pytest.fixture
def temp_database(monkeypatch, tmp_path):
    database_path = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{database_path}")
    monkeypatch.setenv("DATABASE_AUTO_CREATE", "true")
    monkeypatch.setenv("DATABASE_SEED_DATA", "true")
    monkeypatch.setenv("PRODUCT_LOOKUP_PROVIDER", "stub")

    get_product_lookup_service.cache_clear()
    get_engine.cache_clear()
    get_settings.cache_clear()

    yield database_path

    get_product_lookup_service.cache_clear()
    get_engine.cache_clear()
    get_settings.cache_clear()
