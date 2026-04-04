from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.check_ingredients import router as check_ingredients_router
from app.api.routes.product_lookup import router as product_lookup_router
from app.api.routes.saved_products import router as saved_products_router
from app.api.routes.scan_history import router as scan_history_router
from app.api.routes.internal_ui import router as internal_ui_router
from app.core.config import settings
from app.services.persistence import prepare_persistence


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.database_ready = prepare_persistence()
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)

app.include_router(health_router)
app.include_router(check_ingredients_router)
app.include_router(product_lookup_router)
app.include_router(saved_products_router)
app.include_router(scan_history_router)
app.include_router(internal_ui_router)
