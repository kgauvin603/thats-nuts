import os
from functools import lru_cache

from pydantic import BaseModel

from app.core.product_lookup_constants import DEFAULT_PRODUCT_LOOKUP_USER_AGENT


class Settings(BaseModel):
    app_name: str = "Thats Nuts API"
    environment: str = "dev"
    app_host: str = "0.0.0.0"
    app_port: int = 8002
    database_url: str = "sqlite:///./thatsnuts.db"
    database_echo: bool = False
    database_auto_create: bool = True
    database_seed_data: bool = True
    product_lookup_provider: str = "food_then_beauty"
    product_lookup_beauty_base_url: str = "https://world.openbeautyfacts.org"
    product_lookup_food_base_url: str = "https://world.openfoodfacts.org"
    product_lookup_api_key: str = ""
    product_lookup_user_agent: str = DEFAULT_PRODUCT_LOOKUP_USER_AGENT
    product_lookup_timeout_seconds: float = 5.0


def _read_bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "Thats Nuts API"),
        environment=os.getenv("ENVIRONMENT", "dev"),
        app_host=os.getenv("APP_HOST", "0.0.0.0"),
        app_port=int(os.getenv("APP_PORT", os.getenv("PORT", "8002"))),
        database_url=os.getenv("DATABASE_URL", "sqlite:///./thatsnuts.db"),
        database_echo=_read_bool_env("DATABASE_ECHO", False),
        database_auto_create=_read_bool_env("DATABASE_AUTO_CREATE", True),
        database_seed_data=_read_bool_env("DATABASE_SEED_DATA", True),
        product_lookup_provider=os.getenv("PRODUCT_LOOKUP_PROVIDER", "food_then_beauty"),
        product_lookup_beauty_base_url=os.getenv(
            "PRODUCT_LOOKUP_BEAUTY_BASE_URL",
            "https://world.openbeautyfacts.org",
        ),
        product_lookup_food_base_url=os.getenv(
            "PRODUCT_LOOKUP_FOOD_BASE_URL",
            os.getenv("PRODUCT_LOOKUP_BASE_URL", "https://world.openfoodfacts.org"),
        ),
        product_lookup_api_key=os.getenv("PRODUCT_LOOKUP_API_KEY", ""),
        product_lookup_user_agent=(
            os.getenv("PRODUCT_LOOKUP_USER_AGENT") or DEFAULT_PRODUCT_LOOKUP_USER_AGENT
        ),
        product_lookup_timeout_seconds=float(os.getenv("PRODUCT_LOOKUP_TIMEOUT_SECONDS", "5.0")),
    )


settings = get_settings()
