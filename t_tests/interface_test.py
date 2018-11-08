"""
interface_test.py

Unit testing of t_games/interface.py

Classes:
InterfaceCommandTest: Tests of Interface command handling. (unittest.TestCase)
InterfaceDoStatsTest: Tests of the Interface.do_stats. (unittest.TestCase)
InterfaceGameTest: Tests of the Interface's game handling. (unittest.TestCase)
InterfaceTextTest: Tests of the Interface's text handling. (unittest.TestCase)
InterfaceWinLossDrawTest: Tests of figure_win_loss_draw. (unittest.TestCase)
ValveTest: Tests of the RandomValve class. (unittest.TestCase)
"""


import itertools
import unittest

import t_games.interface as interface
import t_tests.unitility as unitility


TEST_CATEGORIES= {'games': [interface.game.Flip, interface.game.Sorter],
    'sub-categories': {'Unit Games': {'games': [unitility.TestGame, interface.game.Game],
    'sub-categories': {}}}}

TEST_GAMES = [interface.game.Game, interface.game.Flip, interface.game.Sorter, unitility.TestGame]

# need games across all TEST_CATEGORIES,
TEST_RESULTS = [['Flip', 1, 0, 0, 5, 10, 2, ''], ['Flip', 0, 1, 0, 3, 8, 4, ''],
    ['Flip', 1, 0, 0, 4, 9, 0, ''], ['Sorter', 1, 0, 0, 0, 5, 128, ''], ['Sorter', 1, 0, 0, 0, 1, 3, '2'],
    ['Sorter', 0, 1, 0, -1, 7, 8, ''], ['Null', 1, 0, 0, 0, 1, 0, ''], ['Null', 0, 1, 0, 0, 2, 0, ''],
    ['Null', 0, 0, 1, 0, 18, 0, ''], ['Unit', 3, 2, 0, 5, 5, 0, ''], ['Unit', 2, 3, 0, 4, 4, 0, ''],
    ['Unit', 2, 2, 2, 8, 8, 128, '']]


class InterfaceCommandTest(unittest.TestCase):
    """Tests of the Interface's command handling. (unittest.TestCase)"""

    def setUp(self):
        self.bot = unitility.AutoBot()
        self.interface = interface.Interface(self.bot)

    def testDefaultFail(self):
        """Test default's handling of an invalid command."""
        self.interface.default('Spam')
        self.assertEqual(self.bot.errors[0], '\nThat is an invalid selection.\n')

    def testDefaultOptions(self):
        """Test default's handling of a game with options."""
        self.bot.replies = ['!', 'n']
        self.interface.default('Sorter / 2')
        self.assertIn('The current sequence is:  1, 0\n', self.bot.info)

    def testDefaultPlay(self):
        """Test default's handling of a game name."""
        self.bot.replies = ['n', '!', 'n']
        self.interface.default('Sorter')
        self.assertEqual(self.bot.info[-1], 'You are currently on a 1 game losing streak.\n')

    def testGamesParent(self):
        """Test do_games with a sub-category."""
        # Set up the bot and the interface.
        self.interface.categories = TEST_CATEGORIES
        self.interface.focus = self.interface.categories
        self.bot.replies = ['']
        # Get and check the game shown.
        self.interface.do_games('')
        check = ['Flip\n', 'Null\n', 'Sorter\n', 'Unit (1)\n']
        self.assertEqual(check, self.bot.info[1:])

    def testGamesTerminal(self):
        """Test do_games with a terminal category."""
        # Set up the bot and the interface.
        self.interface.categories = TEST_CATEGORIES
        self.interface.focus = self.interface.categories['sub-categories']['Unit Games']
        self.bot.replies = ['']
        # Get and check the game shown.
        self.interface.do_games('')
        check = ['Null\n', 'Unit (1)\n']
        self.assertEqual(check, self.bot.info[1:])

    def testHomeFocus(self):
        """Test do_home resetting the focus in the menu tree."""
        self.interface.focus = self.interface.categories['sub-categories']['Dice Games']
        self.interface.do_home('')
        self.assertEqual(self.interface.focus, self.interface.categories)

    def testHomePrevious(self):
        """Test do_home resetting the previous menu category."""
        self.interface.focus = self.interface.categories['sub-categories']['Dice Games']
        self.interface.do_home('')
        self.assertEqual([], self.interface.previous)

    def testHomeTitle(self):
        """Test do_home resetting the title history."""
        self.interface.focus = self.interface.categories['sub-categories']['Dice Games']
        self.interface.do_home('')
        self.assertEqual(['Home Menu'], self.interface.titles)

    def testPlayFail(self):
        """Test do_play's handling of an invalid game name."""
        self.interface.do_play('Spam')
        self.assertEqual("\nI don't know how to play that game.\n", self.bot.errors[0])

    def testPlayOptions(self):
        """Test do_play's handling of a game with options."""
        self.bot.replies = ['!', 'n']
        self.interface.do_play('Sorter / 2')
        self.assertIn('The current sequence is:  1, 0\n', self.bot.info)

    def testPlayPlay(self):
        """Test do_play's handling of a game name."""
        self.bot.replies = ['n', '!', 'n']
        self.interface.do_play('Sorter')
        self.assertEqual([], self.bot.replies)

    def testRandomAll(self):
        """Test do_random forcing all games."""
        # Set up the bot and the interface.
        self.bot.replies = ['n', '!', 'lose', 'n']
        self.interface.categories = TEST_CATEGORIES
        self.interface.games = {game.name: game for game in TEST_GAMES}
        self.interface.focus = self.interface.categories['sub-categories']['Unit Games']
        # Get the actual value
        self.interface.do_random('all')
        intro = self.bot.info[0]
        comma_index = intro.index(',')
        # Check for a valid value.
        self.assertIn(intro[22:comma_index], [game.name for game in TEST_GAMES])

    def testRandomParent(self):
        """Test do_random with child categories."""
        # Set up the bot and the interface.
        self.bot.replies = ['n', '!', 'lose', 'n']
        self.interface.categories = TEST_CATEGORIES
        self.interface.focus = self.interface.categories
        # Get the actual value
        self.interface.do_random('')
        intro = self.bot.info[0]
        comma_index = intro.index(',')
        # Check for a valid value.
        self.assertIn(intro[22:comma_index], [game.name for game in TEST_GAMES])

    def testRandomTerminal(self):
        """Test do_random without child categories."""
        # Set up the bot and the interface.
        self.bot.replies = ['n', '!', 'lose', 'n']
        self.interface.categories = TEST_CATEGORIES
        self.interface.focus = self.interface.categories['sub-categories']['Unit Games']
        # Get the actual value
        self.interface.do_random('')
        intro = self.bot.info[0]
        comma_index = intro.index(',')
        # Check for a valid value.
        check = [game.name for game in TEST_CATEGORIES['sub-categories']['Unit Games']['games']]
        self.assertIn(intro[22:comma_index], check)


class InterfaceDoStatsTest(unittest.TestCase):
    """Tests of the Interface's stats command. (unittest.TestCase)"""

    def setUp(self):
        self.bot = unitility.AutoBot()
        self.bot.results = TEST_RESULTS
        self.interface = interface.Interface(self.bot)
        self.interface.focus = TEST_CATEGORIES
        self.interface.show_stats = unitility.ProtoObject()

    def testAliasStatsAllGames(self):
        """Test stat groups shown for Interface.do_stats for a specific game alias."""
        self.interface.do_stats('1')
        self.assertEqual(1, len(self.interface.show_stats.arg_list))

    def testAiliasStatsTitle(self):
        """Test call arguments for Interface.do_stats for a specific game alias."""
        self.interface.do_stats('1')
        self.assertIn((TEST_RESULTS[-3:],), self.interface.show_stats.arg_list)

    def testBaseStatsAllGames(self):
        """Test stat groups shown for Interface.do_stats with no mods."""
        self.interface.do_stats('')
        self.assertEqual(5, len(self.interface.show_stats.arg_list))

    def testBaseStatsTitle(self):
        """Test call arguments for Interface.do_stats with no mods."""
        self.interface.do_stats('')
        self.assertIn((TEST_RESULTS, 'Category Statistics', ''), self.interface.show_stats.arg_list)

    def testCategoryAllStatsAllGames(self):
        """Test stat groups shown for Interface.do_stats in a category with 'all'."""
        self.interface.focus = TEST_CATEGORIES['sub-categories']['Unit Games']
        self.interface.do_stats('all')
        self.assertEqual(5, len(self.interface.show_stats.arg_list))

    def testCategoryAllStatsTitle(self):
        """Test call arguments for Interface.do_stats in a category with 'all'."""
        self.interface.focus = TEST_CATEGORIES['sub-categories']['Unit Games']
        self.interface.do_stats('all')
        self.assertIn((TEST_RESULTS, 'Overall Statistics', ''), self.interface.show_stats.arg_list)

    def testCategoryStatsAllGames(self):
        """Test stat groups shown for Interface.do_stats in a category."""
        self.interface.focus = TEST_CATEGORIES['sub-categories']['Unit Games']
        self.interface.do_stats('')
        self.assertEqual(3, len(self.interface.show_stats.arg_list))

    def testCategoryStatsTitle(self):
        """Test call arguments for Interface.do_stats in a category."""
        self.interface.focus = TEST_CATEGORIES['sub-categories']['Unit Games']
        self.interface.do_stats('')
        self.assertIn((TEST_RESULTS[-6:], 'Category Statistics', ''), self.interface.show_stats.arg_list)

    def testGameStatsAllGames(self):
        """Test stat groups shown for Interface.do_stats for a specific game."""
        self.interface.do_stats('unit')
        self.assertEqual(1, len(self.interface.show_stats.arg_list))

    def testGameStatsTitle(self):
        """Test call arguments for Interface.do_stats for a specific game."""
        self.interface.do_stats('unit')
        self.assertIn((TEST_RESULTS[-3:],), self.interface.show_stats.arg_list)

    def testUnknownStatsAllGames(self):
        """Test stat groups shown for Interface.do_stats for an unknown game."""
        self.interface.do_stats('calvin ball')
        self.assertEqual(0, len(self.interface.show_stats.arg_list))

    def testUnknownWarnimg(self):
        """Test error text for Interface.do_stats for an unknown game."""
        self.interface.do_stats('calvin ball')
        self.assertIn('You have never played that game.\n', self.bot.errors)


class InterfaceGameTest(unittest.TestCase):
    """Tests of the Interface's game handling. (unittest.TestCase)"""

    def setUp(self):
        self.bot = unitility.AutoBot()
        self.interface = interface.Interface(self.bot)

    def testCategoryParent(self):
        """Test category_games with a sub-category."""
        check = ['Bisley', 'Canfield', 'Crazy Eights', 'Cribbage', 'Forty Thieves', 'FreeCell', 'Klondike']
        check += ['Monte Carlo', 'Ninety-Nine', 'Pyramid', 'Quadrille', 'Spider', 'Strategy']
        self.interface.focus = self.interface.categories['sub-categories']['Card Games']
        self.assertEqual(check, sorted([game.name for game in self.interface.category_games()]))

    def testCategoryTerminal(self):
        """Test category_games with a terminal category."""
        check = ["Liar's Dice", 'Pig', 'Solitaire Dice', 'Yacht']
        self.interface.focus = self.interface.categories['sub-categories']['Dice Games']
        self.assertEqual(check, sorted([game.name for game in self.interface.category_games()]))


class InterfaceTextTest(unittest.TestCase):
    """Tests of the Interface's text handling. (unittest.TestCase)"""

    def setUp(self):
        self.bot = unitility.AutoBot()
        self.interface = interface.Interface(self.bot)

    def testAliasLocal(self):
        """Test that the local aliases are retained."""
        self.assertEqual('help', self.interface.aliases['?'])

    def testAliasParent(self):
        """Test that the parent aliases are copied."""
        self.assertEqual('debug', self.interface.aliases['&'])

    def testRepr(self):
        """Test the debugging text representation of the interface."""
        check = '<Interface <AutoBot {}>>'.format(self.bot.name)
        self.assertEqual(check, repr(self.interface))


class InterfaceWinLossDrawTest(unittest.TestCase):
    """Tests of Interface.figure_win_loss_draw. (unittest.TestCase)"""

    def setUp(self):
        self.bot = unitility.AutoBot()
        self.interface = interface.Interface(self.bot)

    def testGameRecord(self):
        """Test the game win/loss/draw calculation."""
        self.assertEqual([5, 6, 1], self.interface.figure_win_loss_draw(TEST_RESULTS)[0])

    def testPlayerRecord(self):
        """Test the player win/loss/draw calculation."""
        self.assertEqual([12, 10, 3], self.interface.figure_win_loss_draw(TEST_RESULTS)[1])


class ValveTest(unittest.TestCase):
    """Tests of the RandomValve class. (unittest.TestCase)"""

    def setUp(self):
        self.valve = interface.RandomValve()

    def testRepr(self):
        """Test a random valve's debugging text representation."""
        self.assertEqual('<RandomValve 0.0500/0.0500>', repr(self.valve))

    def testReprReset(self):
        """Test a random valve's debugging text representation after it blows."""
        # Run the valve until it blows.
        for check in itertools.cycle('abc'):
            if self.valve.blow(check):
                break
        # Check the repr.
        self.assertEqual('<RandomValve 0.0500/0.0500>', repr(self.valve))

    def testReprUsed(self):
        """Test a random valve's debugging text representation after some use."""
        # Run the valve a few times, but make sure it isn't blown.
        while True:
            for check in 'abc':
                blown = self.valve.blow(check)
            if not blown:
                break
        # Check the repr.
        check = '<RandomValve {:.4f}/{:.4f}>'.format(self.valve.p, self.valve.q)
        self.assertEqual(check, repr(self.valve))


if __name__ == '__main__':
    unittest.main()
