from datetime import date

from sqlmodel import SQLModel, Field
from typing import Optional


# Account related models
class Account(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str
    password: str
    is_admin: bool
    is_employee: bool


# Film related models
class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str


class Film(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str
    release_date: date
    category_id: int = Field(default=None, foreign_key="category.id")
    price_by_day: float
    stock: int
    film_type: str
    film_prequel_id: Optional[int] = Field(default=None, nullable=True,
                                           foreign_key="film.id")


class Season(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    film_id: int = Field(default=None, foreign_key="film.id")
    title: str
    season_prequel_id: Optional[int] = Field(default=None,
                                             foreign_key="season.id")


class Chapter(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    season_id: int = Field(default=None, foreign_key="season.id")
    title: str
    chapter_prequel_id: Optional[int] = Field(default=None,
                                              foreign_key="chapter.id")


# Person related models
class Person(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    lastname: str
    gender: str
    date_of_birth: date
    person_type: str


class Role(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str


class FilmPersonRole(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    film_id: int = Field(default=None, foreign_key="film.id")
    person_id: int = Field(default=None, foreign_key="person.id")
    role_id: int = Field(default=None, foreign_key="role.id")


class Client(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    person_id: int = Field(default=None, foreign_key="person.id")
    direction: str
    phone: str
    email: str


# Rent related model
class Rent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    film_id: int = Field(default=None, foreign_key="film.id")
    client_id: int = Field(default=None, foreign_key="client.id")
    amount: int
    start_date: date
    return_date: date
    actual_return_date: Optional[date]
    state: str
