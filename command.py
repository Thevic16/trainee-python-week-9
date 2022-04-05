import random
from datetime import date

import typer
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from databases.db import get_db_session
from models.films_and_rents import Film, Category, Season, Chapter, Rent, \
    RentCreate
from models.persons import Role, Person, FilmPersonRole, Client
from models.users import User
from security.security import get_password_hash
from utilities.generators_functions import (get_random_string, gen_date,
                                            gen_random_float, gen_random_int,
                                            gen_random_film_type,
                                            gen_person_gender,
                                            gen_person_type, gen_phone,
                                            gen_number)

app = typer.Typer()
session = get_db_session()


@app.command()
def usersgen(user_type: str = typer.Option("-a",
                                           help='Define the'
                                                ' account type')):
    for i in range(10):
        email = get_random_string(15)
        password = get_random_string(15)

        try:
            if user_type == "-a":
                new_user = User(
                    username=f'{email}@filmrentalsystem.com',
                    password=password,
                    is_admin=True,
                    is_employee=False)

                session.add(new_user)
                session.commit()

            elif user_type == "-e":
                new_user = User(
                    username=f'{email}@filmrentalsystem.com',
                    password=get_password_hash(password),
                    is_admin=False,
                    is_employee=True)

                session.add(new_user)
                session.commit()
            else:
                new_user = User(
                    username=f'{email}@filmrentalsystem.com',
                    password=get_password_hash(password),
                    is_admin=False,
                    is_employee=False)

                session.add(new_user)
                session.commit()

            typer.echo(f'Email: {email}  password:({password}) '
                       f'user created!')
        except IntegrityError:
            session.rollback()
            typer.echo('An error has occurred during the creation '
                       'of the account')


@app.command()
def categoriesgen():
    for i in range(10):
        name = get_random_string(15)
        description = get_random_string(15)

        try:
            new_category = Category(
                name=name,
                description=description)

            session.add(new_category)
            session.commit()

            typer.echo(f'name: {name}  description:({description}) '
                       f'category created!')

        except IntegrityError:
            session.rollback()
            typer.echo('An error has occurred during the creation '
                       'of the category')


@app.command()
def filmsgen():
    for i in range(10):
        title = get_random_string(15)
        description = get_random_string(15)
        release_date = gen_date()

        statement = select(Category)
        items_category = list(session.exec(statement).all())
        category = random.choice(items_category)

        price_by_day = gen_random_float()
        stock = gen_random_int()
        film_type = gen_random_film_type()

        try:
            new_film = Film(title=title,
                            description=description,
                            release_date=release_date,
                            category_id=category.id,
                            price_by_day=price_by_day,
                            stock=stock,
                            film_type=film_type,
                            film_prequel_id=None,
                            availability=stock)

            session.add(new_film)
            session.commit()

            typer.echo(f'title: {title} , description:{description}'
                       f' release_date:{release_date},'
                       f'category:{category}, '
                       f'price_by_day:{price_by_day},'
                       f'stock:{stock},'
                       f'availability:{stock},'
                       f'film_type:{film_type},'
                       f' film created!')

        except IntegrityError:
            session.rollback()
            typer.echo('An error has occurred during the creation '
                       'of the film')


@app.command()
def seasonsgen():
    for i in range(10):
        title = get_random_string(15)

        statement = select(Film)
        items_film = list(session.exec(statement).all())
        film = random.choice(items_film)

        try:
            new_season = Season(title=title,
                                film_id=film.id,
                                season_prequel_id=None)

            session.add(new_season)
            session.commit()

            typer.echo(f'film: {film} , title:{title}'
                       f' season created!')

        except IntegrityError:
            session.rollback()
            typer.echo('An error has occurred during the creation '
                       'of the season')


@app.command()
def chaptersgen():
    for i in range(10):
        title = get_random_string(15)

        statement = select(Season)
        items_season = list(session.exec(statement).all())
        season = random.choice(items_season)

        try:
            new_chapter = Chapter(title=title,
                                  season_id=season.id,
                                  chapter_prequel_id=None)

            session.add(new_chapter)
            session.commit()

            typer.echo(f'season: {season} , title:{title}'
                       f' chapter created!')

        except IntegrityError:
            session.rollback()
            typer.echo('An error has occurred during the creation '
                       'of the chapter')


@app.command()
def persongen():
    for i in range(10):
        name = get_random_string(15)
        lastname = get_random_string(15)
        gender = gen_person_gender()
        date_of_birth = gen_date()
        person_type = gen_person_type()

        try:
            new_person = Person(name=name,
                                lastname=lastname,
                                gender=gender,
                                date_of_birth=date_of_birth,
                                person_type=person_type)

            session.add(new_person)
            session.commit()

            typer.echo(f'name: {name} , lastname:{lastname}'
                       f' gender:{gender},'
                       f'gender:{gender}, '
                       f'date_of_birth:{date_of_birth},'
                       f'person_type:{person_type},'
                       f' person created!')

        except IntegrityError:
            session.rollback()
            typer.echo('An error has occurred during the creation '
                       'of the person')


@app.command()
def rolesgen():
    for i in range(10):
        name = get_random_string(15)
        description = get_random_string(15)

        try:
            new_role = Role(name=name,
                            description=description)

            session.add(new_role)
            session.commit()

            typer.echo(f'name: {name} , description:{description}'
                       f' role created!')

        except IntegrityError:
            session.rollback()
            typer.echo('An error has occurred during the creation '
                       'of the roles')


@app.command()
def filmspersonsrolesgen():
    for i in range(10):
        statement = select(Film)
        items_film = list(session.exec(statement).all())
        film = random.choice(items_film)

        statement = select(Person)
        items_person = list(session.exec(statement).all())
        person = random.choice(items_person)

        statement = select(Role)
        items_role = list(session.exec(statement).all())
        role = random.choice(items_role)

        try:
            new_film_person_role = FilmPersonRole(film_id=film.id,
                                                  person_id=person.id,
                                                  role_id=role.id)

            session.add(new_film_person_role)
            session.commit()

            typer.echo(f'film: {film} , person:{person}'
                       f' role:{role},'
                       f' film-person-role created!')

        except IntegrityError:
            session.rollback()
            typer.echo('An error has occurred during the creation '
                       'of the films-persons-roles')


@app.command()
def clientsgen():
    for i in range(10):
        statement = select(Person)
        items_person = list(session.exec(statement).all())
        person = random.choice(items_person)

        direction = get_random_string(15)
        phone = gen_phone()
        email = get_random_string(15)

        try:
            new_client = Client(person_id=person.id,
                                direction=direction,
                                phone=phone,
                                email=f'{email}@filmrentalsystem.com')

            session.add(new_client)
            session.commit()

            typer.echo(f'person: {person} , direction:{direction}'
                       f' phone:{phone}, email:{email} '
                       f' client created!')

        except IntegrityError:
            session.rollback()
            typer.echo('An error has occurred during the creation '
                       'of the client')


@app.command()
def rentsgen():
    for i in range(10):
        statement = select(Film)
        items_film = list(session.exec(statement).all())
        film = random.choice(items_film)

        statement = select(Client)
        items_client = list(session.exec(statement).all())
        client = random.choice(items_client)

        amount = gen_number(1, 9)

        start_date = date(year=2020, month=1, day=1)
        return_date = date(year=2020, month=1, day=5)
        state = 'open'

        try:
            new_rent_create = RentCreate(film_id=film.id,
                                         client_id=client.id,
                                         amount=amount,
                                         start_date=start_date,
                                         return_date=return_date,
                                         actual_return_date=None,
                                         state=state)

            new_rent = Rent(film_id=film.id,
                            client_id=client.id,
                            amount=amount,
                            start_date=start_date,
                            return_date=return_date,
                            actual_return_date=None,
                            state=state,
                            cost=Rent.get_cost(new_rent_create))

            session.add(new_rent)
            session.commit()

            typer.echo(f'film: {film} , client:{client}'
                       f' amount:{amount}, start_date:{start_date},'
                       f' return_date:{return_date}, state:{state},'
                       f' Rent created!')

        except IntegrityError:
            session.rollback()
            typer.echo('An error has occurred during the creation '
                       'of the Rent')
        except ValidationError:
            session.rollback()
            typer.echo('An error has occurred during the creation '
                       'of the Rent')


if __name__ == "__main__":
    app()
