from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi_redis_cache import cache_one_month
from sqlmodel import select
from starlette import status

from databases.db import get_db_session
from models.users import UserRead, User, UserCreate
from security.security import get_admin_user, get_password_hash

router = APIRouter()

session = get_db_session()


# User Related Routes
@router.get('/api/users', response_model=List[UserRead],
            status_code=status.HTTP_200_OK,
            dependencies=[Depends(get_admin_user)])
@cache_one_month()
async def get_all_users():
    session.rollback()
    statement = select(User)
    results = session.exec(statement).all()

    return results


@router.get('/api/users/{user_id}', response_model=UserRead,
            dependencies=[Depends(get_admin_user)])
@cache_one_month()
async def get_by_id_a_user(user_id: int):
    session.rollback()
    statement = select(User).where(User.id == user_id)
    result = session.exec(statement).first()

    return result


@router.post('/api/users', response_model=UserRead,
             status_code=status.HTTP_201_CREATED)
async def create_a_user(user: UserCreate):
    session.rollback()
    new_user = User(username=user.username,
                    password=get_password_hash(user.password),
                    is_admin=user.is_admin,
                    is_employee=user.is_employee)

    session.add(new_user)

    session.commit()

    return new_user


@router.put('/api/users/{user_id}', response_model=UserRead,
            dependencies=[Depends(get_admin_user)])
async def update_a_user(user_id: int, user: UserCreate):
    session.rollback()
    statement = select(User).where(User.id == user_id)

    result = session.exec(statement).first()

    result.username = user.username
    result.password = get_password_hash(user.password)
    result.is_admin = user.is_admin
    result.is_employee = user.is_employee

    session.commit()

    return result


@router.delete('/api/users/{user_id}',
               status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(get_admin_user)])
async def delete_a_user(user_id: int):
    session.rollback()
    statement = select(User).where(User.id == user_id)
    result = session.exec(statement).one_or_none()

    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Resource Not Found")

    session.delete(result)
    session.commit()

    return result
