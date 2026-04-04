import logging
from contextlib import contextmanager
from functools import lru_cache
from typing import Generator

from sqlmodel import Session, SQLModel, create_engine

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def create_db_engine(database_url: str, echo: bool = False):
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    return create_engine(database_url, echo=echo, connect_args=connect_args)


@lru_cache(maxsize=1)
def get_engine():
    settings = get_settings()
    return create_db_engine(settings.database_url, echo=settings.database_echo)


def initialize_database(engine=None) -> bool:
    settings = get_settings()
    if not settings.database_auto_create:
        return True

    active_engine = engine or get_engine()
    try:
        import app.models  # noqa: F401

        SQLModel.metadata.create_all(active_engine)
        return True
    except Exception:
        logger.exception("Database initialization failed. Continuing without database-backed persistence.")
        return False


def get_session() -> Generator[Session, None, None]:
    with Session(get_engine()) as session:
        yield session


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    with Session(get_engine()) as session:
        yield session
