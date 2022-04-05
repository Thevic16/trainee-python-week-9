from datetime import date
from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship, select

from business_logic.business_logic import RentBusinessLogic
from databases.db import get_db_session
from pydantic import validator
from validators import validators
from sqlalchemy import Column, String, Integer

session = get_db_session()


# Film related models
class CategoryBase(SQLModel):
    name: str = Field(sa_column=Column("name", String, unique=True))
    description: str


class Category(CategoryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class CategoryCreate(CategoryBase):
    pass


class CategoryRead(CategoryBase):
    id: int


class FilmBase(SQLModel):
    title: str = Field(sa_column=Column("title", String, unique=True))
    description: str
    release_date: date
    category_id: int = Field(foreign_key="category.id")
    price_by_day: float
    stock: int
    film_type: str
    film_prequel_id: Optional[int] = Field(default=None, nullable=True,
                                           foreign_key="film.id",
                                           sa_column=Column("film_prequel_id",
                                                            Integer,
                                                            unique=True))


class Film(FilmBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    availability: Optional[int]

    rent: "Rent" = Relationship(back_populates="film")

    @staticmethod
    def get_availability(film_id):
        statement = select(Film).where(Film.id == film_id)
        film = session.exec(statement).first()
        return film.stock - Rent.get_total_amount_by_film_id(film.id)


class FilmCreate(FilmBase):
    @validator('release_date')
    def validate_release_date(cls, v):
        return validators.validator_date_limit_today(v)

    @validator('price_by_day')
    def validate_price_by_day(cls, v):
        return validators.validator_no_negative(v)

    @validator('stock')
    def validate_stock(cls, v):
        return validators.validator_no_negative(v)

    @validator('film_type')
    def validate_film_type(cls, v):
        return validators.validate_film_type(v)


class FilmRead(FilmBase):
    id: int
    availability: Optional[int]


class PosterBase(SQLModel):
    film_id: int = Field(foreign_key="film.id")


class Poster(PosterBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    link: str


class PosterCreate(PosterBase):
    pass


class PosterRead(PosterBase):
    id: int
    link: str


class SeasonBase(SQLModel):
    film_id: int = Field(foreign_key="film.id")
    title: str = Field(sa_column=Column("title", String, unique=True))
    season_prequel_id: Optional[int] = Field(
        default=None,
        foreign_key="season.id",
        sa_column=Column("season_prequel_id", Integer, unique=True))


class Season(SeasonBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class SeasonCreate(SeasonBase):
    pass


class SeasonRead(SeasonBase):
    id: int


class ChapterBase(SQLModel):
    season_id: int = Field(foreign_key="season.id")
    title: str = Field(sa_column=Column("title", String, unique=True))
    chapter_prequel_id: Optional[int] = Field(
        default=None,
        foreign_key="chapter.id",
        sa_column=Column("chapter_prequel_id", Integer, unique=True))


class Chapter(ChapterBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class ChapterCreate(ChapterBase):
    pass


class ChapterRead(ChapterBase):
    id: int


class RentBase(SQLModel):
    film_id: int = Field(foreign_key="film.id")
    client_id: int = Field(foreign_key="client.id")
    amount: int
    start_date: date
    return_date: date
    actual_return_date: Optional[date]
    state: str


# Rent related model
class Rent(RentBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    cost: Optional[float]

    film: "Film" = Relationship(back_populates="rent")

    @classmethod
    def find_all_rents_by_film_id(cls, film_id: int) -> List["Rent"]:
        statement = select(Rent).where(Rent.film_id == film_id,
                                       Rent.state == 'open')
        return session.exec(statement)

    @classmethod
    def get_total_amount_by_film_id(cls, film_id: id) -> int:
        total = 0
        for rent in cls.find_all_rents_by_film_id(film_id):
            total += rent.amount
        return total

    @staticmethod
    def get_cost(rent: "Rent") -> float:
        statement = select(Film).where(Film.id == rent.film_id)
        film = session.exec(statement).first()

        return RentBusinessLogic.get_rent_cost(rent.amount, rent.start_date,
                                               rent.return_date,
                                               rent.actual_return_date,
                                               film.price_by_day)


class RentCreate(RentBase):
    @validator('amount')
    def validate_amount(cls, v, values, **kwargs):
        validators.validator_no_negative(v)
        validators.validate_amount(v, values['film_id'])
        return v

    @validator('return_date')
    def validate_return_date(cls, v, values, **kwargs):
        validators.RentValidation.validate_date_gt_max_limit(
            v, values['start_date'], 'return_date')

        validators.RentValidation.validate_date1_eq_or_low_date2(
            v, values['start_date'], 'return_date')
        return v

    @validator('actual_return_date')
    def validate_actual_return_date(cls, v, values, **kwargs):
        validators.RentValidation.validate_date1_gr_or_eq_date2(
            v, values['start_date'], 'actual_return_date')
        return v

    @validator('state')
    def validate_state(cls, v):
        return validators.validate_rent_state(v)


class RentRead(RentBase):
    id: int
    cost: Optional[float]
