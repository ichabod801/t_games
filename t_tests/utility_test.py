"""
utility_test.py

Tests of t_games/utility.py.

Classes:
FactorialTest: Tests of factorial functions in utility. (unittest.TestCase)
MedianTest: Test of median calculation. (unittest.TestCase)
NumTextTests: Tests of combined number and text handling. (unittest.TestCase)
NumberPluralTests: Tests of number word & singular/plural. (unittest.TestCase)
NumberWordTests: Tests of converting numbers to words. (unittest.TestCase)
OxfordTest: Tests of converting Python lists to English lists. (TestCase)
PluralTest: Tests of getting the singular/plural form. (unittest.TestCase)
PowTest: Tests of power calculations. (unittest.TestCase)
StreakTest: Tests of longest streak calculations. (unittest.TestCase)
"""


import unittest

from .. import utility
#from t_games import utility

class FactorialTest(unittest.TestCase):
    """Tests of factorial functions in utility. (unittest.TestCase)"""

    def testChooseLarge(self):
        """Test getting a large n choose r value."""
        self.assertEqual(2598960, utility.choose(52, 5))

    def testChooseSmall(self):
        """Test getting a small n choose r value."""
        self.assertEqual(10, utility.choose(5, 2))

    def testPermuteLarge(self):
        """Test getting a large n permute r value."""
        self.assertEqual(311875200, utility.permutations(52, 5))

    def testPermuteSmall(self):
        """Test getting a small n permute r value."""
        self.assertEqual(20, utility.permutations(5, 2))


class MeanTest(unittest.TestCase):
    """Test of mean calculation. (unittest.TestCase)"""

    def testEvenList(self):
        """Test a mean for an even number of values."""
        self.assertEqual(3.5, utility.mean([1, 2, 3, 4, 5, 6]))

    def testLeftSkew(self):
        """Test a mean lower than the median."""
        self.assertEqual(4.4, utility.mean([3, 1, 6, 5, 7]))

    def testNoSkew(self):
        """Test a mean equal to the median."""
        self.assertEqual(5.0, utility.mean([3, 7, 4, 6, 5]))

    def testRightSkew(self):
        """Test a mean higher than the median."""
        self.assertEqual(5.6, utility.mean([5, 3, 4, 9, 7]))


class MedianTest(unittest.TestCase):
    """Test of median calculation. (unittest.TestCase)"""

    def testEvenList(self):
        """Test a median for an even number of values."""
        self.assertEqual(3.5, utility.median([1, 2, 3, 4, 5, 6]))

    def testLeftSkew(self):
        """Test a median higher than the mean."""
        self.assertEqual(5, utility.median([3, 1, 6, 5, 7]))

    def testNoSkew(self):
        """Test a median equal to the mean."""
        self.assertEqual(5, utility.median([3, 7, 4, 6, 5]))

    def testRightSkew(self):
        """Test a median lower than the mean."""
        self.assertEqual(5, utility.median([5, 3, 4, 9, 7]))


class NumTextTest(unittest.TestCase):
    """Tests of combined number and text handling. (unittest.TestCase)"""

    def testForceNumeric(self):
        """Test focing a numeric form of a number."""
        self.assertEqual('9 points', utility.num_text(9, 'point', ':n'))

    def testForceWord(self):
        """Test focing a numeric form of a number."""
        self.assertEqual('eight hundred one corners', utility.num_text(801, 'corner', ':w'))

    def testFour(self):
        """Test using four parameters."""
        self.assertEqual('sixty-six geese', utility.num_text(66, 'goose', 'geese', ':w'))

    def testJustNumber(self):
        """Test only getting the word form of the number."""
        self.assertEqual('eight', utility.num_text(8))

    def testLarge(self):
        """Test a large number being numeric."""
        self.assertEqual('108 buddhas', utility.num_text(108, 'buddha'))

    def testOrdinal(self):
        """Test generating the ordinal form of a number."""
        self.assertEqual('fifth element', utility.num_text(5, 'element', ':o'))

    def testOrdinalForcedNumeric(self):
        """Test generating the ordinal form of a number."""
        self.assertEqual('5th element', utility.num_text(5, 'element', ':on'))

    def testOrdinalForcedWord(self):
        """Test generating the ordinal form of a number."""
        self.assertEqual('one hundred eighth street', utility.num_text(108, 'street', ':wo'))

    def testOrdinalNumeric(self):
        """Test generating the ordinal form of a number."""
        self.assertEqual('108th street', utility.num_text(108, 'street', ':o'))

    def testOrdinalNumericLow(self):
        """Test generating the ordinal form of a number."""
        self.assertEqual('23rd eyeball', utility.num_text(23, 'eyeball', ':o'))

    def testPlural(self):
        """Test getting a plural form of a word."""
        self.assertEqual('seven cards', utility.num_text(7, 'card'))

    def testPluralEs(self):
        """Test getting a plural form of a word with -es."""
        self.assertEqual('six hexes', utility.num_text(6, 'hex', ':e'))

    def testPluralNoS(self):
        """Test getting a plural form of a word without adding s."""
        self.assertEqual('five dice', utility.num_text(5, 'die', 'dice'))

    def testSingular(self):
        """Test getting a plural form of a word."""
        self.assertEqual('one card', utility.num_text(1, 'card'))

    def testSingularNoS(self):
        """Test getting a plural form of a word wihtout adding s."""
        self.assertEqual('one die', utility.num_text(1, 'die', 'dice'))

    def testZero(self):
        """Test getting a plural with zero."""
        self.assertEqual('zero cards', utility.num_text(0, 'card'))

    def testZeroNoS(self):
        """Test getting a plural with zero and not adding s."""
        self.assertEqual('zero dice', utility.num_text(0, 'die', 'dice'))


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


class OxfordTest(unittest.TestCase):
    """Tests of converting Python lists to English lists. (unittest.TestCase)"""

    def testAndEmpty(self):
        """Test converting an empty list to an English list."""
        self.assertEqual('', utility.oxford([]))

    def testAndMultiple(self):
        """Test converting multiple items to an English list."""
        self.assertEqual('spam, spam, spam, spam, spam, and eggs', utility.oxford(['spam'] * 5 + ['eggs']))

    def tesAndOne(self):
        """Test converting a single item list to an English list."""
        self.assertEqual('801', utility.oxford([801]))

    def testAndTwo(self):
        """Test converting two items to an English list."""
        self.assertEqual('yin and yang', utility.oxford(['yin', 'yang']))

    def testConvertedMulitiple(self):
        """Test making multiple item English lists with word conversions."""
        fractions = [1 / float(n) for n in range(1, 7)]
        check = '1.0000, 0.5000, 0.3333, 0.2500, 0.2000, and 0.1667'
        self.assertEqual(check, utility.oxford(fractions, word_format = '{:.4f}'))

    def testConvertedOne(self):
        """Test making single item English lists with word conversions."""
        self.assertEqual('3.1416', utility.oxford([utility.math.pi], word_format = '{:.4f}'))

    def testConvertedTwo(self):
        """Test making two item English lists with word conversions."""
        constants = [utility.math.pi, utility.math.e]
        self.assertEqual('3.1416 and 2.7183', utility.oxford(constants, word_format = '{:.4f}'))

    def testEverything(self):
        """Test conversion to an English list with all parameters."""
        check = "'False', 0, [], or False"
        self.assertEqual(check, utility.oxford(['False', 0, [], False], 'or', '{!r}'))

    def testOrMultiple(self):
        """Test converting multiple items to an English list."""
        self.assertEqual('(1, 2), (3, 4), or (5, 6)', utility.oxford([(1, 2), (3, 4), (5, 6)], 'or'))

    def testOrTwo(self):
        """Test converting two items to an English or list."""
        self.assertEqual('6 or 9', utility.oxford([6, 9], 'or'))


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


class PowTest(unittest.TestCase):
    """Tests of Adam West punching things. (unittest.TestCase)"""

    def testFractionalPower(self):
        """Test a power calcualtion with a fractional power."""
        self.assertEqual(9, utility.pow(81, 0.5))

    def testNegativeBase(self):
        """Test a power calculation with a negative base."""
        self.assertEqual(-81, utility.pow(-9, 2))

    def testNegativePower(self):
        """Test a power calculation with a negative power."""
        self.assertEqual(0.25, utility.pow(2, -2))

    def testLarge(self):
        """Test a large power calculation."""
        self.assertEqual(14693280768, utility.pow(108, 5))

    def testSmall(self):
        """Test a small power calculation."""
        self.assertEqual(81, utility.pow(3, 4))


class StreakTest(unittest.TestCase):
    """Tests of longest streak calculations. (unittest.TestCase)"""

    def setUp(self):
        self.results = [1, 1, -1, -1, -1, -1, 0, 1, -1, 0, 1, 1, 1]
        self.streaks = utility.streaks(self.results)

    def testCurrent(self):
        """Test the current streak calculation."""
        self.assertEqual((3, 1), self.streaks[:2])

    def testDuplicate(self):
        """Test a longest streak coming more than once in the results."""
        self.assertEqual(1, self.streaks[2][0])

    def testEarlier(self):
        """Test a longest streak coming earlier in the results."""
        self.assertEqual(4, self.streaks[2][-1])

    def testEmpty(self):
        """Test a longest streak with no results."""
        self.assertEqual((0, 0, [0, 0, 0]), utility.streaks([]))

    def testLater(self):
        """Test a longest streak coming later in the results."""
        self.assertEqual(3, self.streaks[2][1])

    def testNone(self):
        """Test a longest streak of zero."""
        streaks = utility.streaks([result for result in self.results if result])
        self.assertEqual(0, streaks[2][0])


if __name__ == '__main__':
    unittest.main()