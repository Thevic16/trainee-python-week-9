from fastapi import FastAPI, Request, Response
from sqlalchemy.exc import IntegrityError
from sqlmodel import SQLModel
from starlette.responses import JSONResponse

from databases.db import engine, get_db_session

from utilities.logger import Logger

# Import routes
from routers import users, security, films, persons, rents

# Redis db imports
from fastapi_redis_cache import FastApiRedisCache
from dotenv import load_dotenv
import os

# Initialize environ
# Load virtual variables
load_dotenv()  # take environment variables from .env.

app = FastAPI()

# Add routes
app.include_router(users.router)
app.include_router(security.router)
app.include_router(films.router)
app.include_router(persons.router)
app.include_router(rents.router)

session = get_db_session()

# Creating databases
SQLModel.metadata.create_all(engine)


# Handling Errors--------------------------------------------------------------
@app.exception_handler(IntegrityError)
async def integrityError_exception_handler(request: Request,
                                           exc: IntegrityError):
    Logger.error(f"Integrity Error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": f"Integrity Error: {exc.orig}"},
    )


@app.exception_handler(AttributeError)
async def attributeError_exception_handler(request: Request,
                                           exc: AttributeError):
    Logger.error(f"AttributeError: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": f"Attribute Error {exc.name}"},
    )


@app.exception_handler(TypeError)
async def NoneType_exception_handler(request: Request,
                                     exc: TypeError):
    Logger.error(f"AttributeError: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "TypeError"},
    )


# Redis event------------------------------------------------------------------
@app.on_event("startup")
def startup():
    redis_cache = FastApiRedisCache()
    redis_cache.init(
        host_url=os.environ.get("REDIS_URL", os.getenv('REDIS_URL')),
        prefix="api-cache",
        response_header="X-API-Cache",
        ignore_arg_types=[Request, Response, session]
    )
