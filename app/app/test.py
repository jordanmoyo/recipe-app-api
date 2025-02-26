"""sample test
"""
from django.test import TestCase  # type: ignore

from app import calc


class CalcTests(TestCase):
    """Test the calc module"""
    def test_add_numbers(self):
        """test that two numbers are added together
        """
        self.assertEqual(calc.add(3, 8), 11)

    def test_subtract_numbers(self):
        """test that values are subtracted and returned
        """
        self.assertEqual(calc.subtract(5, 11), 6)
