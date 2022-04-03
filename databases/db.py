import os

from sqlmodel import create_engine, Session

DATABASE_URL = os.environ.get("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=True)


def get_db_session():
    return Session(bind=engine)
