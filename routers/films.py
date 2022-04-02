from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from starlette import status

from database.db import get_db_session
from models.films_and_rents import (CategoryRead, Category, CategoryCreate,
                                    FilmRead, Film, FilmCreate, SeasonRead,
                                    Season, SeasonCreate, ChapterRead, Chapter,
                                    ChapterCreate)
from security.security import get_admin_user

router = APIRouter()

session = get_db_session()


# Film Related Routes
@router.get('/api/categories', response_model=List[CategoryRead],
            status_code=status.HTTP_200_OK)
async def get_all_categories():
    statement = select(Category)
    results = session.exec(statement).all()

    return results


@router.get('/api/categories/{category_id}', response_model=CategoryRead)
async def get_by_id_a_category(category_id: int):
    statement = select(Category).where(Category.id == category_id)
    result = session.exec(statement).first()

    return result


@router.post('/api/categories', response_model=CategoryRead,
             status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(get_admin_user)])
async def create_a_category(category: CategoryCreate):
    new_category = Category(name=category.name,
                            description=category.description)

    session.add(new_category)

    session.commit()

    return new_category


@router.put('/api/categories/{category_id}', response_model=CategoryRead,
            dependencies=[Depends(get_admin_user)])
async def update_a_category(category_id: int, category: CategoryCreate):
    statement = select(Category).where(Category.id == category_id)

    result = session.exec(statement).first()

    result.name = category.name
    result.description = category.description

    session.commit()

    return result


@router.delete('/api/categories/{category_id}',
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


@router.get('/api/films', response_model=List[FilmRead],
            status_code=status.HTTP_200_OK)
async def get_all_films():
    statement = select(Film)
    results = session.exec(statement).all()

    for film in results:
        if film:
            film.availability = Film.get_availability(film.id)
            session.commit()

    return results


@router.get('/api/films/{film_id}', response_model=FilmRead)
async def get_by_id_a_film(film_id: int):
    statement = select(Film).where(Film.id == film_id)
    result = session.exec(statement).first()

    if result:
        result.availability = Film.get_availability(film_id)
        session.commit()

    return result


@router.post('/api/films', response_model=FilmRead,
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


@router.put('/api/films/{film_id}', response_model=FilmRead,
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


@router.delete('/api/films/{film_id}',
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


@router.get('/api/seasons', response_model=List[SeasonRead],
            status_code=status.HTTP_200_OK)
async def get_all_seasons():
    statement = select(Season)
    results = session.exec(statement).all()

    return results


@router.get('/api/seasons/{season_id}', response_model=SeasonRead)
async def get_by_a_season(season_id: int):
    statement = select(Season).where(Season.id == season_id)
    result = session.exec(statement).first()

    return result


@router.post('/api/seasons', response_model=SeasonRead,
             status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(get_admin_user)])
async def create_a_season(season: SeasonCreate):
    new_season = Season(film_id=season.film_id,
                        title=season.title,
                        season_prequel_id=season.season_prequel_id)

    session.add(new_season)
    session.commit()

    return new_season


@router.put('/api/seasons/{season_id}', response_model=SeasonRead,
            dependencies=[Depends(get_admin_user)])
async def update_a_season(season_id: int, season: SeasonCreate):
    statement = select(Season).where(Season.id == season_id)

    result = session.exec(statement).first()

    result.film_id = season.film_id
    result.title = season.title
    result.season_prequel_id = season.season_prequel_id

    session.commit()

    return result


@router.delete('/api/seasons/{season_id}',
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


@router.get('/api/chapters', response_model=List[ChapterRead],
            status_code=status.HTTP_200_OK)
async def get_all_chapters():
    statement = select(Chapter)
    results = session.exec(statement).all()

    return results


@router.get('/api/chapters/{chapter_id}', response_model=ChapterRead)
async def get_by_id_a_chapter(chapter_id: int):
    statement = select(Chapter).where(Chapter.id == chapter_id)
    result = session.exec(statement).first()

    return result


@router.post('/api/chapters', response_model=ChapterRead,
             status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(get_admin_user)])
async def create_a_chapter(chapter: ChapterCreate):
    new_chapter = Chapter(season_id=chapter.season_id,
                          title=chapter.title,
                          chapter_prequel_id=chapter.chapter_prequel_id)

    session.add(new_chapter)

    session.commit()

    return new_chapter


@router.put('/api/chapters/{chapter_id}', response_model=ChapterRead,
            dependencies=[Depends(get_admin_user)])
async def update_a_chapter(chapter_id: int, chapter: ChapterCreate):
    statement = select(Chapter).where(Chapter.id == chapter_id)

    result = session.exec(statement).first()

    result.season_id = chapter.season_id
    result.title = chapter.title
    result.chapter_prequel_id = chapter.chapter_prequel_id

    session.commit()

    return result


@router.delete('/api/chapters/{chapter_id}',
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
