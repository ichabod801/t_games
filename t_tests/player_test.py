"""
player_test.py

Unittesting of t_games/player.py

Classes:
PlayerAskTest: Tests of the Player ask methods. (unittest.TestCase)
PlayerTextTest: Test the text representation of various play objects. (TestCase)
"""


import unittest
import sys

import t_games.player as player
import t_tests.unitility as unitility


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
