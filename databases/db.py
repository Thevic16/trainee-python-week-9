import os

from sqlmodel import create_engine, Session
from dotenv import load_dotenv

# Initialize environ
# Load virtual variables
from utilities.logger import Logger

load_dotenv()  # take environment variables from .env.

database_url = ''
app_state = os.environ.get("APP_STATE")
Logger.info(f"app_state:{app_state}")

if app_state == "Deploy":
    database_url_orig = os.environ.get("DATABASE_URL")
    database_url = database_url_orig.replace("postgres", "postgresql")
elif app_state == "Local":
    database_url = os.environ.get("DATABASE_URL")

Logger.info(f"database_url:{database_url}")

engine = create_engine(database_url, echo=True)


def get_db_session():
    return Session(bind=engine)
