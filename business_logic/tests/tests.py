import unittest
from datetime import date
from business_logic.business_logic import (FilmBusinessLogic,
                                           PersonBusinessLogic,
                                           RentBusinessLogic)
from unittest.mock import patch


def fake_today():
    return date(year=2022, month=3, day=13)


class BusinessLogicTestCase(unittest.TestCase):

    def setUp(self):
        self.price_by_day = 10
        self.stock = 10
        self.availability = 8
        self.amount = 2
        self.start_date = date(year=2050, month=1, day=1)
        self.return_date = date(year=2050, month=1, day=2)
        self.actual_return_date = date(year=2050, month=1, day=5)

    def test_validate_stock_greater_availability(self):
        with self.assertRaises(AssertionError):
            stock = 5
            availability = 10
            FilmBusinessLogic.validate_stock_greater_availability(
                stock, availability)

    @patch("business_logic.business_logic.date")
    def test_get_age_by_birthday(self, mock_today):
        # Set mock
        mock_today.today.return_value = fake_today()

        age = 22
        self.assertEqual(age, PersonBusinessLogic.get_age_by_birthday(
            date(year=1999, month=3, day=16)))

    def test_get_rent_cost(self):
        cost = 20
        self.assertEqual(cost,
                         RentBusinessLogic.get_rent_cost(self.amount,
                                                         self.start_date,
                                                         self.return_date,
                                                         None,
                                                         self.price_by_day))

    def test_get_actual_cost(self):
        cost = 92
        self.assertEqual(cost,
                         RentBusinessLogic.get_actual_cost
                         (self.amount,
                          self.start_date,
                          self.return_date,
                          self.actual_return_date,
                          self.price_by_day))


if __name__ == '__main__':
    unittest.main()
