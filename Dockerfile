FROM python:3.10-alpine

WORKDIR /film_rental_system

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY Pipfile .
COPY Pipfile.lock .
RUN pip install pipenv
RUN pipenv lock --pre --requirements > requirements.txt
RUN apk add --no-cache zlib-dev jpeg-dev gcc musl-dev linux-headers
RUN pip install -r requirements.txt

COPY . .
