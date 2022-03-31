from fastapi import FastAPI, status, Request
from fastapi.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select, SQLModel
from starlette.responses import JSONResponse

from app.db import engine
from app.models import (Category, Account, Film, Season, Chapter, Person, Role,
                        FilmPersonRole, Rent, Client, AccountRead,
                        AccountCreate, CategoryRead, CategoryCreate, FilmRead,
                        FilmCreate, SeasonRead, SeasonCreate, ChapterRead,
                        ChapterCreate, PersonCreate, PersonRead, RoleCreate,
                        RoleRead, FilmPersonRoleCreate, FilmPersonRoleRead,
                        ClientRead, ClientCreate, RentCreate, RentRead)
from typing import List

from utilities.logger import Logger

app = FastAPI()

session = Session(bind=engine)

# Creating database
SQLModel.metadata.create_all(engine)


# Handling Errors
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


# Account Related Routes
@app.get('/api/accounts', response_model=List[AccountRead],
         status_code=status.HTTP_200_OK)
async def get_all_accounts():
    statement = select(Account)
    results = session.exec(statement).all()

    return results


@app.get('/api/accounts/{account_id}', response_model=AccountRead)
async def get_by_id_a_account(account_id: int):
    statement = select(Account).where(Account.id == account_id)
    result = session.exec(statement).first()

    return result


@app.post('/api/accounts', response_model=AccountRead,
          status_code=status.HTTP_201_CREATED)
async def create_a_account(account: AccountCreate):
    new_account = Account(email=account.email,
                          password=account.password,
                          is_admin=account.is_admin,
                          is_employee=account.is_employee)

    session.add(new_account)

    session.commit()

    return new_account


@app.put('/api/accounts/{account_id}', response_model=AccountRead)
async def update_a_account(account_id: int, account: AccountCreate):
    statement = select(Account).where(Account.id == account_id)

    result = session.exec(statement).first()

    result.email = account.email
    result.password = account.password
    result.is_admin = account.is_admin
    result.is_employee = account.is_employee

    session.commit()

    return result


@app.delete('/api/accounts/{account_id}',
            status_code=status.HTTP_204_NO_CONTENT)
async def delete_a_account(account_id: int):
    statement = select(Account).where(Account.id == account_id)

    result = session.exec(statement).one_or_none()

    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Resource Not Found")

    session.delete(result)

    return result


# Film Related Routes
@app.get('/api/categories', response_model=List[CategoryRead],
         status_code=status.HTTP_200_OK)
async def get_all_categories():
    statement = select(Category)
    results = session.exec(statement).all()

    return results


@app.get('/api/categories/{category_id}', response_model=CategoryRead)
async def get_by_id_a_category(category_id: int):
    statement = select(Category).where(Category.id == category_id)
    result = session.exec(statement).first()

    return result


@app.post('/api/categories', response_model=CategoryRead,
          status_code=status.HTTP_201_CREATED)
async def create_a_category(category: CategoryCreate):
    new_category = Category(name=category.name,
                            description=category.description)

    session.add(new_category)

    session.commit()

    return new_category


@app.put('/api/categories/{category_id}', response_model=CategoryRead)
async def update_a_category(category_id: int, category: CategoryCreate):
    statement = select(Category).where(Category.id == category_id)

    result = session.exec(statement).first()

    result.name = category.name
    result.description = category.description

    session.commit()

    return result


@app.delete('/api/categories/{category_id}',
            status_code=status.HTTP_204_NO_CONTENT)
async def delete_a_category(category_id: int):
    statement = select(Category).where(Category.id == category_id)

    result = session.exec(statement).one_or_none()

    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Resource Not Found")

    session.delete(result)

    return result


@app.get('/api/films', response_model=List[FilmRead],
         status_code=status.HTTP_200_OK)
async def get_all_films():
    statement = select(Film)
    results = session.exec(statement).all()

    for film in results:
        if film:
            film.availability = Film.get_availability(film.id)

    return results


@app.get('/api/films/{film_id}', response_model=FilmRead)
async def get_by_id_a_film(film_id: int):
    statement = select(Film).where(Film.id == film_id)
    result = session.exec(statement).first()

    if result:
        result.availability = Film.get_availability(film_id)

    return result


@app.post('/api/films', response_model=FilmRead,
          status_code=status.HTTP_201_CREATED)
async def create_a_film(film: FilmCreate):
    new_film = Film(title=film.title,
                    description=film.description,
                    release_date=film.release_date,
                    category_id=film.category_id,
                    price_by_day=film.price_by_day,
                    stock=film.stock,
                    film_type=film.film_type,
                    film_prequel_id=film.film_prequel_id,
                    availability=film.stock)

    session.add(new_film)

    session.commit()

    return new_film


@app.put('/api/films/{film_id}', response_model=FilmRead)
async def update_a_film(film_id: int, film: FilmCreate):
    statement = select(Film).where(Film.id == film_id)

    result = session.exec(statement).first()

    result.title = film.title
    result.description = film.description
    result.release_date = film.release_date
    result.category_id = film.category_id
    result.price_by_day = film.price_by_day
    result.stock = film.stock
    result.film_type = film.film_type
    result.film_prequel_id = film.film_prequel_id
    if result:
        result.availability = Film.get_availability(film_id)

    session.commit()

    return result


@app.delete('/api/films/{film_id}',
            status_code=status.HTTP_204_NO_CONTENT)
async def delete_a_film(film_id: int):
    statement = select(Film).where(Film.id == film_id)

    result = session.exec(statement).one_or_none()

    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Resource Not Found")

    session.delete(result)

    return result


@app.get('/api/seasons', response_model=List[SeasonRead],
         status_code=status.HTTP_200_OK)
async def get_all_seasons():
    statement = select(Season)
    results = session.exec(statement).all()

    return results


@app.get('/api/seasons/{season_id}', response_model=SeasonRead)
async def get_by_a_season(season_id: int):
    statement = select(Season).where(Season.id == season_id)
    result = session.exec(statement).first()

    return result


@app.post('/api/seasons', response_model=SeasonRead,
          status_code=status.HTTP_201_CREATED)
async def create_a_season(season: SeasonCreate):
    new_season = Season(film_id=season.film_id,
                        title=season.title,
                        season_prequel_id=season.season_prequel_id)

    session.add(new_season)
    session.commit()

    return new_season


@app.put('/api/seasons/{season_id}', response_model=SeasonRead)
async def update_a_season(season_id: int, season: SeasonCreate):
    statement = select(Season).where(Season.id == season_id)

    result = session.exec(statement).first()

    result.film_id = season.film_id
    result.title = season.title
    result.season_prequel_id = season.season_prequel_id

    session.commit()

    return result


@app.delete('/api/seasons/{season_id}',
            status_code=status.HTTP_204_NO_CONTENT)
async def delete_a_season(season_id: int):
    statement = select(Season).where(Season.id == season_id)

    result = session.exec(statement).one_or_none()

    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Resource Not Found")

    session.delete(result)

    return result


@app.get('/api/chapters', response_model=List[ChapterRead],
         status_code=status.HTTP_200_OK)
async def get_all_chapters():
    statement = select(Chapter)
    results = session.exec(statement).all()

    return results


@app.get('/api/chapters/{chapter_id}', response_model=ChapterRead)
async def get_by_id_a_chapter(chapter_id: int):
    statement = select(Chapter).where(Chapter.id == chapter_id)
    result = session.exec(statement).first()

    return result


@app.post('/api/chapters', response_model=ChapterRead,
          status_code=status.HTTP_201_CREATED)
async def create_a_chapter(chapter: ChapterCreate):
    new_chapter = Chapter(season_id=chapter.season_id,
                          title=chapter.title,
                          chapter_prequel_id=chapter.chapter_prequel_id)

    session.add(new_chapter)

    session.commit()

    return new_chapter


@app.put('/api/chapters/{chapter_id}', response_model=ChapterRead)
async def update_a_chapter(chapter_id: int, chapter: ChapterCreate):
    statement = select(Chapter).where(Chapter.id == chapter_id)

    result = session.exec(statement).first()

    result.season_id = chapter.season_id
    result.title = chapter.title
    result.chapter_prequel_id = chapter.chapter_prequel_id

    session.commit()

    return result


@app.delete('/api/chapters/{chapter_id}',
            status_code=status.HTTP_204_NO_CONTENT)
async def delete_a_chapter(chapter_id: int):
    statement = select(Chapter).where(Chapter.id == chapter_id)

    result = session.exec(statement).one_or_none()

    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Resource Not Found")

    session.delete(result)

    return result


# Person Related Routes
@app.get('/api/persons', response_model=List[PersonRead],
         status_code=status.HTTP_200_OK)
async def get_all_persons():
    statement = select(Person)
    results = session.exec(statement).all()

    return results


@app.get('/api/persons/{person_id}', response_model=PersonRead)
async def get_by_id_a_person(person_id: int):
    statement = select(Person).where(Person.id == person_id)
    result = session.exec(statement).first()

    return result


@app.post('/api/persons', response_model=PersonRead,
          status_code=status.HTTP_201_CREATED)
async def create_a_person(person: PersonCreate):
    new_person = Person(name=person.name,
                        lastname=person.lastname,
                        gender=person.gender,
                        date_of_birth=person.date_of_birth,
                        person_type=person.person_type)

    session.add(new_person)

    session.commit()

    return new_person


@app.put('/api/persons/{person_id}', response_model=PersonRead)
async def update_a_person(person_id: int, person: PersonCreate):
    statement = select(Person).where(Person.id == person_id)

    result = session.exec(statement).first()

    result.name = person.name
    result.lastname = person.lastname
    result.gender = person.gender
    result.date_of_birth = person.date_of_birth
    result.person_type = person.person_type

    session.commit()

    return result


@app.delete('/api/persons/{person_id}',
            status_code=status.HTTP_204_NO_CONTENT)
async def delete_a_person(person_id: int):
    statement = select(Person).where(Person.id == person_id)

    result = session.exec(statement).one_or_none()

    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Resource Not Found")

    session.delete(result)

    return result


@app.get('/api/roles', response_model=List[RoleRead],
         status_code=status.HTTP_200_OK)
async def get_all_roles():
    statement = select(Role)
    results = session.exec(statement).all()

    return results


@app.get('/api/roles/{role_id}', response_model=RoleRead)
async def get_by_id_a_role(role_id: int):
    statement = select(Role).where(Role.id == role_id)
    result = session.exec(statement).first()

    return result


@app.post('/api/roles', response_model=RoleRead,
          status_code=status.HTTP_201_CREATED)
async def create_a_role(role: RoleCreate):
    new_role = Role(name=role.name,
                    description=role.description)

    session.add(new_role)

    session.commit()

    return new_role


@app.put('/api/roles/{role_id}', response_model=RoleRead)
async def update_a_role(role_id: int, role: RoleCreate):
    statement = select(Role).where(Role.id == role_id)

    result = session.exec(statement).first()

    result.name = role.name
    result.description = role.description

    session.commit()

    return result


@app.delete('/api/roles/{role_id}',
            status_code=status.HTTP_204_NO_CONTENT)
async def delete_a_role(role_id: int):
    statement = select(Role).where(Role.id == role_id)

    result = session.exec(statement).one_or_none()

    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Resource Not Found")

    session.delete(result)

    return result


@app.get('/api/films-persons-roles', response_model=List[FilmPersonRoleRead],
         status_code=status.HTTP_200_OK)
async def get_all_films_persons_roles():
    statement = select(FilmPersonRole)
    results = session.exec(statement).all()

    return results


@app.get('/api/films-persons-roles/{film_person_role_id}',
         response_model=FilmPersonRoleRead)
async def get_by_id_a_film_person_role(film_person_role_id: int):
    statement = select(FilmPersonRole).where(
        FilmPersonRole.id == film_person_role_id)

    result = session.exec(statement).first()

    return result


@app.post('/api/films-persons-roles', response_model=FilmPersonRoleRead,
          status_code=status.HTTP_201_CREATED)
async def create_a_film_person_role(role: FilmPersonRoleCreate):
    new_role = FilmPersonRole(film_id=role.film_id,
                              person_id=role.person_id,
                              role_id=role.role_id)

    session.add(new_role)

    session.commit()

    return new_role


@app.put('/api/films-persons-roles/{film_person_role_id}',
         response_model=FilmPersonRoleRead)
async def update_a_film_person_role(film_person_role_id: int,
                                    film_person_role: FilmPersonRoleCreate):
    statement = select(FilmPersonRole).where(
        FilmPersonRole.id == film_person_role_id)

    result = session.exec(statement).first()

    result.film_id = film_person_role.film_id
    result.person_id = film_person_role.person_id
    result.role_id = film_person_role.role_id

    session.commit()

    return result


@app.delete('/api/films-persons-roles/{film_person_role_id}',
            status_code=status.HTTP_204_NO_CONTENT)
async def delete_a_film_person_role(film_person_role_id: int):
    statement = select(FilmPersonRole).where(
        FilmPersonRole.id == film_person_role_id)

    result = session.exec(statement).one_or_none()

    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Resource Not Found")

    session.delete(result)

    return result


@app.get('/api/clients', response_model=List[ClientRead],
         status_code=status.HTTP_200_OK)
async def get_all_clients():
    statement = select(Client)
    results = session.exec(statement).all()

    return results


@app.get('/api/clients/{client_id}', response_model=ClientRead)
async def get_by_id_a_client(client_id: int):
    statement = select(Client).where(Client.id == client_id)
    result = session.exec(statement).first()

    return result


@app.post('/api/clients', response_model=ClientRead,
          status_code=status.HTTP_201_CREATED)
async def create_a_client(client: ClientCreate):
    new_client = Client(person_id=client.person_id,
                        direction=client.direction,
                        phone=client.phone,
                        email=client.email)

    session.add(new_client)

    session.commit()

    return new_client


@app.put('/api/clients/{client_id}', response_model=ClientRead)
async def update_a_client(client_id: int, client: Client):
    statement = select(Client).where(Client.id == client_id)

    result = session.exec(statement).first()

    result.person_id = client.person_id
    result.direction = client.direction
    result.phone = client.phone
    result.email = client.email

    session.commit()

    return result


@app.delete('/api/clients/{client_id}',
            status_code=status.HTTP_204_NO_CONTENT)
async def delete_a_client(client_id: int):
    statement = select(Client).where(Client.id == client_id)

    result = session.exec(statement).one_or_none()

    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Resource Not Found")

    session.delete(result)

    return result


# Rent Related Routes
@app.get('/api/rents', response_model=List[RentRead],
         status_code=status.HTTP_200_OK)
async def get_all_rents():
    statement = select(Rent)
    results = session.exec(statement).all()

    return results


@app.get('/api/rents/{rent_id}', response_model=RentRead)
async def get_by_id_a_rent(rent_id: int):
    statement = select(Rent).where(Rent.id == rent_id)
    result = session.exec(statement).first()

    return result


@app.post('/api/rents', response_model=RentRead,
          status_code=status.HTTP_201_CREATED)
async def create_a_rent(rent: RentCreate):
    new_rent = Rent(film_id=rent.film_id,
                    client_id=rent.client_id,
                    amount=rent.amount,
                    start_date=rent.start_date,
                    return_date=rent.return_date,
                    actual_return_date=rent.actual_return_date,
                    state=rent.state)

    session.add(new_rent)

    session.commit()

    return new_rent


@app.put('/api/rents/{rent_id}', response_model=RentRead)
async def update_a_rent(rent_id: int, rent: RentCreate):
    statement = select(Rent).where(Rent.id == rent_id)

    result = session.exec(statement).first()

    result.film_id = rent.film_id
    result.client_id = rent.client_id
    result.amount = rent.amount
    result.start_date = rent.start_date
    result.return_date = rent.return_date
    result.actual_return_date = rent.actual_return_date
    result.state = rent.state

    session.commit()

    return result


@app.delete('/api/rents/{rent_id}',
            status_code=status.HTTP_204_NO_CONTENT)
async def delete_a_rent(rent_id: int):
    statement = select(Rent).where(Rent.id == rent_id)

    result = session.exec(statement).one_or_none()

    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Resource Not Found")

    session.delete(result)

    return result
