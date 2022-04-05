from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi_redis_cache import cache_one_month
from sqlmodel import select
from starlette import status

from databases.db import get_db_session
from models.films_and_rents import (CategoryRead, Category, CategoryCreate,
                                    FilmRead, Film, FilmCreate, SeasonRead,
                                    Season, SeasonCreate, ChapterRead, Chapter,
                                    ChapterCreate, Poster, PosterRead)
from s3_events.s3_utils import S3_SERVICE
from security.security import get_admin_user

# S3 related imports
import os
from dotenv import load_dotenv
from fastapi.param_functions import File
from fastapi.datastructures import UploadFile
import datetime

from utilities.logger import Logger

load_dotenv()

router = APIRouter()

session = get_db_session()

# S3 service environment variables and service
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.environ.get("AWS_REGION")
S3_Bucket = os.environ.get("S3_Bucket")
S3_Key = os.environ.get("S3_Key")

# Object of S3_SERVICE Class
s3_client = S3_SERVICE(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION)


# Film Related Routes
@router.get('/api/categories', response_model=List[CategoryRead],
            status_code=status.HTTP_200_OK)
@cache_one_month()
async def get_all_categories():
    session.rollback()
    statement = select(Category)
    results = session.exec(statement).all()

    return results


@router.get('/api/categories/{category_id}', response_model=CategoryRead)
@cache_one_month()
async def get_by_id_a_category(category_id: int):
    session.rollback()
    statement = select(Category).where(Category.id == category_id)
    result = session.exec(statement).first()

    return result


@router.post('/api/categories', response_model=CategoryRead,
             status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(get_admin_user)])
async def create_a_category(category: CategoryCreate):
    new_category = Category(name=category.name,
                            description=category.description)
    session.rollback()
    session.add(new_category)

    session.commit()

    return new_category


@router.put('/api/categories/{category_id}', response_model=CategoryRead,
            dependencies=[Depends(get_admin_user)])
async def update_a_category(category_id: int, category: CategoryCreate):
    session.rollback()
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
    session.rollback()
    statement = select(Category).where(Category.id == category_id)

    result = session.exec(statement).one_or_none()

    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Resource Not Found")

    session.delete(result)
    session.commit()

    return result


@router.get('/api/films', response_model=List[FilmRead],
            status_code=status.HTTP_200_OK)
@cache_one_month()
async def get_all_films():
    session.rollback()
    statement = select(Film)
    results = session.exec(statement).all()

    for film in results:
        if film:
            film.availability = Film.get_availability(film.id)
            session.commit()

    return results


@router.get('/api/films/{film_id}', response_model=FilmRead)
@cache_one_month()
async def get_by_id_a_film(film_id: int):
    session.rollback()
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
    session.rollback()
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
    session.rollback()
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
    session.rollback()
    statement = select(Film).where(Film.id == film_id)

    result = session.exec(statement).one_or_none()

    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Resource Not Found")

    session.delete(result)
    session.commit()

    return result


@router.get('/api/posters', response_model=List[PosterRead],
            status_code=status.HTTP_200_OK)
@cache_one_month()
async def get_all_posters():
    session.rollback()
    statement = select(Poster)
    results = session.exec(statement).all()

    return results


@router.get('/api/posters/{poster_id}', response_model=PosterRead)
@cache_one_month()
async def get_by_id_a_poster(poster_id: int):
    session.rollback()
    statement = select(Poster).where(Poster.id == poster_id)
    result = session.exec(statement).first()

    return result


@router.post("/api/poster/upload/{film_id}", status_code=200,
             description="Upload png poster asset to S3 ")
async def upload_poster(film_id: int, fileobject: UploadFile = File(...)):
    filename = fileobject.filename
    current_time = datetime.datetime.now()
    # split the file name into two different path (string +  extention)
    split_file_name = os.path.splitext(
        filename)

    # for realtime application you must have genertae unique name for the file
    file_name_unique = str(current_time.timestamp()).replace('.', '')

    file_extension = split_file_name[1]  # file extention
    # Converting tempfile.SpooledTemporaryFile to io.BytesIO
    data = fileobject.file._file
    uploads3 = await s3_client.upload_fileobj(
        bucket=S3_Bucket,
        key=S3_Key + file_name_unique + file_extension,
        fileobject=data)

    if uploads3:
        s3_url = f"https://" \
                 f"{S3_Bucket}.s3.{AWS_REGION}.amazonaws.com/" \
                 f"{S3_Key}{file_name_unique + file_extension}"
        Logger.info(f"s3_url:{s3_url}")

        session.rollback()
        new_poster = Poster(film_id=film_id,
                            link=s3_url)
        session.add(new_poster)
        session.commit()

        return {"status": "success", "image_url": s3_url}  # response added
    else:
        raise HTTPException(status_code=400, detail="Failed to upload in S3")


@router.delete('/api/posters/{poster_id}',
               status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(get_admin_user)])
async def delete_a_poster(poster_id: int):
    session.rollback()
    statement = select(Poster).where(Poster.id == poster_id)

    result = session.exec(statement).one_or_none()

    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Resource Not Found")

    session.delete(result)
    session.commit()

    return result


@router.get('/api/seasons', response_model=List[SeasonRead],
            status_code=status.HTTP_200_OK)
@cache_one_month()
async def get_all_seasons():
    session.rollback()
    statement = select(Season)
    results = session.exec(statement).all()

    return results


@router.get('/api/seasons/{season_id}', response_model=SeasonRead)
@cache_one_month()
async def get_by_a_season(season_id: int):
    session.rollback()
    statement = select(Season).where(Season.id == season_id)
    result = session.exec(statement).first()

    return result


@router.post('/api/seasons', response_model=SeasonRead,
             status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(get_admin_user)])
async def create_a_season(season: SeasonCreate):
    session.rollback()
    new_season = Season(film_id=season.film_id,
                        title=season.title,
                        season_prequel_id=season.season_prequel_id)

    session.add(new_season)
    session.commit()

    return new_season


@router.put('/api/seasons/{season_id}', response_model=SeasonRead,
            dependencies=[Depends(get_admin_user)])
async def update_a_season(season_id: int, season: SeasonCreate):
    session.rollback()
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
    session.rollback()
    statement = select(Season).where(Season.id == season_id)

    result = session.exec(statement).one_or_none()

    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Resource Not Found")

    session.delete(result)
    session.commit()

    return result


@router.get('/api/chapters', response_model=List[ChapterRead],
            status_code=status.HTTP_200_OK)
@cache_one_month()
async def get_all_chapters():
    session.rollback()
    statement = select(Chapter)
    results = session.exec(statement).all()

    return results


@router.get('/api/chapters/{chapter_id}', response_model=ChapterRead)
@cache_one_month()
async def get_by_id_a_chapter(chapter_id: int):
    session.rollback()
    statement = select(Chapter).where(Chapter.id == chapter_id)
    result = session.exec(statement).first()

    return result


@router.post('/api/chapters', response_model=ChapterRead,
             status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(get_admin_user)])
async def create_a_chapter(chapter: ChapterCreate):
    session.rollback()
    new_chapter = Chapter(season_id=chapter.season_id,
                          title=chapter.title,
                          chapter_prequel_id=chapter.chapter_prequel_id)

    session.add(new_chapter)

    session.commit()

    return new_chapter


@router.put('/api/chapters/{chapter_id}', response_model=ChapterRead,
            dependencies=[Depends(get_admin_user)])
async def update_a_chapter(chapter_id: int, chapter: ChapterCreate):
    session.rollback()
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
    session.rollback()
    statement = select(Chapter).where(Chapter.id == chapter_id)

    result = session.exec(statement).one_or_none()

    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Resource Not Found")

    session.delete(result)
    session.commit()

    return result
