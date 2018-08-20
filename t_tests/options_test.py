"""
options_test.py

Unit testing of options.py

Classes:
AllRangeTest: Tests of the all inclusive range. (unittest.TestCase)
OptionTextTest: Tests of text representations of OptionSet. (unittest.TestCase)
ParseTest: Tests of OptionSet.parse_settings changing settings_text (TestCase)
ReprTest: Test the repr of an OptionSet. (unittest.TestCase)
"""


import unittest

from t_games import game
from t_games import options
from t_games import player


class AllRangeTest(unittest.TestCase):
    """Tests of the all inclusive range. (unittest.TestCase)"""

    def setUp(self):
        self.all_range = options.AllRange()

    def testRepr(self):
        """Test the computer readable text representation of AllRange."""
        self.assertEqual('AllRange()', repr(self.all_range))

    def testReprSimilar(self):
        """Test evaluating the computer readable text representation of AllRange."""
        AllRange = options.AllRange
        self.assertTrue('everything' in eval(repr(self.all_range)))


class OptionTextTest(unittest.TestCase):
    """Tests of text representations of OptionSet. (unittest.TestCase)"""

    def setUp(self):
        self.game = game.Game(player.Bot(), 'none')
        self.option_set = self.game.option_set
        self.option_set.add_option('floats')

    def testRepr(self):
        """Test the debugging text representation of an option set."""
        self.assertEqual('<OptionSet for Null with 1 option>', repr(self.option_set))

    def testReprMultiple(self):
        """Test the repr of an option set with multiple options."""
        self.option_set.add_option('weight', converter = options.lower, default = 'duck')
        self.assertEqual('<OptionSet for Null with 2 options>', repr(self.option_set))


class ParseTest(unittest.TestCase):
    """Tests of OptionSet.parse_settings changing OptionSet.settings_text (TestCase)"""

    def setUp(self):
        self.option_set = options.OptionSet(object())
        self.option_set.add_option('spam')
        self.option_set.add_option('three', ['3'], int, 5)

    def testBasic(self):
        """Test a simple option."""
        self.option_set.parse_settings('spam')
        self.assertEqual('spam', self.option_set.settings_text)

    def testEquals(self):
        """Test setting an option value."""
        self.option_set.parse_settings('three=5')
        self.assertEqual('three=5', self.option_set.settings_text)

    def testEqualsSpace(self):
        """Test setting an option value with spaces."""
        self.option_set.parse_settings('three = 5')
        self.assertEqual('three=5', self.option_set.settings_text)

    def testEqualsSpaceAfter(self):
        """Test setting an option value with a space after."""
        self.option_set.parse_settings('three= 5')
        self.assertEqual('three=5', self.option_set.settings_text)

    def testEqualsSpaceBefore(self):
        """Test setting an option value with a space before."""
        self.option_set.parse_settings('three =5')
        self.assertEqual('three=5', self.option_set.settings_text)

    def testEqualsSpaceMultiple(self):
        """Test setting an option value with multiple spaces."""
        self.option_set.parse_settings('three  =  5')
        self.assertEqual('three=5', self.option_set.settings_text)

    def testSort(self):
        """Test sorting multiple options."""
        self.option_set.parse_settings('three=3 spam')
        self.assertEqual('spam three=3', self.option_set.settings_text)


class ReprTest(unittest.TestCase):
    """Test the repr of an OptionSet. (unittest.TestCase)"""

    def setUp(self):
        self.game = game.Game(player.Bot(), '')
        self.options = options.OptionSet(self.game)

    def testOneOption(self):
        """Test repr(OptionSet) with zero options."""
        self.options.add_option('spam')
        self.assertEqual('<OptionSet for Null with 1 option>', repr(self.options))

    def testMultipleOptions(self):
        """Test repr(OptionSet) with more than one option."""
        self.options.add_option('spam')
        self.options.add_option('eggs')
        self.options.add_option('"Bob"')
        self.assertEqual('<OptionSet for Null with 3 options>', repr(self.options))

    def testZeroOptions(self):
        """Test repr(OptionSet) with zero options."""
        self.assertEqual('<OptionSet for Null with 0 options>', repr(self.options))


if __name__ == '__main__':
    unittest.main()