from fastapi import FastAPI, status
from fastapi.exceptions import HTTPException
from sqlmodel import Session, select, SQLModel

from app.db import engine
from app.models import Category
from typing import List

app = FastAPI()

# Creating database
SQLModel.metadata.create_all(engine)

session = Session(bind=engine)


@app.get("/ping")
async def pong():
    return {"ping": "pong!"}


@app.get('/api/categories', response_model=List[Category],
         status_code=status.HTTP_200_OK)
async def get_all_categories():
    statement = select(Category)
    results = session.exec(statement).all()

    return results


@app.post('/api/categories', response_model=Category,
          status_code=status.HTTP_201_CREATED)
async def create_a_category(category: Category):
    new_category = Category(name=category.name,
                            description=category.description)

    session.add(new_category)

    session.commit()

    return new_category


@app.put('/api/categories/{category_id}', response_model=Category)
async def update_a_category(category_id: int, category: Category):
    statement = select(Category).where(Category.id == category_id)

    result = session.exec(statement).first()

    result.name = category.name
    result.description = category.description

    session.commit()

    return result


@app.delete('/api/categories/{category_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_a_book(category_id: int):
    statement = select(Category).where(Category.id == category_id)

    result = session.exec(statement).one_or_none()

    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Resource Not Found")

    session.delete(result)

    return result
