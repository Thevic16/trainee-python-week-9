import os

from sqlmodel import create_engine, Session

DATABASE_URL_ORIG = os.environ.get("DATABASE_URL")

DATABASE_URL = DATABASE_URL_ORIG.replace("postgres", "postgresql")

engine = create_engine(DATABASE_URL, echo=True)


def get_db_session():
    return Session(bind=engine)
