"""
game_test.py

Unit tests of t_games/game.py.

Classes:
GameCommandTest: Test of game do_foo methods. (unittest.TestCase)
GameGipfCheckTest: Test of validating a gipf move. (unittest.TestCase)
GameInitTest: Test of game initialization. (unittest.TestCase)
GamePlayTest: Tests of playing the game. (unittest.TestCase)
GameRPNTest: Test of the RPN calculator in game.Game. (unittest.TestCase)
GameTextTest: Tests of the base game class text versions. (unittest.TestCase)
GameXyzzyTest: Tests of the xyzzy command. (unittest.TestCase)
GameXyzzyHelpText: Tests of Game.help_xyzzy. (unittest.TestCase)

Functions:
rpn_tests: Make a test class for the Game.do_rpn calculations. (unittest.TestCase)
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

    def testRPNFlip(self):
        """Test flipping a coin with the rpn command."""
        self.game.do_rpn('F')
        self.assertIn(self.bot.info[-1], ('0\n', '1\n'))

    def testRPNRandomChange(self):
        """Test that consecutive random numbers from rpn are different."""
        self.game.do_rpn('R R')
        first, second = [float(x) for x in self.bot.info[-1].split()]
        self.assertNotEqual(first, second)

    def testRPNRandomRange(self):
        """Test that random numbers from rpn are in the zero to one range."""
        self.game.do_rpn('R')

    def testRPNValueError(self):
        """Test raising a value error with the rpn command."""
        self.game.do_rpn('2 5 C')
        self.assertEqual('Bad value for C operator.\n', self.bot.errors[0])

    def testRPNZeroDivisionError(self):
        """Test raising a zero division error with the rpn command."""
        self.game.do_rpn('18 0 /')
        self.assertEqual('Zero division error.\n', self.bot.errors[0])

    def testRules(self):
        """Test showing the rules."""
        check = 'No rules have been specified for this game.\n'
        self.game.do_rules('')
        self.assertEqual(check, self.bot.info[1])


class GameGipfCheckTest(unittest.TestCase):
    """Test of validating a gipf move. (unittest.TestCase)"""

    def setUp(self):
        game_list = {'dice': TestGame, 'cards': TestGame}
        interface = unitility.ProtoObject(games = game_list)
        self.bot = unitility.AutoBot()
        self.bot.replies = ['win']
        self.game = game.Game(self.bot, 'none')
        self.game.interface = interface

    def testAlias(self):
        """Test gipfing using an alias."""
        self.game.gipf_check('1', ('cards', 'dice'))
        self.assertTrue(self.game.flags & 8)

    def testDraw(self):
        """Test losing on a multi-player draw."""
        self.bot.replies = ['draw++']
        self.assertEqual(('dice', 1), self.game.gipf_check('Dice', ('cards', 'dice')))

    def testDrawSolo(self):
        """Test losing on a solitaire draw."""
        self.bot.replies = ['draw']
        self.assertEqual(('dice', 1), self.game.gipf_check('Dice', ('cards', 'dice')))

    def testFocus(self):
        """Test returning the human's focus to the original game."""
        self.game.gipf_check('Dice', ('cards', 'dice'))
        self.assertEqual(self.game, self.bot.game)

    def testGiphedFromFlag(self):
        """Test the flag for gipfing from a game."""
        self.game.gipf_check('Dice', ('cards', 'dice'))
        self.assertTrue(self.game.flags & 8)

    def testGiphedToFlag(self):
        """Test the flag for gipfing to a game."""
        self.game.gipf_check('Cards', ('cards', 'dice'))
        self.assertTrue(self.bot.results[0][6] & 16)

    def testGiphTracking(self):
        """Test that the game gipfed to is tracked."""
        self.game.gipf_check('Cards', ('cards', 'dice'))
        self.assertIn('Unit', self.game.gipfed)

    def testGiphTwice(self):
        """Test that you can't gipf to the same game twice."""
        self.game.gipf_check('Dice', ('cards', 'dice'))
        self.assertEqual(('invalid-game', 1), self.game.gipf_check('Dice', ('cards', 'dice')))

    def testInvalidGame(self):
        """Test gipfing to an invalid game."""
        self.assertEqual(('invalid-game', 1), self.game.gipf_check('Dice', ('cards',)))

    def testLoss(self):
        """Test losing the gipf challenge."""
        self.bot.replies = ['lose']
        self.assertEqual(('dice', 1), self.game.gipf_check('Dice', ('cards', 'dice')))

    def testMatchDraw(self):
        """Test drawing the gipf challenge with match play."""
        self.bot.replies = ['lose+']
        self.game.interface.flags = 256
        self.assertEqual(('dice', 3), self.game.gipf_check('Dice', ('cards', 'dice')))

    def testMatchLoss(self):
        """Test losing the gipf challenge with match play."""
        self.bot.replies = ['lose']
        self.game.interface.flags = 256
        self.assertEqual(('dice', 3), self.game.gipf_check('Dice', ('cards', 'dice')))

    def testMatchWin(self):
        """Test winning the gipf challenge with match play."""
        self.game.interface.flags = 256
        self.assertEqual(('dice', 0), self.game.gipf_check('Dice', ('cards', 'dice')))

    def testWin(self):
        """Test winning the gipf challenge."""
        self.assertEqual(('dice', 0), self.game.gipf_check('Dice', ('cards', 'dice')))


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


class GamePlayTest(unittest.TestCase):
    """Tests of playing the game. (unittest.TestCase)"""

    def setUp(self):
        self.bot = unitility.AutoBot(['win'])
        self.game = TestGame(self.bot, '')

    def testScores(self):
        """Test that the scores are set up."""
        self.game.play()
        self.assertEqual({self.bot.name: 1}, self.game.scores)

    def testSetUpBot(self):
        """Test that the bot is set up."""
        self.game.play()
        self.assertTrue(self.bot.all_set)

    def testSetUpGame(self):
        """Test that the game is set up."""
        self.game.play()
        self.assertTrue(self.game.all_set)

def rpn_tests():
    """Make a test class for the Game.do_rpn calculations. (unittest.TestCase)"""
    # Create the base class.
    class GameRPNTest(unittest.TestCase):
        """Test of the reverse polish notation calculator in game.Game. (unittest.TestCase)"""
        def setUp(self):
            self.bot = unitility.AutoBot()
            self.game = game.Game(self.bot, ' ')
    # Create a function to add test methods.
    def make_rpn_test(arguments, check, description):
        def testSomething(self):
            self.game.do_rpn(arguments)
            self.assertEqual(check, self.bot.info[-1].strip())
        testSomething.__doc__ = 'Test RPN calculation of {}.'.format(description)
        return testSomething
    # Define the tests to run.
    tests = [('testABC', '1 2 4 ab/c', '1.5', 'the abc of powers of two'),
        ('testAbsNeg', '-2 |', '2', 'the absolute value of a negative number'),
        ('testAbsPos', '1 |', '1', 'the absolute value of a postive number'),
        ('testAddMixed', '2 -2 +', '0', 'adding a negative and a postive'),
        ('testAddNeg', '-2 -2 +', '-4', 'adding two negative numbers'),
        ('testAddPos', '2 2 +', '4', 'adding two positive numbers'),
        ('textChooseLarge', '108 23 C', '181886780350687116846960', 'n choose r with large numbers'),
        ('testChooseSmall', '5 2 C', '10', 'n choose r with small numbers'),
        ('testCosPi', '3.1415926535 cos', '-1.0', 'the cos of pi'),
        ('testCosZero', '0 cos', '1.0', 'the cos of zero'),
        ('testDivideEven', '4 2 /', '2.0', 'an even division'),
        ('testDivideNegBoth', '-4 -2 /', '2.0', 'division with two negatives'),
        ('testDivideNegDown', '4 -2 /', '-2.0', 'division with a negative denominator'),
        ('testDivideNegUp', '-4 2 /', '-2.0', 'division with a negative numerator'),
        ('testDivideReaminder', '18 4 /', '4.5', 'division resulting in a float'),
        ('testDivModEven', '108 27 /%', '4 0', 'divmod with no remainder'),
        ('testDivModNegBoth', '-15 -2 /%', '7 -1', 'divmod with two negative numbers'),
        ('testDivModNegDown', '15 -2 /%', '-8 -1', 'divmod with a negative divisor'),
        ('testDivModUp', '-15 2 /%', '-8 1', 'divmod with a negative dividend'),
        ('testDivModRemain', '23 5 /%', '4 3', 'divmod with a remainder'),
        ('testExponentNegative', '2 -2 ^', '0.25', 'a negative exponent'),
        ('testExponentOfNegative', '-2 4 ^', '-16', 'failures of mathematical notation'),
        ('testExpoenentRoot', '81 0.5 ^', '9.0', 'a fractional exponent'),
        ('testExponentSimple', '2 10 ^', '1024', 'a basic exponent'),
        ('testFactorialLarge', '23 !', '25852016738884976640000', 'a large factorial'),
        ('testFactorialSmall', '5 !', '120', 'a small factorial'),
        ('testFactorialZero', '0 !', '1', 'the factorial of zero'),
        ('testFloorDivideEven', '4 2 //', '2', 'an even floor division'),
        ('testFloorDivideFloorNeg', '18 -4 //', '-5', 'floor division that floors a negative'),
        ('testFloorDivideFloorPos', '18 4 //', '4', 'floor division that floors'),
        ('testFloorDivideNegBoth', '-4 -2 //', '2', 'floor division with two negatives'),
        ('testFloorDivideNegDown', '4 -2 //', '-2', 'floor division with a negative denominator'),
        ('testFloorDivideNegUp', '-4 2 //', '-2', 'floor division with a negative numerator'),
        ('testLnE', '2.718281828459045 ln', '1.0', 'the natural logarith of e'),
        ('testLnOne', '1 ln', '0.0', 'the natural logarith of 1'),
        ('testLogK', '1000 log', '3.0', 'the common logarithm of 1000'),
        ('testLogOne', '1 log', '0.0', 'the common logarithm of 1'),
        ('testModEven', '108 27 %', '0', 'divmod with no remainder'),
        ('testModNegBoth', '-15 -2 %', '-1', 'divmod with two negative numbers'),
        ('testModNegDown', '15 -2 %', '-1', 'divmod with a negative divisor'),
        ('testModUp', '-15 2 %', '1', 'divmod with a negative dividend'),
        ('testModRemain', '23 5 %', '3', 'divmod with a remainder'),
        ('testMultiplyFloat', '2.3 8.1 *', '18.63', 'mulitplying floating point numbers'),
        ('testMulitplyInt', '108 801 *', '86508', 'multiplying integers'),
        ('testMultiplyNegOne', '2 -3 *', '-6', 'mulitplying a negative and a positive'),
        ('testMultiplyNegTwo', '-8 -1 *', '8', 'multplying two negatives'),
        ('testNegationFloat', '8.01 +-', '-8.01', 'negating a floating point number'),
        ('testNegationNegative', '-8 +-', '8', 'negating a negative'),
        ('testNegationPositive', '8 +-', '-8', 'negating a positive'),
        ('textPermuteLarge', '32 9 P', '10178348544000', 'n permute r with large numbers'),
        ('testPermuteSmall', '5 2 P', '20', 'n permute r with small numbers'),
        ('testReciprocalFloat', '0.25 1/', '4.0', 'the reciprocal of a floating point number'),
        ('testReciprocalInt', '5 1/', '0.2', 'the reciprocal of an integer'),
        ('testReciprocalNegative', '-8 1/', '-0.125', 'the reciprocal of a negative'),
        ('testSinHalfPi', '3.141592653589793 2 / sin', '1.0', 'the sine of pi over two'),
        ('testSinZero', '0 sin', '0.0', 'the sine of zero'),
        ('testSubtractMixed', '2 -2 -', '4', 'subtracting a negative and a postive'),
        ('testSubtractNeg', '-2 -2 -', '0', 'subtracting two negative numbers'),
        ('testSubtractPos', '2 2 -', '0', 'subtracting two positive numbers'),
        ('testSquareRootFloat', '6.25 V', '2.5', 'the sqaure root of a floating point number'),
        ('testSquareRootInt', '81 V', '9.0', 'the square root of an integer'),
        ('testTanZero', '0 tan', '0.0', 'the tangent of zero')]
    # Add the tests to the class.
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


class GameXyzzyTest(unittest.TestCase):
    """Tests of the xyzzy command. (unittest.TestCase)s"""

    def setUp(self):
        game_list = {'unit': TestGame}
        valve = unitility.ProtoObject(blow = lambda s: self.trigger)
        interface = unitility.ProtoObject(games = game_list, valve = valve)
        self.bot = unitility.AutoBot()
        self.game = game.Game(self.bot, 'none')
        self.game.interface = interface

    def testBlowFlagEnter(self):
        """Test the xyzzy used flag after a successful blow."""
        self.trigger = True
        self.bot.replies = ['lose']
        self.game.do_xyzzy('')
        self.assertTrue(self.bot.results[0][6] & 64)

    def testBlowFlagExit(self):
        """Test the results flag after a successful blow."""
        self.trigger = True
        self.bot.replies = ['lose']
        self.game.do_xyzzy('')
        self.assertTrue(self.game.flags & 32)

    def testBlowLoseFlag(self):
        """Test the return value for a failed incantation."""
        self.trigger = True
        self.bot.replies = ['lose']
        self.assertTrue(self.game.do_xyzzy(''))

    def testBlowLoseMatch(self):
        """Test identifying a match loss."""
        self.trigger = True
        self.bot.replies = ['lose']
        self.game.interface.flags = 256
        self.game.do_xyzzy('')
        self.assertFalse(self.game.flags & 128)

    def testBlowLoseReturn(self):
        """Test the return value for a failed incantation."""
        self.trigger = True
        self.bot.replies = ['lose']
        self.assertTrue(self.game.do_xyzzy(''))

    def testBlowWinFlag(self):
        """Test the starting flag after a successful incantation."""
        self.trigger = True
        self.bot.replies = ['win']
        self.game.do_xyzzy('')
        self.assertTrue(self.game.flags & 128)

    def testBlowWinForce(self):
        """Test forcing the win after a successful incantation."""
        self.trigger = True
        self.bot.replies = ['win']
        self.game.do_xyzzy('')
        self.assertEqual(self.game.force_end, 'win')

    def testBlowWinMatch(self):
        """Test identifying a match win."""
        self.trigger = True
        self.bot.replies = ['win']
        self.game.interface.flags = 256
        self.game.do_xyzzy('')
        self.assertIn('\nThe incantation is complete. You win at Null.\n\n', self.bot.info)

    def testBlowWinPrint(self):
        """Test the printed output after a successful incantation."""
        self.trigger = True
        self.bot.replies = ['win']
        self.game.do_xyzzy('')
        self.assertIn('\nThe incantation is complete. You win at Null.\n\n', self.bot.info)

    def testBlowWinReturn(self):
        """Test the return value for a succesful incantation."""
        self.trigger = True
        self.bot.replies = ['win']
        self.assertFalse(self.game.do_xyzzy(''))

    def testBlowWinWLD(self):
        """Test the win/loss/draw record after a successful incantation."""
        self.trigger = True
        self.bot.replies = ['win']
        self.game.do_xyzzy('')
        self.assertEqual(self.game.win_loss_draw, [1, 0, 0])

    def testBlowPrint(self):
        """Test the printed response for a successful blow."""
        self.trigger = True
        self.bot.replies = ['lose']
        self.game.do_xyzzy('')
        self.assertIn('\nPoof!\n', self.bot.info)

    def testFailurePrint(self):
        """Test a xyzzy failure's printed text."""
        self.trigger = False
        self.game.do_xyzzy('')
        self.assertEqual('Nothing happens.\n', self.bot.info[-1])

    def testFailureReturn(self):
        """Test a xyzzy failure's return value."""
        self.trigger = False
        self.assertTrue(self.game.do_xyzzy(''))


class GameXyzzyHelpTest(unittest.TestCase):
    """Tests of Game.help_xyzzy. (unittest.TestCase)"""

    def setUp(self):
        self.random_hold = game.random
        self.mock_random = unitility.MockRandom()
        game.random = self.mock_random
        self.bot = unitility.AutoBot([''])
        self.game = game.Game(self.bot, '')

    def tearDown(self):
        game.random = self.random_hold

    def testNothing(self):
        """Test nothing happening with help xyzzy."""
        self.mock_random.push(0.81)
        self.game.help_xyzzy()
        self.assertEqual('\nNothing happens.\n', self.bot.info[-1])

    def testNotNothing(self):
        """Test not nothing happening with 1 in 5 help xyzzy."""
        self.bot.info = []
        self.mock_random.push([0, 0.18])
        self.game.help_xyzzy()
        self.assertNotEqual('\nNothing happens.\n', self.bot.info[0])

    def testSomething(self):
        """Test something happening with 1 in 5 help xyzzy."""
        self.bot.info = []
        self.mock_random.push([0, 0.18])
        self.game.help_xyzzy()
        self.assertEqual(1, len(self.bot.info))


class TestGame(game.Game):
    """
    A Game sub-class for testing purposes. (game.Game)

    Attributes:
    all_set: A flag for the set_up method being called. (bool)
    all_done: A flag for the clean_up method being called. (bool)
    move: The move the player made.

    Overridden Methods
    game_over
    player_action
    """

    aka = '1'
    name = 'Unit'
    rules = '\nIf you enter win, you win; if you enter lose, you lose.\n'

    def __init__(self, human, raw_options, interface = None):
        """
        Set up the game. (None)

        human: The primary player of the game. (player.Player)
        raw_options: The user's option choices as provided by the interface. (str)
        interface: The interface that started the game playing. (interface.Interface)
        """
        super(TestGame, self).__init__(human, raw_options, interface)
        if hasattr(self.interface, 'flags'):
            self.flags = self.interface.flags
        self.all_set, self.all_done = False, False

    def game_over(self):
        """Check for the end of the game. (bool)"""
        # Check for match play.
        if self.flags & 256:
            self.win_loss_draw = [2, 2, 1]
        # Resolve game ending moves.
        if self.move.startswith('win'):
            self.win_loss_draw[0] += 1
        elif self.move.startswith('lose'):
            self.win_loss_draw[1] += 1
        elif self.move.startswith('draw'):
            self.win_loss_draw[1] += 1
        else:
            # Keep playing.
            return False
        # Add additional wins, losses, and draws.
        for result_index, result_char in enumerate('+-='):
            self.win_loss_draw[result_index] += self.move.count(result_char)
        # Set the score when the game ends.
        self.scores[self.human.name] = self.turns
        return True

    def clean_up(self):
        """Do any necessary post-game processing. (None)"""
        self.all_done = True

    def player_action(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        self.move = player.ask('What is your move, {}? '.format(player.name)).lower()
        if self.move == 'continue':
            return True
        elif self.move.startswith('quit'):
            if '+' in self.move:
                self.force_end = 'win'
            else:
                self.force_end = 'loss'

    def set_up(self):
        """Do any necessary pre-game processing. (None)"""
        self.all_set = True


if __name__ == '__main__':
    unittest.main()
