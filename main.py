from fastapi import FastAPI, Request
from sqlalchemy.exc import IntegrityError
from sqlmodel import SQLModel
from starlette.responses import JSONResponse

from database.db import engine, get_db_session

from utilities.logger import Logger

# Import routes
from routers import users, security, films, persons, rents


app = FastAPI()

app.include_router(users.router)
app.include_router(security.router)
app.include_router(films.router)
app.include_router(persons.router)
app.include_router(rents.router)

session = get_db_session()

# Creating database
SQLModel.metadata.create_all(engine)


# Handling Errors--------------------------------------------------------------
@app.exception_handler(IntegrityError)
async def integrityError_exception_handler(request: Request,
                                           exc: IntegrityError):
    session.rollback()
    Logger.error(f"Integrity Error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": f"Integrity Error: {exc.orig}"},
    )


@app.exception_handler(AttributeError)
async def attributeError_exception_handler(request: Request,
                                           exc: AttributeError):
    session.rollback()
    Logger.error(f"AttributeError: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": f"Attribute Error {exc.name}"},
    )
