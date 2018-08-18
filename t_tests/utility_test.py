"""
utility_test.py

Tests of t_games/utility.py.

Classes:
NumberPluralTests: Tests of number word & singular/plural. (unittest.TestCase)
NumberWordTests: Tests of converting numbers to words. (unittest.TestCase)
PluralTest: Tests of getting the singular/plural form. (unittest.TestCase)
"""


import unittest

import t_games.utility as utility


class NumberPluralTest(unittest.TestCase):
    """Tests of getting the number word and singular/plural. (unittest.TestCase)"""

    def testPlural(self):
        """Test getting a plural form of a word."""
        self.assertEqual('seven cards', utility.number_plural(7, 'card'))

    def testPluralNoS(self):
        """Test getting a plural form of a word without adding s."""
        self.assertEqual('five dice', utility.number_plural(5, 'die', 'dice'))

    def testSingular(self):
        """Test getting a plural form of a word."""
        self.assertEqual('one card', utility.number_plural(1, 'card'))

    def testSingularNoS(self):
        """Test getting a plural form of a word wihtout adding s."""
        self.assertEqual('one die', utility.number_plural(1, 'die', 'dice'))

    def testZero(self):
        """Test getting a plural with zero."""
        self.assertEqual('zero cards', utility.number_plural(0, 'card'))

    def testZeroNoS(self):
        """Test getting a plural with zero and not adding s."""
        self.assertEqual('zero dice', utility.number_plural(0, 'die', 'dice'))


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


class PluralTest(unittest.TestCase):
    """Tests of getting the singular/plural form. (unittest.TestCase)"""

    def testPlural(self):
        """Test getting a plural form of a word."""
        self.assertEqual('cards', utility.plural(7, 'card'))

    def testPluralNoS(self):
        """Test getting a plural form of a word without adding s."""
        self.assertEqual('dice', utility.plural(5, 'die', 'dice'))

    def testSingular(self):
        """Test getting a plural form of a word."""
        self.assertEqual('card', utility.plural(1, 'card'))

    def testSingularNoS(self):
        """Test getting a plural form of a word wihtout adding s."""
        self.assertEqual('die', utility.plural(1, 'die', 'dice'))

    def testZero(self):
        """Test getting a plural with zero."""
        self.assertEqual('cards', utility.plural(0, 'card'))

    def testZeroNoS(self):
        """Test getting a plural with zero and not adding s."""
        self.assertEqual('dice', utility.plural(0, 'die', 'dice'))


if __name__ == '__main__':
    unittest.main()
