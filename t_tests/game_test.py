"""
game_test.py

Unit tests of t_games/game.py.

Classes:
GameCommandTest:
GameInitTest: Test of game initialization. (unittest.TestCase)
GameRPNTest: Test of the RPN calculator in game.Game. (unittest.TestCase)
GameTextTest: Tests of the base game class text versions. (unittest.TestCase)
"""


import unittest

import t_games.game as game
import t_games.player as player
import t_tests.unitility as unitility


class GameCommandTest(unittest.TestCase):
    """Test of game do_foo methods. (unittest.TestCase)"""

    def setUp(self):
        self.bot = unitility.AutoBot()
        self.game = game.Game(self.bot, ' ')

    def testCredits(self):
        """Test showing the credits."""
        check = 'No credits have been specified for this game.\n'
        self.game.do_credits('')
        self.assertEqual(check, self.bot.info[1])

    def testDebugFlag(self):
        """Test setting the flag after a debug command."""
        self.game.do_debug('self.name')
        self.assertEqual(2, self.game.flags)

    def testDebugResponse(self):
        """Test the response from a debug command."""
        self.game.do_debug('self.name')
        check = "'Null'\n"
        self.assertEqual(check, self.bot.info[1])

    def testDefault(self):
        """Test handling unknown commands."""
        check = "\nI do not recognize the command 'obey'.\n"
        self.game.player_index = 0
        self.game.handle_cmd('obey')
        self.assertEqual(check, self.bot.errors[0])

    def testQuitReturn(self):
        """Test quit command return value."""
        self.assertFalse(self.game.do_quit(''))

    def testQuitSet(self):
        """Test quit command setting attributes."""
        self.game.do_quit('')
        attrs = (self.game.flags, self.game.force_end, self.game.win_loss_draw)
        self.assertEqual((4, 'loss', [0, 1, 0]), attrs)

    def testQuitQuit(self):
        """Test quit quit command."""
        self.game.do_quit('quit')
        self.assertEqual(['!'], self.bot.held_inputs)

    def testQuitWithQuit(self):
        """Test quit command with quit argument."""
        self.game.do_quit('quit')
        self.assertEqual(['!'], self.bot.held_inputs)


class GameInitTest(unittest.TestCase):
    """Test of game initialization. (unittest.TestCase)"""

    def setUp(self):
        self.bot = unitility.AutoBot()
        self.bot.name = 'Bumblebee'
        self.game = game.Game(self.bot, ' ')

    def testAlias(self):
        """Test updating the aliases dictionary."""
        self.assertIn('&', self.game.aliases)

    def testGreeting(self):
        """Test displaying the greeting text."""
        check = '\nWelcome to a game of Null, Bumblebee.\n'
        self.assertEqual(check, self.bot.info[0])

    def testHelp(self):
        """Test updating help dictionairy."""
        check = '\nUse the rules command for instructions on how to play.'
        self.assertEqual(check, self.game.help_text['help'])

    def testPlayers(self):
        """Test default players."""
        self.assertEqual([self.bot], self.game.players)

    def testPlayerGame(self):
        """Test setting the player's game attribute."""
        self.assertEqual(self.game, self.bot.game)

    def testRawOptions(self):
        """Test setting raw_options."""
        self.assertEqual('', self.game.raw_options)

def rpn_tests():
    class GameRPNTest(unittest.TestCase):
        """Test of the reverse polish notation calculator in game.Game. (unittest.TestCase)"""

        def setUp(self):
            self.bot = unitility.AutoBot()
            self.game = game.Game(self.bot, ' ')

    def make_rpn_test(arguments, check, description):
        def testSomething(self):
            self.game.do_rpn(arguments)
            self.assertEqual(check, self.bot.info[-1].strip())
        testSomething.__doc__ = 'Test RPN calculation of {}.'.format(description)
        return testSomething

    tests = [('testAbsPos', '1 |', '1', 'the absolute value of a postive number'),
        ('testAbsNeg', '-2 |', '2', 'the absolute value of a negative number')]
    for arguments in tests:
        setattr(GameRPNTest, arguments[0], make_rpn_test(*arguments[1:]))
    return GameRPNTest
GameRPNTest = rpn_tests()


class GameTextTest(unittest.TestCase):
    """Tests of the base game class text representations. (unittest.TestCase)"""

    def setUp(self):
        self.game = game.Game(unitility.AutoBot(), '')

    def testRepr(self):
        """Test the game's debugging text representation."""
        self.assertEqual('<Game of Null with 1 player>', repr(self.game))

    def testReprMulti(self):
        """Test the game's debugging text representation with multiple players."""
        self.game.players.append(player.Bot())
        self.game.players.append(player.Bot())
        self.assertEqual('<Game of Null with 3 players>', repr(self.game))


if __name__ == '__main__':
    unittest.main()
