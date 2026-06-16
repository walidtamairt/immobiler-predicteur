from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base, sessionmaker

from backend.config.settings import get_settings
from backend.utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)

Base = declarative_base()

PRIMARY_DATABASE_URL = settings.database_url or "sqlite:///./test_real_estate.db"
FALLBACK_DATABASE_URL = settings.database_fallback_url


def _build_connect_args(database_url: str) -> dict:
    connect_args = {}
    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    elif database_url:
        connect_args["connect_timeout"] = settings.database_connect_timeout
        if "sslmode=" not in database_url:
            connect_args["sslmode"] = "require"
    return connect_args


def _build_engine(database_url: str):
    return create_engine(
        database_url,
        future=True,
        pool_pre_ping=True,
        connect_args=_build_connect_args(database_url),
    )


engine = _build_engine(PRIMARY_DATABASE_URL)
_fallback_engine = None
if FALLBACK_DATABASE_URL and FALLBACK_DATABASE_URL != PRIMARY_DATABASE_URL:
    _fallback_engine = _build_engine(FALLBACK_DATABASE_URL)

SessionLocal = sessionmaker(autoflush=False, autocommit=False, future=True)
SessionLocal.configure(bind=engine)

_primary_verified = PRIMARY_DATABASE_URL.startswith("sqlite")
_fallback_active = False


def _activate_fallback(primary_error: Exception) -> bool:
    global engine, _primary_verified, _fallback_active

    if _fallback_engine is None:
        logger.warning("Primary database is unavailable and no fallback is configured: %s", primary_error)
        return False

    fallback_session = sessionmaker(
        bind=_fallback_engine,
        autoflush=False,
        autocommit=False,
        future=True,
    )()
    try:
        fallback_session.execute(text("SELECT 1"))
    except SQLAlchemyError as fallback_error:
        fallback_session.rollback()
        logger.warning(
            "Primary database is unavailable (%s) and fallback database could not be reached (%s).",
            primary_error,
            fallback_error,
        )
        return False
    finally:
        fallback_session.close()

    engine = _fallback_engine
    SessionLocal.configure(bind=engine)
    _primary_verified = True
    _fallback_active = True
    logger.warning("Primary database is unavailable. Falling back to local database: %s", FALLBACK_DATABASE_URL)
    return True


def ensure_database_ready() -> None:
    global _primary_verified

    if _primary_verified:
        return

    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        _primary_verified = True
    except SQLAlchemyError as primary_error:
        db.rollback()
        if not _activate_fallback(primary_error):
            raise
    finally:
        db.close()


def get_db():
    ensure_database_ready()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
