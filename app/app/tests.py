""""
Sample tests
"""

from django.test import SimpleTestCase

from app import calc

class CalcTestCase(SimpleTestCase):
    """ Test the calc module """

    def test_add_numbers(self):
        """ Test adding number """
        res = calc.add(10,20)
        self.assertEqual(res, 30)

    
    def test_substract_numbers(self):
        """ Test subtracting number """
        res = calc.substract(10,15)
        self.assertEqual(res, 5)