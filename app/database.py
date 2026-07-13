from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings


Base = declarative_base()


def get_engine(database_url: str = None):
    return create_engine(database_url or settings.DATABASE_URL, echo=True)


def get_sessionmaker(engine=None):
    if engine is None:
        engine = get_engine()

    return sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )


engine = get_engine()
SessionLocal = get_sessionmaker(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()