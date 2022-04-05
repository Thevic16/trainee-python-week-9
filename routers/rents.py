from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi_redis_cache import cache_one_month
from sqlmodel import select
from starlette import status

from databases.db import get_db_session
from models.films_and_rents import RentRead, Rent, RentCreate
from security.security import get_admin_or_employee_user

router = APIRouter()

session = get_db_session()


# Rent Related Routes
@router.get('/api/rents', response_model=List[RentRead],
            status_code=status.HTTP_200_OK)
@cache_one_month()
async def get_all_rents():
    session.rollback()
    statement = select(Rent)
    results = session.exec(statement).all()

    return results


@router.get('/api/rents/{rent_id}', response_model=RentRead)
@cache_one_month()
async def get_by_id_a_rent(rent_id: int):
    session.rollback()
    statement = select(Rent).where(Rent.id == rent_id)
    result = session.exec(statement).first()

    return result


@router.post('/api/rents', response_model=RentRead,
             status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(get_admin_or_employee_user)])
async def create_a_rent(rent: RentCreate):
    session.rollback()
    new_rent = Rent(film_id=rent.film_id,
                    client_id=rent.client_id,
                    amount=rent.amount,
                    start_date=rent.start_date,
                    return_date=rent.return_date,
                    actual_return_date=rent.actual_return_date,
                    state=rent.state,
                    cost=Rent.get_cost(rent))

    session.add(new_rent)

    session.commit()

    return new_rent


@router.put('/api/rents/{rent_id}', response_model=RentRead,
            dependencies=[Depends(get_admin_or_employee_user)])
async def update_a_rent(rent_id: int, rent: RentCreate):
    session.rollback()
    statement = select(Rent).where(Rent.id == rent_id)

    result = session.exec(statement).first()

    result.film_id = rent.film_id
    result.client_id = rent.client_id
    result.amount = rent.amount
    result.start_date = rent.start_date
    result.return_date = rent.return_date
    result.actual_return_date = rent.actual_return_date
    result.state = rent.state
    if result:
        result.cost = Rent.get_cost(rent)

    session.commit()

    return result


@router.delete('/api/rents/{rent_id}',
               status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(get_admin_or_employee_user)])
async def delete_a_rent(rent_id: int):
    session.rollback()
    statement = select(Rent).where(Rent.id == rent_id)

    result = session.exec(statement).one_or_none()

    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Resource Not Found")

    session.delete(result)
    session.commit()

    return result
