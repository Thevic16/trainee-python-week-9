# User related models
from typing import Optional
from sqlmodel import SQLModel, Field

from pydantic import validator

from validators import validators


class UserBase(SQLModel):
    username: str
    password: str
    is_admin: bool
    is_employee: bool

    @validator('username')
    def validate_email(cls, v):
        return validators.validate_email(v)


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    id: int
