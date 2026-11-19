from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.config import settings


def build_auth_engine():
    if not settings.auth_database_url:
        raise RuntimeError("AUTH_DATABASE_URL is missing in .env")

    return create_engine(
        settings.auth_database_url,
        pool_pre_ping=True,
        pool_timeout=5,
        connect_args={"connect_timeout": 5},
    )


engine = build_auth_engine()
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
