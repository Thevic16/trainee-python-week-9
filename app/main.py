from fastapi import FastAPI, status, Request, Depends
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import ExpiredSignatureError, InvalidSignatureError
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select, SQLModel
from starlette.responses import JSONResponse

from app.db import engine
from app.models import (Category, User, Film, Season, Chapter, Person, Role,
                        FilmPersonRole, Rent, Client, UserRead,
                        UserCreate, CategoryRead, CategoryCreate, FilmRead,
                        FilmCreate, SeasonRead, SeasonCreate, ChapterRead,
                        ChapterCreate, PersonCreate, PersonRead, RoleCreate,
                        RoleRead, FilmPersonRoleCreate, FilmPersonRoleRead,
                        ClientRead, ClientCreate, RentCreate, RentRead,
                        TokenData, Token)
from typing import List

from utilities.logger import Logger

# JWT imports
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt

app = FastAPI()

session = Session(bind=engine)

# Creating database
SQLModel.metadata.create_all(engine)

# JWT -------------------------------------------------------------------------
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str):
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except ExpiredSignatureError:
        raise credentials_exception
    except InvalidSignatureError:
        raise credentials_exception
    statement = select(User).where(User.username == token_data.username)
    user = session.exec(statement).first()
    if user is None:
        raise credentials_exception
    return user


@app.post("/token", response_model=Token)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# JWT permissions
async def get_admin_user(
        admin_user: User = Depends(get_current_user)):
    if not admin_user.is_admin:
        raise HTTPException(status_code=400, detail="Not admin user")
    return admin_user


async def get_admin_or_employee_user(
        user: User = Depends(get_current_user)):
    if not user.is_admin and not user.is_employee:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


# Handling Errors--------------------------------------------------------------
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


# User Related Routes
@app.get('/api/users', response_model=List[UserRead],
         status_code=status.HTTP_200_OK,
         dependencies=[Depends(get_admin_user)])
async def get_all_users():
    statement = select(User)
    results = session.exec(statement).all()

    return results


@app.get('/api/users/{user_id}', response_model=UserRead,
         dependencies=[Depends(get_admin_user)])
async def get_by_id_a_user(user_id: int):
    statement = select(User).where(User.id == user_id)
    result = session.exec(statement).first()

    return result


@app.post('/api/users', response_model=UserRead,
          status_code=status.HTTP_201_CREATED)
async def create_a_user(user: UserCreate):
    new_user = User(username=user.username,
                    password=get_password_hash(user.password),
                    is_admin=user.is_admin,
                    is_employee=user.is_employee)

    session.add(new_user)

    session.commit()

    return new_user


@app.put('/api/users/{user_id}', response_model=UserRead,
         dependencies=[Depends(get_admin_user)])
async def update_a_user(user_id: int, user: UserCreate):
    statement = select(User).where(User.id == user_id)

    result = session.exec(statement).first()

    result.username = user.username
    result.password = get_password_hash(user.password)
    result.is_admin = user.is_admin
    result.is_employee = user.is_employee

    session.commit()

    return result


@app.delete('/api/users/{user_id}',
            status_code=status.HTTP_204_NO_CONTENT,
            dependencies=[Depends(get_admin_user)])
async def delete_a_user(user_id: int):
    statement = select(User).where(User.id == user_id)
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
          status_code=status.HTTP_201_CREATED,
          dependencies=[Depends(get_admin_user)])
async def create_a_category(category: CategoryCreate):
    new_category = Category(name=category.name,
                            description=category.description)

    session.add(new_category)

    session.commit()

    return new_category


@app.put('/api/categories/{category_id}', response_model=CategoryRead,
         dependencies=[Depends(get_admin_user)])
async def update_a_category(category_id: int, category: CategoryCreate):
    statement = select(Category).where(Category.id == category_id)

    result = session.exec(statement).first()

    result.name = category.name
    result.description = category.description

    session.commit()

    return result


@app.delete('/api/categories/{category_id}',
            status_code=status.HTTP_204_NO_CONTENT,
            dependencies=[Depends(get_admin_user)])
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
            session.commit()

    return results


@app.get('/api/films/{film_id}', response_model=FilmRead)
async def get_by_id_a_film(film_id: int):
    statement = select(Film).where(Film.id == film_id)
    result = session.exec(statement).first()

    if result:
        result.availability = Film.get_availability(film_id)
        session.commit()

    return result


@app.post('/api/films', response_model=FilmRead,
          status_code=status.HTTP_201_CREATED,
          dependencies=[Depends(get_admin_user)])
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


@app.put('/api/films/{film_id}', response_model=FilmRead,
         dependencies=[Depends(get_admin_user)])
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
            status_code=status.HTTP_204_NO_CONTENT,
            dependencies=[Depends(get_admin_user)])
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
          status_code=status.HTTP_201_CREATED,
          dependencies=[Depends(get_admin_user)])
async def create_a_season(season: SeasonCreate):
    new_season = Season(film_id=season.film_id,
                        title=season.title,
                        season_prequel_id=season.season_prequel_id)

    session.add(new_season)
    session.commit()

    return new_season


@app.put('/api/seasons/{season_id}', response_model=SeasonRead,
         dependencies=[Depends(get_admin_user)])
async def update_a_season(season_id: int, season: SeasonCreate):
    statement = select(Season).where(Season.id == season_id)

    result = session.exec(statement).first()

    result.film_id = season.film_id
    result.title = season.title
    result.season_prequel_id = season.season_prequel_id

    session.commit()

    return result


@app.delete('/api/seasons/{season_id}',
            status_code=status.HTTP_204_NO_CONTENT,
            dependencies=[Depends(get_admin_user)])
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
          status_code=status.HTTP_201_CREATED,
          dependencies=[Depends(get_admin_user)])
async def create_a_chapter(chapter: ChapterCreate):
    new_chapter = Chapter(season_id=chapter.season_id,
                          title=chapter.title,
                          chapter_prequel_id=chapter.chapter_prequel_id)

    session.add(new_chapter)

    session.commit()

    return new_chapter


@app.put('/api/chapters/{chapter_id}', response_model=ChapterRead,
         dependencies=[Depends(get_admin_user)])
async def update_a_chapter(chapter_id: int, chapter: ChapterCreate):
    statement = select(Chapter).where(Chapter.id == chapter_id)

    result = session.exec(statement).first()

    result.season_id = chapter.season_id
    result.title = chapter.title
    result.chapter_prequel_id = chapter.chapter_prequel_id

    session.commit()

    return result


@app.delete('/api/chapters/{chapter_id}',
            status_code=status.HTTP_204_NO_CONTENT,
            dependencies=[Depends(get_admin_user)])
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
          status_code=status.HTTP_201_CREATED,
          dependencies=[Depends(get_admin_user)])
async def create_a_person(person: PersonCreate):
    new_person = Person(name=person.name,
                        lastname=person.lastname,
                        gender=person.gender,
                        date_of_birth=person.date_of_birth,
                        person_type=person.person_type,
                        age=Person.get_age(person.date_of_birth))

    session.add(new_person)

    session.commit()

    return new_person


@app.put('/api/persons/{person_id}', response_model=PersonRead,
         dependencies=[Depends(get_admin_user)])
async def update_a_person(person_id: int, person: PersonCreate):
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


@app.delete('/api/persons/{person_id}',
            status_code=status.HTTP_204_NO_CONTENT,
            dependencies=[Depends(get_admin_user)])
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
          status_code=status.HTTP_201_CREATED,
          dependencies=[Depends(get_admin_user)])
async def create_a_role(role: RoleCreate):
    new_role = Role(name=role.name,
                    description=role.description)

    session.add(new_role)

    session.commit()

    return new_role


@app.put('/api/roles/{role_id}', response_model=RoleRead,
         dependencies=[Depends(get_admin_user)])
async def update_a_role(role_id: int, role: RoleCreate):
    statement = select(Role).where(Role.id == role_id)

    result = session.exec(statement).first()

    result.name = role.name
    result.description = role.description

    session.commit()

    return result


@app.delete('/api/roles/{role_id}',
            status_code=status.HTTP_204_NO_CONTENT,
            dependencies=[Depends(get_admin_user)])
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
          status_code=status.HTTP_201_CREATED,
          dependencies=[Depends(get_admin_user)])
async def create_a_film_person_role(role: FilmPersonRoleCreate):
    new_role = FilmPersonRole(film_id=role.film_id,
                              person_id=role.person_id,
                              role_id=role.role_id)

    session.add(new_role)

    session.commit()

    return new_role


@app.put('/api/films-persons-roles/{film_person_role_id}',
         response_model=FilmPersonRoleRead,
         dependencies=[Depends(get_admin_user)])
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
            status_code=status.HTTP_204_NO_CONTENT,
            dependencies=[Depends(get_admin_user)])
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
          status_code=status.HTTP_201_CREATED,
          dependencies=[Depends(get_admin_user)])
async def create_a_client(client: ClientCreate):
    new_client = Client(person_id=client.person_id,
                        direction=client.direction,
                        phone=client.phone,
                        email=client.email)

    session.add(new_client)

    session.commit()

    return new_client


@app.put('/api/clients/{client_id}', response_model=ClientRead,
         dependencies=[Depends(get_admin_user)])
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
            status_code=status.HTTP_204_NO_CONTENT,
            dependencies=[Depends(get_admin_user)])
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
          status_code=status.HTTP_201_CREATED,
          dependencies=[Depends(get_admin_or_employee_user)])
async def create_a_rent(rent: RentCreate):
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


@app.put('/api/rents/{rent_id}', response_model=RentRead,
         dependencies=[Depends(get_admin_or_employee_user)])
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
    if result:
        result.cost = Rent.get_cost(rent)

    session.commit()

    return result


@app.delete('/api/rents/{rent_id}',
            status_code=status.HTTP_204_NO_CONTENT,
            dependencies=[Depends(get_admin_or_employee_user)])
async def delete_a_rent(rent_id: int):
    statement = select(Rent).where(Rent.id == rent_id)

    result = session.exec(statement).one_or_none()

    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Resource Not Found")

    session.delete(result)

    return result
