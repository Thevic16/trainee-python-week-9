from datetime import date
import unittest
from unittest.mock import patch

from validators.validators import (validator_date_limit_today,
                                   validator_no_negative, RentValidation,
                                   validate_email, validate_phone,
                                   validate_film_type, validate_gender,
                                   validate_person_type_client,
                                   validate_rent_state)


def fake_today():
    return date(year=2020, month=1, day=1)


class ValidationsTestCase(unittest.TestCase):
    def setUp(self):
        # Defining variables
        self.previous_date = date(year=2019, month=12, day=1)
        self.later_date = date(year=2020, month=1, day=2)
        self.positive_number = 5
        self.negative_number = -5

    def test_validate_email(self):
        with self.assertRaises(ValueError):
            validate_email(None)

        with self.assertRaises(AssertionError):
            validate_email("admingmail.com")

        with self.assertRaises(AssertionError):
            validate_email("admin@gmailcom")

        self.assertEqual("admin@gmail.com", validate_email("admin@gmail.com"))

    def test_validate_phone(self):
        with self.assertRaises(ValueError):
            validate_phone(None)

        with self.assertRaises(AssertionError):
            validate_phone("5034-4896-7854")

        self.assertEqual("503-4896-7854", validate_phone("503-4896-7854"))

    def test_validate_film_type(self):
        with self.assertRaises(AssertionError):
            validate_film_type("moviee")

        with self.assertRaises(AssertionError):
            validate_film_type("seriee")

        self.assertEqual("movie", validate_film_type("movie"))
        self.assertEqual("serie", validate_film_type("serie"))

    def test_validate_gender(self):
        with self.assertRaises(AssertionError):
            validate_gender("malee")

        with self.assertRaises(AssertionError):
            validate_gender("femininee")

        self.assertEqual("male", validate_gender("male"))
        self.assertEqual("feminine", validate_gender("feminine"))

    def test_validate_person_type_client(self):
        with self.assertRaises(AssertionError):
            validate_person_type_client("clientt")

        self.assertEqual("client", validate_person_type_client("client"))

    def test_validate_rent_state(self):
        with self.assertRaises(AssertionError):
            validate_rent_state('openn')

        with self.assertRaises(AssertionError):
            validate_rent_state('closee')

        self.assertEqual("open", validate_rent_state('open'))
        self.assertEqual("close", validate_rent_state("close"))

    @patch("validators.validators.date")
    def test_validator_date_limit_today(self, mock_today):
        # Set mock
        mock_today.today.return_value = fake_today()

        self.assertEqual(self.previous_date,
                         validator_date_limit_today(
                             self.previous_date))

        with self.assertRaises(AssertionError):
            validator_date_limit_today(self.later_date)

    def test_validator_no_negative(self):
        self.assertEqual(self.positive_number,
                         validator_no_negative(self.positive_number))

        with self.assertRaises(AssertionError):
            validator_no_negative(self.negative_number)

    def test_validate_date_gt_max_limit(self):
        with self.assertRaises(AssertionError):
            date1 = date(year=2022, month=1, day=17)
            date2 = date(year=2022, month=1, day=1)
            RentValidation.validate_date_gt_max_limit(date1, date2, "test")

    def test_validate_date1_gr_or_eq_date2(self):
        with self.assertRaises(AssertionError):
            date1 = date(year=2022, month=1, day=1)
            date2 = date(year=2022, month=1, day=1)
            RentValidation.validate_date1_gr_or_eq_date2(date1, date2,
                                                         "test")

        with self.assertRaises(AssertionError):
            date1 = date(year=2022, month=1, day=1)
            date2 = date(year=2022, month=1, day=2)
            RentValidation.validate_date1_gr_or_eq_date2(date1, date2,
                                                         "test")

    def test_validate_date1_eq_or_low_date2(self):
        with self.assertRaises(AssertionError):
            date1 = date(year=2022, month=1, day=1)
            date2 = date(year=2022, month=1, day=1)
            RentValidation.validate_date1_eq_or_low_date2(date1, date2,
                                                          "test")

        with self.assertRaises(AssertionError):
            date1 = date(year=2022, month=1, day=1)
            date2 = date(year=2022, month=1, day=2)
            RentValidation.validate_date1_eq_or_low_date2(date1, date2,
                                                          "test")


if __name__ == '__main__':
    unittest.main()
