import re
from datetime import date

# New Validators
from sqlmodel import select

from business_logic.business_logic import RentBusinessLogic
from databases.db import get_db_session
from models.films_and_rents import Film

session = get_db_session()


def validate_email(email: str) -> str:
    if not email:
        raise ValueError('No email provided')
    if not re.match("[^@]+@[^@]+\.[^@]+", email):
        raise AssertionError('Provided email is not an email address')

    return email


def validate_phone(phone: str) -> str:
    if not phone:
        raise ValueError('No phone provided')
    if not re.match("\d{3}-\d{4}-\d{4}$", phone):
        raise AssertionError('Provided phone is not an valid please use'
                             'the following format (XXX-XXXX-XXXX)')
    return phone


def validate_film_type(film_type: str) -> str:
    if film_type not in ('movie', 'serie'):
        raise AssertionError('film_type should be movie or serie')
    return film_type


def validate_gender(gender: str) -> str:
    if gender not in ('male', 'feminine'):
        raise AssertionError('gender should be male or feminine')
    return gender


def validate_person_type(person_type: str) -> str:
    if person_type not in ('film related', 'client'):
        raise AssertionError('person_type should be film related or client')
    return person_type


def validate_person_type_client(person_type: str) -> str:
    if person_type != 'client':
        raise AssertionError('person_type should be client')
    return person_type


def validate_rent_state(film_type: str) -> str:
    if film_type not in ('open', 'close'):
        raise AssertionError('state should be open or close')
    return film_type


def validate_amount(amount: int, film_id: int):
    statement = select(Film).where(Film.id == film_id)
    film = session.exec(statement).one_or_none()

    if (availability := (film.get_availability(film_id) - amount)) < 0:
        raise AssertionError(
            f'The amount exceeds availability by {-availability}')
    return amount


# Film Validators

def validator_date_limit_today(input_date: date) -> date:
    """
    Validate that the input date is not in the future

    Args:
        input_date (date): Input date

    Raises:
        ValidationError: The inserted date has not happened yet

    Return:
        input_date (date): Input date
    """
    if input_date > date.today():
        raise AssertionError("The inserted date has not happened yet")

    return input_date


def validator_no_negative(num: int) -> int:
    """
    Validate that the number is not negative

    Args:
        num (int): Input number

    Raises:
        ValidationError: The inserted number has to be '0' or positive

    Return:
        num (int): Input number
    """
    if num < 0:
        raise AssertionError("The inserted number has to be '0' or positive")

    return num


# Rent Validators

amount_day_max_limit = 15


class RentValidation:
    """
    The class contains all the validations of the rent app
    """

    # Methods about validate date
    @classmethod
    def validate_date_gt_max_limit(cls, date1: date, date2: date, field: str):
        """
        Validate that the difference between both dates is not greater than max
         limit.

        Args:
            date1 (date): Input date1
            date2 (date): Input date2
            field (str): Indicate the field to report the ValidationError
        Raises:
            ValidationError: This return date has to be before the max limit
        """
        if RentBusinessLogic.get_date_diff_in_days(date1, date2) > \
                amount_day_max_limit:
            raise AssertionError(
                {field: (f'This return date has to be before'
                         f' {amount_day_max_limit} days from the start date')
                 })

    @staticmethod
    def validate_date1_gr_or_eq_date2(date1: date, date2: date, field: str):
        """
        Validate that date2 is not greater or equal than date2

        Args:
            date1 (date): Input date1
            date2 (date): Input date2
            field (str): Indicate the field to report the ValidationError
        Raises:
            ValidationError: date2 has to be after the date1
        """
        if date1 is not None:
            if date2 >= date1:
                raise AssertionError(
                    {field: ('This date has to be'
                             ' after the start date')
                     })

    @staticmethod
    def validate_date1_eq_or_low_date2(date1: date, date2: date, field: str):
        """
        Validate that date1 is not lower or equal than date2

        Args:
            date1 (date): Input date1
            date2 (date): Input date2
            field (str): Indicate the field to report the ValidationError

        Raises:
            ValidationError: date1 has to be after the date2
        """
        if date1 <= date2:
            raise AssertionError(
                {field: ('This date has to be'
                         ' after the start date')
                 })
