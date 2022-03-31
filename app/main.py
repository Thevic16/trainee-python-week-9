from fastapi import FastAPI, status, Request
from fastapi.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select, SQLModel
from starlette.responses import JSONResponse

from app.db import engine
from app.models import (Category, Account, Film, Season, Chapter, Person, Role,
                        FilmPersonRole, Rent, Client)
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
@app.get('/api/accounts', response_model=List[Account],
         status_code=status.HTTP_200_OK)
async def get_all_accounts():
    statement = select(Account)
    results = session.exec(statement).all()

    return results


@app.get('/api/accounts/{account_id}', response_model=Account)
async def get_by_id_a_account(account_id: int):
    statement = select(Account).where(Account.id == account_id)
    result = session.exec(statement).first()

    return result


@app.post('/api/accounts', response_model=Account,
          status_code=status.HTTP_201_CREATED)
async def create_a_account(account: Account):
    new_account = Account(email=account.email,
                          password=account.password,
                          is_admin=account.is_admin,
                          is_employee=account.is_employee)

    session.add(new_account)

    session.commit()

    return new_account


@app.put('/api/accounts/{account_id}', response_model=Account)
async def update_a_account(account_id: int, account: Account):
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
@app.get('/api/categories', response_model=List[Category],
         status_code=status.HTTP_200_OK)
async def get_all_categories():
    statement = select(Category)
    results = session.exec(statement).all()

    return results


@app.get('/api/categories/{category_id}', response_model=Category)
async def get_by_id_a_category(category_id: int):
    statement = select(Category).where(Category.id == category_id)
    result = session.exec(statement).first()

    return result


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


@app.get('/api/films', response_model=List[Film],
         status_code=status.HTTP_200_OK)
async def get_all_films():
    statement = select(Film)
    results = session.exec(statement).all()

    return results


@app.get('/api/films/{film_id}', response_model=Film)
async def get_by_id_a_film(film_id: int):
    statement = select(Film).where(Film.id == film_id)
    result = session.exec(statement).first()

    return result


@app.post('/api/films', response_model=Film,
          status_code=status.HTTP_201_CREATED)
async def create_a_film(film: Film):
    new_film = Film(title=film.title,
                    description=film.description,
                    release_date=film.release_date,
                    category_id=film.category_id,
                    price_by_day=film.price_by_day,
                    stock=film.stock,
                    film_type=film.film_type,
                    film_prequel_id=film.film_prequel_id)

    session.add(new_film)

    session.commit()

    return new_film


@app.put('/api/films/{film_id}', response_model=Film)
async def update_a_film(film_id: int, film: Film):
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


@app.get('/api/seasons', response_model=List[Season],
         status_code=status.HTTP_200_OK)
async def get_all_seasons():
    statement = select(Season)
    results = session.exec(statement).all()

    return results


@app.get('/api/seasons/{season_id}', response_model=Season)
async def get_by_a_season(season_id: int):
    statement = select(Season).where(Season.id == season_id)
    result = session.exec(statement).first()

    return result


@app.post('/api/seasons', response_model=Season,
          status_code=status.HTTP_201_CREATED)
async def create_a_season(season: Season):
    new_season = Season(film_id=season.film_id,
                        title=season.title,
                        season_prequel_id=season.season_prequel_id)

    session.add(new_season)

    session.commit()

    return new_season


@app.put('/api/seasons/{season_id}', response_model=Season)
async def update_a_season(season_id: int, season: Season):
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


@app.get('/api/chapters', response_model=List[Chapter],
         status_code=status.HTTP_200_OK)
async def get_all_chapters():
    statement = select(Chapter)
    results = session.exec(statement).all()

    return results


@app.get('/api/chapters/{chapter_id}', response_model=Chapter)
async def get_by_id_a_chapter(chapter_id: int):
    statement = select(Chapter).where(Chapter.id == chapter_id)
    result = session.exec(statement).first()

    return result


@app.post('/api/chapters', response_model=Chapter,
          status_code=status.HTTP_201_CREATED)
async def create_a_chapter(chapter: Chapter):
    new_chapter = Chapter(season_id=chapter.season_id,
                          title=chapter.title,
                          chapter_prequel_id=chapter.chapter_prequel_id)

    session.add(new_chapter)

    session.commit()

    return new_chapter


@app.put('/api/chapters/{chapter_id}', response_model=Chapter)
async def update_a_chapter(chapter_id: int, chapter: Chapter):
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
@app.get('/api/persons', response_model=List[Person],
         status_code=status.HTTP_200_OK)
async def get_all_persons():
    statement = select(Person)
    results = session.exec(statement).all()

    return results


@app.get('/api/persons/{person_id}', response_model=Person)
async def get_by_id_a_person(person_id: int):
    statement = select(Person).where(Person.id == person_id)
    result = session.exec(statement).first()

    return result


@app.post('/api/persons', response_model=Person,
          status_code=status.HTTP_201_CREATED)
async def create_a_person(person: Person):
    new_person = Person(name=person.name,
                        lastname=person.lastname,
                        gender=person.gender,
                        date_of_birth=person.date_of_birth,
                        person_type=person.person_type)

    session.add(new_person)

    session.commit()

    return new_person


@app.put('/api/persons/{person_id}', response_model=Person)
async def update_a_person(person_id: int, person: Person):
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


@app.get('/api/roles', response_model=List[Role],
         status_code=status.HTTP_200_OK)
async def get_all_roles():
    statement = select(Role)
    results = session.exec(statement).all()

    return results


@app.get('/api/roles/{role_id}', response_model=Role)
async def get_by_id_a_role(role_id: int):
    statement = select(Role).where(Role.id == role_id)
    result = session.exec(statement).first()

    return result


@app.post('/api/roles', response_model=Role,
          status_code=status.HTTP_201_CREATED)
async def create_a_role(role: Role):
    new_role = Role(name=role.name,
                    description=role.description)

    session.add(new_role)

    session.commit()

    return new_role


@app.put('/api/roles/{role_id}', response_model=Role)
async def update_a_role(role_id: int, role: Role):
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


@app.get('/api/films-persons-roles', response_model=List[FilmPersonRole],
         status_code=status.HTTP_200_OK)
async def get_all_films_persons_roles():
    statement = select(FilmPersonRole)
    results = session.exec(statement).all()

    return results


@app.get('/api/films-persons-roles/{film_person_role_id}',
         response_model=FilmPersonRole)
async def get_by_id_a_film_person_role(film_person_role_id: int):
    statement = select(FilmPersonRole).where(
        FilmPersonRole.id == film_person_role_id)

    result = session.exec(statement).first()

    return result


@app.post('/api/films-persons-roles', response_model=FilmPersonRole,
          status_code=status.HTTP_201_CREATED)
async def create_a_film_person_role(role: FilmPersonRole):
    new_role = FilmPersonRole(film_id=role.film_id,
                              person_id=role.person_id,
                              role_id=role.role_id)

    session.add(new_role)

    session.commit()

    return new_role


@app.put('/api/films-persons-roles/{film_person_role_id}',
         response_model=FilmPersonRole)
async def update_a_film_person_role(film_person_role_id: int,
                                    film_person_role: FilmPersonRole):
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


@app.get('/api/clients', response_model=List[Client],
         status_code=status.HTTP_200_OK)
async def get_all_clients():
    statement = select(Client)
    results = session.exec(statement).all()

    return results


@app.get('/api/clients/{client_id}', response_model=Client)
async def get_by_id_a_client(client_id: int):
    statement = select(Client).where(Client.id == client_id)
    result = session.exec(statement).first()

    return result


@app.post('/api/clients', response_model=Client,
          status_code=status.HTTP_201_CREATED)
async def create_a_client(client: Client):
    new_client = Client(person_id=client.person_id,
                        direction=client.direction,
                        phone=client.phone,
                        email=client.email)

    session.add(new_client)

    session.commit()

    return new_client


@app.put('/api/clients/{client_id}', response_model=Client)
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
@app.get('/api/rents', response_model=List[Rent],
         status_code=status.HTTP_200_OK)
async def get_all_rents():
    statement = select(Rent)
    results = session.exec(statement).all()

    return results


@app.get('/api/rents/{rent_id}', response_model=Rent)
async def get_by_id_a_rent(rent_id: int):
    statement = select(Rent).where(Rent.id == rent_id)
    result = session.exec(statement).first()

    return result


@app.post('/api/rents', response_model=Rent,
          status_code=status.HTTP_201_CREATED)
async def create_a_rent(rent: Rent):
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


@app.put('/api/rents/{rent_id}', response_model=Rent)
async def update_a_rent(rent_id: int, rent: Rent):
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
