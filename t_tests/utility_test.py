"""
utility_test.py

Tests of t_games/utility.py.

Classes:
NumberWordTests: Tests of converting numbers to words. (unittest.TestCase)
"""


import unittest

import t_games.utility as utility


class NumberWordTests(unittest.TestCase):
    """Tests of converting numbers to words. (unittest.TestCase)"""

    def testCompoundDashed(self):
        """Test wording a number with multiple words and a dash."""
        self.assertEqual('six hundred sixty-six', utility.number_word(666))

    def testOrdinalComplex(self):
        """Test ordinalling a number ending in >= three zeros and > one non-zero digits."""
        check = 'one quadrillion twenty-three trillion four hundred five billion six hundred million'
        check = '{} seventy thousand eight hundred ninetieth'.format(check)
        self.assertEqual(check, utility.number_word(1023405600070890, True))

    def testOrdinalCompound(self):
        """Test ordinalling a number with multiple words."""
        self.assertEqual('one hundred eighth', utility.number_word(108, True))

    def testOrdinalCompoundDashed(self):
        """Test ordinalling a number with multiple words and a dash."""
        self.assertEqual('six hundred sixty-sixth', utility.number_word(666, True))

    def testOrdinalDashed(self):
        """Test ordinalling a number with a dash."""
        self.assertEqual('thirty-second', utility.number_word(32, True))

    def testOrdinalSingle(self):
        """Test ordinalling a single digit number."""
        self.assertEqual('third', utility.number_word(3, True))

    def testOrdinalTeen(self):
        """Test ordinalling a teenage number."""
        self.assertEqual('eighteenth', utility.number_word(18, True))

    def testOrdinalTens(self):
        """Test ordinalling a low multiple of ten."""
        self.assertEqual('fiftieth', utility.number_word(50, True))

    def testOrdinalTopHeavy(self):
        """Test ordinalling a number ending in at least three zeros."""
        self.assertEqual('five thousandth', utility.number_word(5000, True))

    def testOrdinalTopHeavyCompound(self):
        """Test ordinalling a number ending in >= three zeros and > one non-zero digits."""
        self.assertEqual('one million twenty-three thousandth', utility.number_word(1023000, True))

    def testOrdinalZero(self):
        """Test ordinalling zero."""
        self.assertEqual('zeroth', utility.number_word(0, True))

    def testTopHeavy(self):
        """Test wording a number ending in at least three zeros."""
        self.assertEqual('five thousand', utility.number_word(5000))

    def testZero(self):
        """Test wording zero."""
        self.assertEqual('zero', utility.number_word(0))


if __name__ == '__main__':
    unittest.main()
