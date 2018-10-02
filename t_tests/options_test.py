"""
options_test.py

Unit testing of options.py

Classes:
AddOptionTest: Tests of adding options to OptionSets. (unittest.TestCase)
AllRangeTest: Tests of the all inclusive range. (unittest.TestCase)
OptionTextTest: Tests of text representations of OptionSet. (unittest.TestCase)
ParseTest: Tests of OptionSet.parse_settings changing settings_text (TestCase)
ReprTest: Test the repr of an OptionSet. (unittest.TestCase)
"""


import unittest

from t_games import game
from t_games import options
from t_games import player
import unitility


class AddOptionTest(unittest.TestCase):
    """Tests of adding options to OptionSet objects. (unittest.TestCase)"""

    def setUp(self):
        self.game = game.Game(unitility.AutoBot(), 'none')
        self.option_set = self.game.option_set

    def testAddAlias(self):
        """Test adding an option with an alias."""
        self.option_set.add_option('spam', ['s', 'spiced-ham'])
        check = {'s': 'spam', 'spiced-ham': 'spam', 'spam': 'spam'}
        self.assertEqual(check, self.option_set.aliases)

    def testAddBoolQuestion(self):
        """Test the question for an option with a yes or no question."""
        query = 'Would you like some spam with your spam? '
        self.option_set.add_option('spam', question = query + 'bool')
        self.assertEqual(query, self.option_set.definitions[0]['question'])

    def testAddBoolQuestionType(self):
        """Test the question type for an option with a yes or no question."""
        query = 'Would you like some spam with your spam? '
        self.option_set.add_option('spam', question = query + 'bool')
        self.assertEqual('bool', self.option_set.definitions[0]['question_type'])

    def testAddBotCountQuestionType(self):
        """Test the question type for a bot option with paramters."""
        self.option_set.add_option('spam-bot', action = 'bot', value = (1, 2))
        self.assertEqual('bot-count', self.option_set.definitions[0]['question_type'])

    def testAddBotParamQuestionType(self):
        """Test the question type for a bot option without paramters."""
        self.option_set.add_option('spam-bot', action = 'bot', value = None)
        self.assertEqual('bot-param', self.option_set.definitions[0]['question_type'])

    def testAddDefault(self):
        """Test adding an option using all the defaults."""
        self.option_set.add_option('spam')
        self.assertEqual('spam', self.option_set.definitions[0]['name'])
        self.assertEqual(str, self.option_set.definitions[0]['converter'])
        self.assertEqual(False, self.option_set.definitions[0]['default'])
        self.assertEqual(True, self.option_set.definitions[0]['value'])
        self.assertEqual('spam', self.option_set.definitions[0]['target'])
        self.assertEqual('assign', self.option_set.definitions[0]['action'])
        self.assertEqual('', self.option_set.definitions[0]['question'])
        self.assertEqual('', self.option_set.definitions[0]['error_text'])
        self.assertEqual('none', self.option_set.definitions[0]['question_type'])

    def testAddHyphenated(self):
        """Test adding an option with a hyphenated name."""
        self.option_set.add_option('spam-spam-eggs')
        self.assertEqual('spam_spam_eggs', self.option_set.definitions[0]['target'])

    def testAddHyphenatedBot(self):
        """Test adding a bot option with a hyphenated name."""
        self.option_set.add_option('spam-bot', action = 'bot')
        self.assertEqual('spam-bot', self.option_set.definitions[0]['target'])


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
        self.game = game.Game(unitility.AutoBot(), 'none')
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

    def testAlias(self):
        """Test an option alias."""
        self.option_set.parse_settings('3=5')
        self.assertEqual('three=5', self.option_set.settings_text)

    def testBasic(self):
        """Test a simple option."""
        self.option_set.parse_settings('spam')
        self.assertEqual('spam', self.option_set.settings_text)

    def testDoubleEquals(self):
        """Test an invalid option."""
        self.option_set.parse_settings('one=1=juan')
        self.assertEqual("Syntax error with equals: 'one=1=juan'.", self.option_set.errors[0])

    def testEquals(self):
        """Test setting an option value."""
        self.option_set.parse_settings('three=5')
        self.assertEqual('three=5', self.option_set.settings_text)

    def testInvalid(self):
        """Test an invalid option."""
        self.option_set.parse_settings('splitter')
        self.assertEqual('Unrecognized option: splitter.', self.option_set.errors[0])

    def testInvalidEquals(self):
        """Test an invalid option with a value assigned."""
        self.option_set.parse_settings('splitter = jpf')
        self.assertEqual('Unrecognized option: splitter.', self.option_set.errors[0])

    def testInvalidMixedError(self):
        """Test error for an invalid option mixed with other options."""
        self.option_set.parse_settings('spam splitter three = 3')
        self.assertEqual('Unrecognized option: splitter.', self.option_set.errors[0])

    def testInvalidMixedParse(self):
        """Test parsing valid options when mixed with an invalid one."""
        self.option_set.parse_settings('spam splitter three = 3')
        self.assertEqual('spam three=3', self.option_set.settings_text)

    def testInvalidRepeat(self):
        """Test an invalid option with a repeat."""
        self.option_set.parse_settings('splitter * 3')
        self.assertEqual('Unrecognized option: splitter.', self.option_set.errors[0])

    def testRepeat(self):
        """Test repeatedly setting an option value."""
        self.option_set.parse_settings('spam * 3')
        self.assertEqual('spam spam spam', self.option_set.settings_text)

    def testRepeatInvalid(self):
        """Test an invalid repeat value."""
        self.option_set.parse_settings('spam * three')
        self.assertEqual("Invalid repeat value: 'spam*three'.", self.option_set.errors[0])

    def testRepeatNegative(self):
        """Test a negative repeat value."""
        self.option_set.parse_settings('spam * -1')
        self.assertEqual('', self.option_set.settings_text)

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
        self.game = game.Game(unitility.AutoBot(), '')
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


class TakeActionTest(unittest.TestCase):
    """Tests of OptionSet.take_action."""

    def setUp(self):
        self.game = game.Game(unitility.AutoBot(), '')
        self.options = options.OptionSet(self.game)

    def testAppend(self):
        """Test appending a value to the option."""
        self.options.settings['test'] = ['spam', 'spam']
        self.options.take_action({'action': 'append', 'target': 'test'}, 'eggs')
        self.assertEqual(['spam', 'spam', 'eggs'], self.options.settings['test'])

    def testAppendEmpty(self):
        """Test appending to an empty value to the option."""
        self.options.take_action({'action': 'append', 'target': 'test'}, 'eggs')
        self.assertEqual(['eggs'], self.options.settings['test'])

    def testAssign(self):
        """Test assigning a value to the option."""
        self.options.take_action({'action': 'assign', 'target': 'test'}, 108)
        self.assertEqual(108, self.options.settings['test'])

    def testBotList(self):
        """Test assigning a bot with parameters."""
        self.game.bot_classes = {'fred': object, 'george': int}
        self.options.take_action({'action': 'bot', 'target': 'fred'}, (1, 0, 8))
        self.assertEqual([(object, (1, 0, 8))], self.options.settings['bots'])

    def testBotPlain(self):
        """Test assigning a bot with no parameters."""
        self.game.bot_classes = {'fred': object, 'george': int}
        self.options.take_action({'action': 'bot', 'target': 'george'}, True)
        self.assertEqual([(int, [])], self.options.settings['bots'])

    def testBotSecond(self):
        """Test assigning a second bot"""
        self.game.bot_classes = {'fred': object, 'george': int}
        self.options.settings['bots'] = [(object, ['crazy'])]
        self.options.take_action({'action': 'bot', 'target': 'george'}, True)
        self.assertEqual([(object, ['crazy']), (int, [])], self.options.settings['bots'])

    def testBotSingle(self):
        """Test assigning a bot with one parameter."""
        self.game.bot_classes = {'fred': object, 'george': int}
        self.options.take_action({'action': 'bot', 'target': 'fred'}, 'crazy')
        self.assertEqual([(object, ['crazy'])], self.options.settings['bots'])

    def testKey(self):
        """Test assigning an option value to a key."""
        self.game.test = {}
        self.options.take_action({'action': 'key=test', 'target': self.game.test}, 108)
        self.assertEqual(108, self.game.test['test'])

    def testMap(self):
        """Test assigning an option value from a mapping."""
        self.game.test = {'low': 108, 'high': 801}
        self.options.take_action({'action': 'map', 'value': self.game.test, 'target': 'test'}, 'high')
        self.assertEqual(801, self.options.settings['test'])


if __name__ == '__main__':
    unittest.main()