from datetime import date

from pydantic import validator
from sqlmodel import SQLModel, Field, Relationship, select, Session
from typing import Optional

from app.db import engine
from validators import validators

session = Session(bind=engine)


# Account related models
class AccountBase(SQLModel):
    email: str
    password: str
    is_admin: bool
    is_employee: bool

    @validator('email')
    def validate_email(cls, v):
        return validators.validate_email(v)


class Account(AccountBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class AccountCreate(AccountBase):
    pass


class AccountRead(AccountBase):
    id: int


# Film related models
class CategoryBase(SQLModel):
    name: str
    description: str


class Category(CategoryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class CategoryCreate(CategoryBase):
    pass


class CategoryRead(CategoryBase):
    id: int


class FilmBase(SQLModel):
    title: str
    description: str
    release_date: date
    category_id: int = Field(foreign_key="category.id")
    price_by_day: float
    stock: int
    film_type: str
    film_prequel_id: Optional[int] = Field(default=None, nullable=True,
                                           foreign_key="film.id")

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


class Film(FilmBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class FilmCreate(FilmBase):
    pass


class FilmRead(FilmBase):
    id: int


class SeasonBase(SQLModel):
    film_id: int = Field(foreign_key="film.id")
    title: str
    season_prequel_id: Optional[int] = Field(default=None,
                                             foreign_key="season.id")


class Season(SeasonBase):
    id: Optional[int] = Field(default=None, primary_key=True)


class SeasonCreate(SeasonBase):
    pass


class SeasonRead(SeasonBase):
    id: int


class ChapterBase(SQLModel):
    season_id: int = Field(foreign_key="season.id")
    title: str
    chapter_prequel_id: Optional[int] = Field(default=None,
                                              foreign_key="chapter.id")


class Chapter(ChapterBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class ChapterCreate(ChapterBase):
    pass


class ChapterRead(ChapterBase):
    id: int


# Person related models
class PersonBase(SQLModel):
    name: str
    lastname: str
    gender: str
    date_of_birth: date
    person_type: str

    client: Optional["Client"] = Relationship(back_populates="person")

    @validator('gender')
    def validate_gender(cls, v):
        return validators.validate_gender(v)

    @validator('date_of_birth')
    def validate_date_of_birth(cls, v):
        return validators.validator_date_limit_today(v)

    @validator('person_type')
    def validate_person_type(cls, v):
        return validators.validate_person_type(v)


class Person(PersonBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class PersonCreate(PersonBase):
    pass


class PersonRead(PersonBase):
    id: int


class RoleBase(SQLModel):
    name: str
    description: str


class Role(RoleBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class RoleCreate(RoleBase):
    pass


class RoleRead(RoleBase):
    id: int


class FilmPersonRoleBase(SQLModel):
    film_id: int = Field(foreign_key="film.id")
    person_id: int = Field(foreign_key="person.id")
    role_id: int = Field(foreign_key="role.id")


class FilmPersonRole(FilmPersonRoleBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class FilmPersonRoleCreate(FilmPersonRoleBase):
    pass


class FilmPersonRoleRead(FilmPersonRoleBase):
    id: int


class ClientBase(SQLModel):
    person_id: int = Field(foreign_key="person.id")
    direction: str
    phone: str
    email: str

    person: Person = Relationship(back_populates="client")

    @validator('email')
    def validate_email(cls, v):
        return validators.validate_email(v)

    @validator('phone')
    def validate_phone(cls, v):
        return validators.validate_phone(v)

    @validator('person_id')
    def validate_person_id(cls, v):
        statement = select(Person).where(Person.id == v)
        person = session.exec(statement).first()
        validators.validate_person_type_client(person.person_type)
        return v


class Client(ClientBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class ClientCreate(ClientBase):
    pass


class ClientRead(ClientBase):
    id: int


# Rent related model
class RentBase(SQLModel):
    film_id: int = Field(foreign_key="film.id")
    client_id: int = Field(foreign_key="client.id")
    amount: int
    start_date: date
    return_date: date
    actual_return_date: Optional[date]
    state: str

    @validator('amount')
    def validate_amount(cls, v):
        return validators.validator_no_negative(v)

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


class Rent(RentBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class RentCreate(RentBase):
    pass


class RentRead(RentBase):
    id: int
