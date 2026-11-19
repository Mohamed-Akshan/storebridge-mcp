from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

from core.config import settings


Base = declarative_base()

DATABASE_URLS = {
    "liberty": settings.liberty_database_url,
    "galle_face": settings.galle_face_database_url,
    "pettah": settings.pettah_database_url,
}

BRANCH_NAMES = {
    "liberty": "Liberty Plaza, Kollupitiya",
    "galle_face": "One Galle Face Mall",
    "pettah": "Main Street, Pettah",
}

engines = {
    branch: create_engine(url, pool_pre_ping=True)
    for branch, url in DATABASE_URLS.items()
}

SessionLocal = {
    branch: sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )
    for branch, engine in engines.items()
}


@contextmanager
def session_for(branch: str, writable: bool = False):
    if branch not in SessionLocal:
        raise ValueError("Unknown branch")

    session = SessionLocal[branch]()

    try:
        if not writable:
            session.execute(text("SET TRANSACTION READ ONLY"))

        yield session
    finally:
        session.close()
