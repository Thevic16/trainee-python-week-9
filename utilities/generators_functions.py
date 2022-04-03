import string
from random import randint, uniform, randrange, choices
from datetime import datetime, timedelta, date


def get_random_string(string_len: int):
    return ''.join(choices(string.ascii_letters, k=string_len))


def gen_dates():
    start = datetime.now()
    random_amount_days = randint(2, 15)
    end = datetime.now()
    end += timedelta(days=random_amount_days)

    return {'start': start.today(), 'end': end.today()}


def gen_date():
    start_date = date(1970, 1, 1)
    end_date = date(2015, 1, 1)

    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = randrange(days_between_dates)
    random_date = start_date + timedelta(days=random_number_of_days)

    return random_date


def gen_person_gender():
    random_number = randint(0, 100)

    if random_number <= 40:
        return 'male'
    elif random_number <= 80:
        return 'feminine'
    else:
        return 'other'


def gen_person_type():
    random_number = randint(0, 100)

    if random_number < 50:
        return 'film related'
    else:
        return 'client'


def gen_random_int():
    return randint(0, 100)


def gen_random_float():
    return uniform(0, 1) * 100


def gen_random_film_type():
    random_number = randint(0, 100)

    if random_number < 50:
        return 'movie'
    else:
        return 'serie'


def gen_phone():
    return f'{randint(0, 9)}{randint(0, 9)}{randint(0, 9)}-' \
           f'{randint(0, 9)}{randint(0, 9)}{randint(0, 9)}{randint(0, 9)}-' \
           f'{randint(0, 9)}{randint(0, 9)}{randint(0, 9)}{randint(0, 9)}'


def gen_number(start, end):
    return randint(start, end)
