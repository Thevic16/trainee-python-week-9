from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi_redis_cache import cache_one_month
from sqlmodel import select
from starlette import status

from databases.db import get_db_session
from models.persons import PersonRead, Person, PersonCreate, RoleRead, Role, \
    RoleCreate, FilmPersonRoleRead, FilmPersonRole, FilmPersonRoleCreate, \
    ClientRead, Client, ClientCreate
from security.security import get_admin_user

router = APIRouter()

session = get_db_session()


# Person Related Routes
@router.get('/api/persons', response_model=List[PersonRead],
            status_code=status.HTTP_200_OK)
@cache_one_month()
async def get_all_persons():
    session.rollback()
    statement = select(Person)
    results = session.exec(statement).all()

    return results


@router.get('/api/persons/{person_id}', response_model=PersonRead)
@cache_one_month()
async def get_by_id_a_person(person_id: int):
    session.rollback()
    statement = select(Person).where(Person.id == person_id)
    result = session.exec(statement).first()

    return result


@router.post('/api/persons', response_model=PersonRead,
             status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(get_admin_user)])
async def create_a_person(person: PersonCreate):
    session.rollback()
    new_person = Person(name=person.name,
                        lastname=person.lastname,
                        gender=person.gender,
                        date_of_birth=person.date_of_birth,
                        person_type=person.person_type,
                        age=Person.get_age(person.date_of_birth))

    session.add(new_person)

    session.commit()

    return new_person


@router.put('/api/persons/{person_id}', response_model=PersonRead,
            dependencies=[Depends(get_admin_user)])
async def update_a_person(person_id: int, person: PersonCreate):
    session.rollback()
    statement = select(Person).where(Person.id == person_id)

    result = session.exec(statement).first()

    result.name = person.name
    result.lastname = person.lastname
    result.gender = person.gender
    result.date_of_birth = person.date_of_birth
    result.person_type = person.person_type
    if result:
        result.age = Person.get_age(result.date_of_birth)

    session.commit()

    return result


@router.delete('/api/persons/{person_id}',
               status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(get_admin_user)])
async def delete_a_person(person_id: int):
    session.rollback()
    statement = select(Person).where(Person.id == person_id)

    result = session.exec(statement).one_or_none()

    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Resource Not Found")

    session.delete(result)
    session.commit()

    return result


@router.get('/api/roles', response_model=List[RoleRead],
            status_code=status.HTTP_200_OK)
@cache_one_month()
async def get_all_roles():
    session.rollback()
    statement = select(Role)
    results = session.exec(statement).all()

    return results


@router.get('/api/roles/{role_id}', response_model=RoleRead)
@cache_one_month()
async def get_by_id_a_role(role_id: int):
    session.rollback()
    statement = select(Role).where(Role.id == role_id)
    result = session.exec(statement).first()

    return result


@router.post('/api/roles', response_model=RoleRead,
             status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(get_admin_user)])
async def create_a_role(role: RoleCreate):
    session.rollback()
    new_role = Role(name=role.name,
                    description=role.description)

    session.add(new_role)

    session.commit()

    return new_role


@router.put('/api/roles/{role_id}', response_model=RoleRead,
            dependencies=[Depends(get_admin_user)])
async def update_a_role(role_id: int, role: RoleCreate):
    session.rollback()
    statement = select(Role).where(Role.id == role_id)

    result = session.exec(statement).first()

    result.name = role.name
    result.description = role.description

    session.commit()

    return result


@router.delete('/api/roles/{role_id}',
               status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(get_admin_user)])
async def delete_a_role(role_id: int):
    session.rollback()
    statement = select(Role).where(Role.id == role_id)

    result = session.exec(statement).one_or_none()

    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Resource Not Found")

    session.delete(result)
    session.commit()

    return result


@router.get('/api/films-persons-roles',
            response_model=List[FilmPersonRoleRead],
            status_code=status.HTTP_200_OK)
@cache_one_month()
async def get_all_films_persons_roles():
    session.rollback()
    statement = select(FilmPersonRole)
    results = session.exec(statement).all()

    return results


@router.get('/api/films-persons-roles/{film_person_role_id}',
            response_model=FilmPersonRoleRead)
@cache_one_month()
async def get_by_id_a_film_person_role(film_person_role_id: int):
    session.rollback()
    statement = select(FilmPersonRole).where(
        FilmPersonRole.id == film_person_role_id)

    result = session.exec(statement).first()

    return result


@router.post('/api/films-persons-roles', response_model=FilmPersonRoleRead,
             status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(get_admin_user)])
async def create_a_film_person_role(role: FilmPersonRoleCreate):
    session.rollback()
    new_film_person_role = FilmPersonRole(film_id=role.film_id,
                                          person_id=role.person_id,
                                          role_id=role.role_id)

    session.add(new_film_person_role)

    session.commit()

    return new_film_person_role


@router.put('/api/films-persons-roles/{film_person_role_id}',
            response_model=FilmPersonRoleRead,
            dependencies=[Depends(get_admin_user)])
async def update_a_film_person_role(film_person_role_id: int,
                                    film_person_role: FilmPersonRoleCreate):
    session.rollback()
    statement = select(FilmPersonRole).where(
        FilmPersonRole.id == film_person_role_id)

    result = session.exec(statement).first()

    result.film_id = film_person_role.film_id
    result.person_id = film_person_role.person_id
    result.role_id = film_person_role.role_id

    session.commit()

    return result


@router.delete('/api/films-persons-roles/{film_person_role_id}',
               status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(get_admin_user)])
async def delete_a_film_person_role(film_person_role_id: int):
    session.rollback()
    statement = select(FilmPersonRole).where(
        FilmPersonRole.id == film_person_role_id)

    result = session.exec(statement).one_or_none()

    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Resource Not Found")

    session.delete(result)
    session.commit()

    return result


@router.get('/api/clients', response_model=List[ClientRead],
            status_code=status.HTTP_200_OK)
@cache_one_month()
async def get_all_clients():
    session.rollback()
    statement = select(Client)
    results = session.exec(statement).all()

    return results


@router.get('/api/clients/{client_id}', response_model=ClientRead)
@cache_one_month()
async def get_by_id_a_client(client_id: int):
    session.rollback()
    statement = select(Client).where(Client.id == client_id)
    result = session.exec(statement).first()

    return result


@router.post('/api/clients', response_model=ClientRead,
             status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(get_admin_user)])
async def create_a_client(client: ClientCreate):
    session.rollback()
    new_client = Client(person_id=client.person_id,
                        direction=client.direction,
                        phone=client.phone,
                        email=client.email)

    session.add(new_client)

    session.commit()

    return new_client


@router.put('/api/clients/{client_id}', response_model=ClientRead,
            dependencies=[Depends(get_admin_user)])
async def update_a_client(client_id: int, client: Client):
    session.rollback()
    statement = select(Client).where(Client.id == client_id)

    result = session.exec(statement).first()

    result.person_id = client.person_id
    result.direction = client.direction
    result.phone = client.phone
    result.email = client.email

    session.commit()

    return result


@router.delete('/api/clients/{client_id}',
               status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(get_admin_user)])
async def delete_a_client(client_id: int):
    session.rollback()
    statement = select(Client).where(Client.id == client_id)

    result = session.exec(statement).one_or_none()

    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Resource Not Found")

    session.delete(result)
    session.commit()

    return result
