# Person related models
from datetime import date
from typing import Optional

from sqlalchemy import Column, Integer
from sqlmodel import SQLModel, Field, Relationship, select

from business_logic.business_logic import PersonBusinessLogic
from databases.db import get_db_session
from pydantic import validator
from validators import validators

session = get_db_session()


class PersonBase(SQLModel):
    name: str
    lastname: str
    gender: str
    date_of_birth: date
    person_type: str

    client: Optional["Client"] = Relationship(back_populates="person")


class Person(PersonBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    age: Optional[int]

    @staticmethod
    def get_age(date_of_birth):
        return PersonBusinessLogic.get_age_by_birthday(date_of_birth)


class PersonCreate(PersonBase):
    @validator('gender')
    def validate_gender(cls, v):
        return validators.validate_gender(v)

    @validator('date_of_birth')
    def validate_date_of_birth(cls, v):
        return validators.validator_date_limit_today(v)

    @validator('person_type')
    def validate_person_type(cls, v):
        return validators.validate_person_type(v)


class PersonRead(PersonBase):
    id: int
    age: Optional[int]


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
    person_id: int = Field(foreign_key="person.id",
                           sa_column=Column("person_id", Integer, unique=True))
    direction: str
    phone: str
    email: str

    person: Person = Relationship(back_populates="client")


class Client(ClientBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class ClientCreate(ClientBase):
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


class ClientRead(ClientBase):
    id: int
