"""
player_test.py

Unittesting of t_games/player.py

Classes:
BotTest: Tests of the Bot class. (unittest.TestCase)
HumanoidAskCardTest: Tests of Humanoid asking for a card. (unittest.TestCase)
HumanoidAskIntListTest: Tests of Humaoid asking for integers. (TestCase)
HumanoidAskIntTest: Tests of Humanoid asking for an int. (unittest.TestCase)
HumanoidAskTest: Tests of basic Humanoid question asking. (unittest.TestCase)
NamelessTest: Tests of the Nameless class. (unittest.TestCase)
PlayerAskTest: Tests of the Player ask methods. (unittest.TestCase)
PythonPrintTest: Test the printing methods of the Player class. (TestCase)
PlayerTextTest: Test the text representation of player objects. (TestCase)
"""

import random
import sys
import unittest

from t_games import player
from t_games import cards
from t_games.t_tests import unitility


class BotTest(unittest.TestCase):
    """Tests of the Bot class. (unittest.TestCase)"""

    def setUp(self):
        self.bot = player.Bot()
        self.stdout_hold = sys.stdout
        sys.stdout = unitility.ProtoStdOut()

    def tearDown(self):
        sys.stdout = self.stdout_hold

    def testErrorComplex(self):
        """Test a complex case for Bot.error."""
        with self.assertRaises(player.BotError) as err:
            self.bot.error('Spam', 'spam', 'and eggs', sep = ', ', end = '!')
        self.assertEqual('Spam, spam, and eggs!', err.exception.args[0])

    def testErrorSimple(self):
        """Test a simple case for Bot.error."""
        with self.assertRaises(player.BotError) as err:
            self.bot.error('Whoops.')
        self.assertEqual('Whoops.', err.exception.args[0])

    def testTellComplex(self):
        """Test complex output for Bot.tell"""
        self.bot.tell('Spam', 'spam', 'and eggs', sep = ', ', end = '!')
        self.assertEqual(['Spam, spam, and eggs', '!'], sys.stdout.output)

    def testTellReplace(self):
        """Test output with replacements for Bot.tell"""
        self.bot.tell('You have won the game. Your quest is complete.')
        check = "{0} has won the game. {0}'s quest is complete.".format(self.bot.name)
        self.assertEqual(check, sys.stdout.output[0])

    def testTellSimple(self):
        """Test a simple case for Bot.tell."""
        self.bot.tell('Craig moved west.')
        self.assertEqual('Craig moved west.', sys.stdout.output[0])


class HumanoidAskCardTest(unittest.TestCase):
    """Tests of Humanoid asking for a card. (unittest.TestCase)"""

    def setUp(self):
        self.human = player.Humanoid('Gandalf')
        self.deck = cards.Deck()
        self.human.game = unitility.ProtoObject(force_end = False, deck = self.deck)
        self.stdin_hold = sys.stdin
        self.stdout_hold = sys.stdout
        sys.stdin = unitility.ProtoStdIn()
        sys.stdout = unitility.ProtoStdOut()

    def tearDown(self):
        sys.stdin = self.stdin_hold
        sys.stdout = self.stdout_hold

    def testAskCardCommand(self):
        """Test a request for a card with a command answer."""
        sys.stdin.lines = ['double-down']
        self.assertEqual('double-down', self.human.ask_card('Pick a card: '))

    def testAskCardCommandNotAnswer(self):
        """Test the answer for a card with an invalid command answer."""
        sys.stdin.lines = ['double-down', 'as']
        self.assertEqual(cards.Card('A', 'S'), self.human.ask_card('Pick a card: ', cmd = False))

    def testAskCardCommandNotError(self):
        """Test the error for a card with an invalid command answer."""
        sys.stdin.lines = ['double-down', 'AS']
        self.human.ask_card('Pick a card: ', cmd = False)
        self.assertEqual('Please enter a valid card.', sys.stdout.output[1])

    def testAskCardDefault(self):
        """Test getting the default answer when asking for a card."""
        sys.stdin.lines = [' ']
        check = cards.Card('2', 'C')
        self.assertEqual(check, self.human.ask_card('Pick a card: ', default = check, cmd = False))

    def testAskCardFeatureDeck(self):
        """Test getting features sets from the game deck when asking for a card."""
        self.human.game.deck = cards.Deck(rank_set = cards.STANDARD_WRAP_RANKS)
        sys.stdin.lines = ['8c']
        card = self.human.ask_card('Pick a card: ', cmd = False)
        self.assertTrue(card.rank_set.wrap)

    def testAskCardFeatureHand(self):
        """Test getting features sets from the valid hand when asking for a card."""
        deck = cards.Deck(rank_set = cards.STANDARD_WRAP_RANKS)
        sys.stdin.lines = ['8h']
        valid = cards.Hand(cards.parse_text('5C 7D 8H TS'), deck = deck)
        card = self.human.ask_card('Pick a card: ', valid = valid, cmd = False)
        self.assertTrue(card.rank_set.wrap)

    def testAskCardMultiple(self):
        """Test the error for getting multiple cards when asking for one card."""
        sys.stdin.lines = ['3H 6D 5d', '7s']
        card = self.human.ask_card('Pick a card: ', cmd = False)
        self.assertEqual('One card only please.', sys.stdout.output[1])

    def testAskCardPlain(self):
        """Test a simple request for a card."""
        sys.stdin.lines = ['3d']
        self.assertEqual(cards.Card('3', 'D'), self.human.ask_card('Pick a card: '))

    def testAskCardSkip(self):
        """Test skipping ask_card at the end of the game."""
        self.human.game.force_end = True
        self.assertEqual(cards.Card('X', 'S'), self.human.ask_card('Pick a card: '))

    def testAskCardValidAnswer(self):
        """Test the answer for a card with defined valid answers."""
        sys.stdin.lines = ['5S', 'tS']
        valid = cards.Hand(cards.parse_text('5C 7D 8H TS'))
        self.assertEqual(cards.Card('T', 'S'), self.human.ask_card('Pick a card: ', valid = valid))

    def testAskCardValidError(self):
        """Test the error for a card with defined valid answers."""
        sys.stdin.lines = ['5S', 'tS']
        valid = cards.Hand(cards.parse_text('5C 7D 8H TS'))
        self.human.ask_card('Pick a card: ', valid = valid)
        self.assertEqual('Please enter one of 5C, 7D, 8H, or TS.', sys.stdout.output[1])


class HumanoidAskIntListTest(unittest.TestCase):
    """Tests of Humaoid asking for integers. (unittest.TestCase)"""

    def setUp(self):
        self.human = player.Humanoid('Gandalf')
        self.human.game = unitility.ProtoObject(force_end = False)
        self.stdin_hold = sys.stdin
        self.stdout_hold = sys.stdout
        sys.stdin = unitility.ProtoStdIn()
        sys.stdout = unitility.ProtoStdOut()

    def tearDown(self):
        sys.stdin = self.stdin_hold
        sys.stdout = self.stdout_hold

    def testAskListCommand(self):
        """Test a request for an integer with a command answer."""
        sys.stdin.lines = ['not-pass']
        self.assertEqual('not-pass', self.human.ask_int_list('Pick some numbers: '))

    def testAskListCommandNotAnswer(self):
        """Test the answer for an integer with an invalid command answer."""
        sys.stdin.lines = ['not-pass', '108 81']
        self.assertEqual([108, 81], self.human.ask_int_list('Pick some numbers: ', cmd = False))

    def testAskListCommandNotError(self):
        """Test the error for an integer with an invalid command answer."""
        sys.stdin.lines = ['not-pass', '108 801']
        self.human.ask_int_list('Pick some numbers: ', cmd = False)
        self.assertEqual('Please enter the requested integers.', sys.stdout.output[1])

    def testAskListDoubleDouble(self):
        """Test the error for an integer with upper and lower bounds and both errors."""
        sys.stdin.lines = ['810 500', '180 666', '801 404']
        self.assertEqual([801, 404], self.human.ask_int_list('Pick some numbers: ', low = 321, high = 808))

    def testAskListDoubleHigh(self):
        """Test the error for an integer with upper and lower bounds and a high error."""
        sys.stdin.lines = ['810 124', '180 404']
        self.human.ask_int_list('Pick some numbers: ', low = 123, high = 666)
        check = '810 is too high. The highest valid response is 666.'
        self.assertEqual(check, sys.stdout.output[1])

    def testAskListDoubleLow(self):
        """Test the error for an integer with upper and lower bounds and a low error."""
        sys.stdin.lines = ['180 108', '801 810']
        self.human.ask_int_list('Pick some numbers: ', low = 230, high = 999)
        self.assertEqual('108 is too low. The lowest valid response is 230.', sys.stdout.output[1])

    def testAskListHighAnswer(self):
        """Test the answer for an integer with an upper bound."""
        sys.stdin.lines = ['108 801', '18 81']
        self.assertEqual([18, 81], self.human.ask_int_list('Pick some numbers: ', high = 100))

    def testAskListHighError(self):
        """Test the error for an integer with an upper bound."""
        sys.stdin.lines = ['108 801', '18 81']
        self.human.ask_int_list('Pick some numbers: ', high = 100)
        check = '801 is too high. The highest valid response is 100.'
        self.assertEqual(check, sys.stdout.output[1])

    def testAskListLenAnswer(self):
        """Test the answer for integer request with valid lengths."""
        sys.stdin.lines = ['108', '108 801 18 81', '18 81 108']
        self.assertEqual([18, 81, 108], self.human.ask_int_list('Pick some numbers: ', valid_lens = [2, 3]))

    def testAskListLenErrorInvalid(self):
        """Test the first part of the error for an invalid length."""
        sys.stdin.lines = ['108', '108 801 18 81', '18 81 108']
        self.human.ask_int_list('Pick some numbers: ', valid_lens = [2, 3])
        self.assertEqual('That is an invalid number of integers.', sys.stdout.output[1])

    def testAskListLenErrorPlease1(self):
        """Test the first part of the error for an invalid length."""
        sys.stdin.lines = ['108 801 18 81', '108']
        self.human.ask_int_list('Pick some numbers: ', valid_lens = [1])
        self.assertEqual('Please enter one integer.', sys.stdout.output[3])

    def testAskListLenErrorPlease2(self):
        """Test the first part of the error for an invalid length."""
        sys.stdin.lines = ['108 801 18 81', '108 801']
        self.human.ask_int_list('Pick some numbers: ', valid_lens = [2])
        self.assertEqual('Please enter two integers.', sys.stdout.output[3])

    def testAskListLenErrorPlease123(self):
        """Test the first part of the error for an invalid length."""
        sys.stdin.lines = ['108 801 18 81', '108 801']
        self.human.ask_int_list('Pick some numbers: ', valid_lens = [1, 2, 3])
        self.assertEqual('Please enter 1, 2, or 3 integers.', sys.stdout.output[3])

    def testAskListLowAnswer(self):
        """Test the answer for an integer with a lower bound."""
        sys.stdin.lines = ['81 18', '801 810']
        self.assertEqual([801, 810], self.human.ask_int_list('Pick some numbers: ', low = 500))

    def testAskListLowError(self):
        """Test the error for an integer with a lower bound."""
        sys.stdin.lines = ['81 18', '801 810']
        self.human.ask_int_list('Pick some numbers: ', low = 500)
        self.assertEqual('18 is too low. The lowest valid response is 500.', sys.stdout.output[1])

    def testAskListPlain(self):
        """Test a simple request for an integer."""
        sys.stdin.lines = ['18 108']
        self.assertEqual([18, 108], self.human.ask_int_list('Pick some numbers: '))

    def testAskListSkip(self):
        """Test skipping ask_int_list at the end of the game."""
        self.human.game.force_end = True
        self.assertEqual([0], self.human.ask_int_list('Pick some numbers: '))

    def testAskListValidAnswer(self):
        """Test the answer for an integer with defined valid answers."""
        sys.stdin.lines = ['66 108', '180 81']
        valid = [18, 81, 108, 180, 801, 810]
        self.assertEqual([180, 81], self.human.ask_int_list('Pick some numbers: ', valid = valid))

    def testAskListValidErrorA(self):
        """Test the first error for an integer with defined valid answers."""
        sys.stdin.lines = ['66 99', '18 81']
        self.human.ask_int_list('Pick some numbers: ', valid = [18, 81, 108, 180, 801, 810])
        check = "You have more 66's than allowed."
        self.assertEqual(check, sys.stdout.output[1])

    def testAskListValidErrorB(self):
        """Test the second error for an integer with defined valid answers."""
        sys.stdin.lines = ['66 99', '18 81']
        self.human.ask_int_list('Pick some numbers: ', valid = [18, 81, 108, 180, 801, 810])
        check = 'You must choose from: 18, 81, 108, 180, 801, and 810.'
        self.assertEqual(check, sys.stdout.output[3])

    def testAskListValidErrorC(self):
        """Test the first error for an integer with too many of one integer."""
        sys.stdin.lines = ['18 18', '18 81']
        self.human.ask_int_list('Pick some numbers: ', valid = [18, 81, 108, 180, 801, 810])
        check = "You have more 18's than allowed."
        self.assertEqual(check, sys.stdout.output[1])


class HumanoidAskIntTest(unittest.TestCase):
    """Tests of Humanoid asking for an integer. (unittest.TestCase)"""

    def setUp(self):
        self.human = player.Humanoid('Gandalf')
        self.human.game = unitility.ProtoObject(force_end = False)
        self.stdin_hold = sys.stdin
        self.stdout_hold = sys.stdout
        sys.stdin = unitility.ProtoStdIn()
        sys.stdout = unitility.ProtoStdOut()

    def tearDown(self):
        sys.stdin = self.stdin_hold
        sys.stdout = self.stdout_hold

    def testAskIntCommand(self):
        """Test a request for an integer with a command answer."""
        sys.stdin.lines = ['not-pass']
        self.assertEqual('not-pass', self.human.ask_int('Pick a number: '))

    def testAskIntCommandNotAnswer(self):
        """Test the answer for an integer with an invalid command answer."""
        sys.stdin.lines = ['not-pass', '108']
        self.assertEqual(108, self.human.ask_int('Pick a number: ', cmd = False))

    def testAskIntCommandNotError(self):
        """Test the error for an integer with an invalid command answer."""
        sys.stdin.lines = ['not-pass', '108']
        self.human.ask_int('Pick a number: ', cmd = False)
        self.assertEqual('Integers only please.', sys.stdout.output[1])

    def testAskIntDoubleDouble(self):
        """Test the error for an integer with upper and lower bounds and both errors."""
        sys.stdin.lines = ['810', '180', '801']
        self.assertEqual(801, self.human.ask_int('Pick a number: ', low = 321, high = 808))

    def testAskIntDoubleHigh(self):
        """Test the error for an integer with upper and lower bounds and a high error."""
        sys.stdin.lines = ['810', '180']
        self.human.ask_int('Pick a number: ', low = 123, high = 666)
        check = 'That number is too high. The highest valid response is 666.'
        self.assertEqual(check, sys.stdout.output[1])

    def testAskIntDoubleLow(self):
        """Test the error for an integer with upper and lower bounds and a low error."""
        sys.stdin.lines = ['180', '810']
        self.human.ask_int('Pick a number: ', low = 230, high = 999)
        self.assertEqual('That number is too low. The lowest valid response is 230.', sys.stdout.output[1])

    def testAskIntHighAnswer(self):
        """Test the answer for an integer with an upper bound."""
        sys.stdin.lines = ['108', '18']
        self.assertEqual(18, self.human.ask_int('Pick a number: ', high = 100))

    def testAskIntHighError(self):
        """Test the error for an integer with an upper bound."""
        sys.stdin.lines = ['108', '18']
        self.human.ask_int('Pick a number: ', high = 100)
        check = 'That number is too high. The highest valid response is 100.'
        self.assertEqual(check, sys.stdout.output[1])

    def testAskIntLowAnswer(self):
        """Test the answer for an integer with a lower bound."""
        sys.stdin.lines = ['81', '801']
        self.assertEqual(801, self.human.ask_int('Pick a number: ', low = 500))

    def testAskIntLowError(self):
        """Test the error for an integer with a lower bound."""
        sys.stdin.lines = ['81', '801']
        self.human.ask_int('Pick a number: ', low = 500)
        self.assertEqual('That number is too low. The lowest valid response is 500.', sys.stdout.output[1])

    def testAskIntPlain(self):
        """Test a simple request for an integer."""
        sys.stdin.lines = ['18']
        self.assertEqual(18, self.human.ask_int('Pick a number: '))

    def testAskIntSkip(self):
        """Test skipping ask_int at the end of the game."""
        self.human.game.force_end = True
        self.assertEqual(0, self.human.ask_int('Pick a number: '))

    def testAskIntValidAnswer(self):
        """Test the answer for an integer with defined valid answers."""
        sys.stdin.lines = ['66', '180']
        self.assertEqual(180, self.human.ask_int('Pick a number: ', valid = [18, 81, 108, 180, 801, 810]))

    def testAskIntValidErrorA(self):
        """Test the first error for an integer with defined valid answers."""
        sys.stdin.lines = ['66', '18']
        self.human.ask_int('Pick a number: ', valid = [18, 81, 108, 180, 801, 810])
        check = '66 is not a valid choice.'
        self.assertEqual(check, sys.stdout.output[1])

    def testAskIntValidErrorB(self):
        """Test the second error for an integer with defined valid answers."""
        sys.stdin.lines = ['66', '18']
        self.human.ask_int('Pick a number: ', valid = [18, 81, 108, 180, 801, 810])
        check = 'You must choose one of 18, 81, 108, 180, 801, or 810.'
        self.assertEqual(check, sys.stdout.output[3])


class HumanoidAskTest(unittest.TestCase):
    """Tests of basic Humanoid question asking. (unittest.TestCase)"""

    def setUp(self):
        self.human = player.Humanoid('Thorin')
        self.stdin_hold = sys.stdin
        self.stdout_hold = sys.stdout
        sys.stdin = unitility.ProtoStdIn()
        sys.stdout = unitility.ProtoStdOut()

    def tearDown(self):
        sys.stdin = self.stdin_hold
        sys.stdout = self.stdout_hold

    def testAskHoldAnswer(self):
        """Test answer when holding inputs for later questions."""
        sys.stdin.lines = ['charge; hack; slay']
        self.assertEqual('charge', self.human.ask('What is your move?'))

    def testAskHoldHeld(self):
        """Test holding inputs for later questions."""
        sys.stdin.lines = ['charge; hack; slay']
        self.human.ask('What is your move?')
        self.assertEqual(['hack', 'slay'], self.human.held_inputs)

    def testAskHeldAnswer(self):
        """Test answer when using held inputs as answers."""
        self.human.held_inputs = ['hack', 'slay']
        self.assertEqual('hack', self.human.ask('What is your move?'))

    def testAskHeldHeld(self):
        """Test using held inputs as answers."""
        self.human.held_inputs = ['hack', 'slay']
        self.human.ask('What is your move?')
        self.assertEqual(['slay'], self.human.held_inputs)

    def testAskPlain(self):
        """Test a simple question."""
        sys.stdin.lines = ['Charge!']
        self.assertEqual('Charge!', self.human.ask('What is your move?'))

    def testAskShortcut(self):
        """Test replacing text with short cuts."""
        self.human.shortcuts = {'d': 'Death'}
        sys.stdin.lines = ['d to my enemies!']
        self.assertEqual('Death to my enemies!', self.human.ask('What is your move?'))

    def testAskShortcutCase(self):
        """Test replacing text with case insensitive short cuts."""
        self.human.shortcuts = {'d': 'Death'}
        sys.stdin.lines = ['D to my enemies!']
        self.assertEqual('Death to my enemies!', self.human.ask('What is your move?'))

    def testAskShortcutNot(self):
        """Test not replacing text with short cuts."""
        self.human.shortcuts = {'D': 'Death'}
        sys.stdin.lines = ['Doom to my enemies!']
        self.assertEqual('Doom to my enemies!', self.human.ask('What is your move?'))

    def testAskStrip(self):
        """Test a stripping white space from an answer."""
        sys.stdin.lines = ['\tCharge! ']
        self.assertEqual('Charge!', self.human.ask('What is your move?'))


class NamelessTest(unittest.TestCase):
    """Tests of the Nameless class. (unittest.TestCase)"""

    def testAnyName(self):
        """Test a Nameless picking any name."""
        bot = player.Nameless()
        initial = bot.name[0].lower()
        check = player.BOT_NAMES[initial].split('/')
        self.assertIn(bot.name, check)

    def testInitial(self):
        """Test a Nameless with an initial."""
        bot = player.Nameless(initial = 'b')
        check = player.BOT_NAMES['b'].split('/')
        self.assertIn(bot.name, check)

    def testInitialUpper(self):
        """Test a Nameless with an uppercase initial."""
        bot = player.Nameless(initial = 'b')
        check = player.BOT_NAMES['b'].split('/')
        self.assertIn(bot.name, check)

    def testTaken(self):
        """Test a Nameless with taken names."""
        initial = random.choice(player.string.ascii_lowercase)
        names = player.BOT_NAMES[initial].split('/')
        force = random.choice(names)
        names.remove(force)
        bot = player.Nameless(initial = initial, taken_names = names)
        self.assertEqual(force, bot.name)


class PlayerAskTest(unittest.TestCase):
    """Tests of the Player ask methods. (unittest.TestCase)"""

    def setUp(self):
        self.player = player.Player('Nicodemus')

    def testAskRaises(self):
        """Test that Player.ask raises a BotError."""
        self.assertRaises(player.BotError, self.player.ask, 'What is your name? ')

    def testAskText(self):
        """The the error text for Player.ask."""
        with self.assertRaises(player.BotError) as err:
            self.player.ask_int('What is your name? ')
        check = "Unexpected question asked of Player: 'What is your name? '"
        self.assertEqual(check, err.exception.args[0])

    def testAskIntRaises(self):
        """Test that Player.ask_int raises a BotError."""
        self.assertRaises(player.BotError, self.player.ask, 'What is your age? ')

    def testAskIntText(self):
        """The the error text for Player.ask_int."""
        with self.assertRaises(player.BotError) as err:
            self.player.ask_int('What is your age? ')
        check = "Unexpected question asked of Player: 'What is your age? '"
        self.assertEqual(check, err.exception.args[0])

    def testAskIntListRaises(self):
        """Test that Player.ask_int_list raises a BotError."""
        self.assertRaises(player.BotError, self.player.ask_int_list, 'What is your move? ')

    def testAskIntListText(self):
        """The the error text for Player.ask_int_list."""
        with self.assertRaises(player.BotError) as err:
            self.player.ask_int_list('What is your move? ')
        check = "Unexpected question asked of Player: 'What is your move? '"
        self.assertEqual(check, err.exception.args[0])

    def testAskValidRaises(self):
        """Test that Player.ask_valid raises a BotError."""
        self.assertRaises(player.BotError, self.player.ask_valid, 'What is your name? ', [])

    def testAskValidText(self):
        """The the error text for Player.ask_valid."""
        with self.assertRaises(player.BotError) as err:
            self.player.ask_valid('What is your name? ', [])
        check = "Unexpected question asked of Player: 'What is your name? '"
        self.assertEqual(check, err.exception.args[0])


class PythonPrintTest(unittest.TestCase):
    """Test the printing methods of the Player class. (unittest.TestCase)"""

    def setUp(self):
        self.player = player.Player('Wordsworth')
        self.stdout_hold = sys.stdout
        sys.stdout = unitility.ProtoStdOut()

    def tearDown(self):
        sys.stdout = self.stdout_hold

    def testErrorKwarg(self):
        """Test Player.error with a keyword argument."""
        self.player.error('You messed up', 'dude.', sep = ', ')
        self.assertEqual('You messed up, dude.\n', ''.join(sys.stdout.output))

    def testErrorMutliple(self):
        """Test Player.error with multiple strings."""
        self.player.error('You', 'messed', 'up.')
        self.assertEqual('You messed up.\n', ''.join(sys.stdout.output))

    def testErrorSingle(self):
        """Test Player.error with a single string."""
        self.player.error('You messed up.')
        self.assertEqual('You messed up.\n', ''.join(sys.stdout.output))

    def testTellKwarg(self):
        """Test Player.error with a keyword argument."""
        self.player.tell('You win', 'dude.', sep = ', ')
        self.assertEqual('You win, dude.\n', ''.join(sys.stdout.output))

    def testTellMutliple(self):
        """Test Player.error with multiple strings."""
        self.player.tell('You', 'win.')
        self.assertEqual('You win.\n', ''.join(sys.stdout.output))

    def testTellSingle(self):
        """Test Player.error with a single string."""
        self.player.tell('You win.')
        self.assertEqual('You win.\n', ''.join(sys.stdout.output))


class PlayerTextTest(unittest.TestCase):
    """Test the text representation of various play objects. (TestCase)"""

    def setUp(self):
        self.stdin_hold = sys.stdin
        self.stdout_hold = sys.stdout
        sys.stdin = unitility.ProtoStdIn()
        sys.stdout = unitility.ProtoStdOut()

    def tearDown(self):
        sys.stdin = self.stdin_hold
        sys.stdout = self.stdout_hold

    def testBaseRepr(self):
        """Test the base player class computer readable text representation."""
        gamer = player.Player('Tyler')
        self.assertEqual('<Player Tyler>', repr(gamer))

    def testBaseStr(self):
        """Test the base player class human readable text representation."""
        gamer = player.Player('Tyler')
        self.assertEqual('Tyler', str(gamer))

    def testBotRepr(self):
        """Test the computer player class computer readable text representation."""
        gamer = player.Bot()
        gamer.name = 'Marvin'
        self.assertEqual('<Bot Marvin>', repr(gamer))

    def testBotStr(self):
        """Test the computer player class human readable text representation."""
        gamer = player.Bot()
        gamer.name = 'Marvin'
        self.assertEqual('Marvin', str(gamer))

    def testCyborgRepr(self):
        """Test the cyborg player class computer readable text representation."""
        gamer = player.Cyborg()
        gamer.name = 'OMAC'
        self.assertEqual('<Cyborg OMAC>', repr(gamer))

    def testCyborgStr(self):
        """Test the cyborg player class human readable text representation."""
        gamer = player.Cyborg()
        gamer.name = 'OMAC'
        self.assertEqual('OMAC', str(gamer))

    def testHumanRepr(self):
        """Test the human player class computer readable text representation."""
        sys.stdin.lines = ['Buckaroo', 'Testing', 'Black']
        gamer = player.Human()
        self.assertEqual('<Human Buckaroo>', repr(gamer))

    def testHumanStr(self):
        """Test the human player class human readable text representation."""
        sys.stdin.lines = ['Buckaroo', 'Testing', 'Black']
        gamer = player.Human()
        self.assertEqual('Buckaroo', str(gamer))


if __name__ == '__main__':
    unittest.main()
