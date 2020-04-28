"""
interface_test.py

Unit testing of t_games/interface.py

Classes:
InterfaceCommandTest: Tests of Interface command handling. (unittest.TestCase)
InterfaceDoStatsTest: Tests of the Interface.do_stats. (unittest.TestCase)
InterfaceGameTest: Tests of the Interface's game handling. (unittest.TestCase)
InterfaceMenuTest: Tests of the Interface's menu system. (unittest.TestCase)
InterfacePlayGameTest: Tests playing a game through the interface. (TestCase)
InterfaceShwoMenuTest: Tests of setting up the interface menu. (TestCase)
InterfaceTextTest: Tests of the Interface's text handling. (unittest.TestCase)
StatisticsBinResultsTest: Tests of Statistics.bin_results. (TestCase)
StatisticsBinResultsMatchTest: Tests of bin_results with match play. (TestCase)
StatisticsDunderTest: Tests of other dunder methods for Statistics. (TestCase)
StatisticsFilterResultsTest: Tests of Statistic's results filtering. (TestCase)
StatisticsStringTest: Tests of the output for a Statistics object. (TestCase)
ValveTest: Tests of the RandomValve class. (unittest.TestCase)
"""


import itertools
import unittest

from t_games import interface
from t_games.t_tests import unitility


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
        self.assertEqual(self.bot.info[-1].split('\n')[-2], 'You are currently on a 1 game losing streak.')

    def testGamesParent(self):
        """Test do_games with a sub-category."""
        # Set up the bot and the interface.
        self.interface.categories = TEST_CATEGORIES.copy()
        self.interface.focus = self.interface.categories
        self.bot.replies = ['']
        # Get and check the game shown.
        self.interface.do_games('')
        check = ['Flip\n', 'Null\n', 'Sorter\n', 'Unit (1)\n']
        self.assertEqual(check, self.bot.info[1:])

    def testGamesTerminal(self):
        """Test do_games with a terminal category."""
        # Set up the bot and the interface.
        self.interface.categories = TEST_CATEGORIES.copy()
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
        self.bot.replies = ['n', '!', 'lose', '!', 'lose', '!', 'lose', 'n']
        self.interface.categories = TEST_CATEGORIES.copy()
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
        self.bot.replies = ['n', '!', 'lose', '!', 'lose', '!', 'lose', 'n']
        self.interface.categories = TEST_CATEGORIES.copy()
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
        self.bot.replies = ['n', '!', 'lose', '!', 'lose', '!', 'lose', 'n']
        self.interface.categories = TEST_CATEGORIES.copy()
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
        self.bot.results = [result[:] for result in TEST_RESULTS]
        self.interface = interface.Interface(self.bot)
        self.interface.focus = TEST_CATEGORIES.copy()

    def testAliasStatsAllGames(self):
        """Test stat groups shown for Interface.do_stats for a specific game alias."""
        self.interface.do_stats('1')
        self.assertEqual(1, len(self.bot.info))

    def testAliasStatsTitle(self):
        """Test call arguments for Interface.do_stats for a specific game alias."""
        self.interface.do_stats('1')
        self.assertIn('\nUnit Statistics\n', self.bot.info[0])

    def testBaseStatsAllGames(self):
        """Test stat groups shown for Interface.do_stats with no mods."""
        self.interface.do_stats('')
        self.assertEqual(5, len(self.bot.info))

    def testBaseStatsTitle(self):
        """Test call arguments for Interface.do_stats with no mods."""
        self.interface.do_stats('')
        self.assertIn('\nCategory Statistics\n', self.bot.info[0])

    def testCategoryAllStatsAllGames(self):
        """Test stat groups shown for Interface.do_stats in a category with 'all'."""
        self.interface.focus = TEST_CATEGORIES['sub-categories']['Unit Games']
        self.interface.do_stats('all')
        self.assertEqual(5, len(self.bot.info))

    def testCategoryAllStatsTitle(self):
        """Test call arguments for Interface.do_stats in a category with 'all'."""
        self.interface.focus = TEST_CATEGORIES['sub-categories']['Unit Games']
        self.interface.do_stats('all')
        self.assertIn('Overall Statistics\n', self.bot.info[0])

    def testCategoryStatsAllGames(self):
        """Test stat groups shown for Interface.do_stats in a category."""
        self.interface.focus = TEST_CATEGORIES['sub-categories']['Unit Games']
        self.interface.do_stats('')
        self.assertEqual(3, len(self.bot.info))

    def testCategoryStatsTitle(self):
        """Test call arguments for Interface.do_stats in a category."""
        self.interface.focus = TEST_CATEGORIES['sub-categories']['Unit Games']
        self.interface.do_stats('')
        self.assertIn('Category Statistics\n', self.bot.info[0])

    def testGameStatsAllGames(self):
        """Test stat groups shown for Interface.do_stats for a specific game."""
        self.interface.do_stats('unit')
        self.assertEqual(1, len(self.bot.info))

    def testGameStatsTitle(self):
        """Test call arguments for Interface.do_stats for a specific game."""
        self.interface.do_stats('unit')
        self.assertIn('Unit Statistics\n', self.bot.info[0])

    def testUnknownWarnimg(self):
        """Test error text for Interface.do_stats for an unknown game."""
        self.interface.do_stats('calvin ball')
        self.assertIn("I don't know that game.\n", self.bot.errors)


class InterfaceGameTest(unittest.TestCase):
    """Tests of the Interface's game handling. (unittest.TestCase)"""

    def setUp(self):
        self.bot = unitility.AutoBot()
        self.interface = interface.Interface(self.bot)

    def testCategoryParent(self):
        """Test category_games with a sub-category."""
        check = ['Bisley', 'Calvin Cards', 'Canfield', 'Crazy Eights', 'Cribbage', 'Forty Thieves']
        check += ['FreeCell', 'Gargantua', 'Gin Rummy', 'Hearts', 'Klondike', 'Monte Carlo', 'Ninety-Nine']
        check += ['Pyramid', 'Quadrille', 'Spider', 'Strategy', 'Thoughtful Solitaire', 'Yukon']
        self.interface.focus = self.interface.categories['sub-categories']['Card Games']
        self.assertEqual(check, sorted([game.name for game in self.interface.category_games()]))

    def testCategoryTerminal(self):
        """Test category_games with a terminal category."""
        check = ["Liar's Dice", 'Mate', 'Pig', 'Solitaire Dice', 'Ten Thousand', 'Yacht']
        self.interface.focus = self.interface.categories['sub-categories']['Dice Games']
        self.assertEqual(check, sorted([game.name for game in self.interface.category_games()]))


class InterfaceMenuTest(unittest.TestCase):
    """Tests of the Interface's menu system. (unittest.TestCase)"""

    def setUp(self):
        self.bot = unitility.AutoBot()
        self.interface = interface.Interface(self.bot)

    def testHandleCommand(self):
        """Test handling a command."""
        self.interface.handle_cmd = unitility.ProtoObject()
        self.bot.replies = ['Fnord', '!']
        self.interface.menu()
        self.assertEqual(('Fnord',), self.interface.handle_cmd.args)

    def testIntroText(self):
        """Test display of the introductory text."""
        self.bot.replies = ['!']
        self.interface.menu()
        self.assertIn("\nWelcome to Ichabod's Text Game Extravaganza!\n", self.bot.info)
        self.assertIn("Copyright (C) 2018-2020 by Craig O'Brien and the t_games contributors.\n",
            self.bot.info)
        self.assertIn("For more details type 'help' or 'help license'.\n", self.bot.info)

    def testPlay(self):
        """Test playing a game."""
        self.interface.play_game = unitility.ProtoObject()
        self.bot.replies = ['D', 'C', '!']
        self.interface.menu()
        self.assertEqual((self.interface.games['pig'], ''), self.interface.play_game.args)

    def testPlayOptions(self):
        """Test playing a game with options."""
        self.interface.play_game = unitility.ProtoObject()
        self.bot.replies = ['D', 'C / satan', '!']
        self.interface.menu()
        self.assertEqual((self.interface.games['pig'], 'satan'), self.interface.play_game.args)

    def testPrevious(self):
        """Test moving back to the main menu."""
        self.bot.replies = ['C', '<', '!']
        self.interface.menu()
        self.assertEqual(self.interface.categories, self.interface.focus)

    def testPreviousComplicatedFocus(self):
        """Test focus complicated movement through the menu."""
        self.bot.replies = ['D', '<', 'C', 'A', '<', '!']
        self.interface.menu()
        self.assertEqual(self.interface.categories['sub-categories']['Card Games'], self.interface.focus)

    def testPreviousComplicatedPrevious(self):
        """Test move history complicated movement through the menu."""
        self.bot.replies = ['D', '<', 'C', 'A', '<', '!']
        self.interface.menu()
        self.assertEqual([self.interface.categories], self.interface.previous)

    def testPreviousOverkill(self):
        """Test moving back above the main menu."""
        self.bot.replies = ['C', '<', '<', '!']
        self.interface.menu()
        self.assertEqual(self.interface.categories, self.interface.focus)

    def testPreviousTwice(self):
        """Test moving back to the main menu after two moves."""
        self.bot.replies = ['C', 'A', '<', '<', '!']
        self.interface.menu()
        self.assertEqual(self.interface.categories, self.interface.focus)

    def testSubCategory(self):
        """Test moving to a sub-category."""
        self.bot.replies = ['D', '!']
        self.interface.menu()
        self.assertEqual(self.interface.categories['sub-categories']['Dice Games'], self.interface.focus)


class InterfacePlayGameTest(unittest.TestCase):
    """Tests playing a game through the interface. (unittest.TestCase)"""

    def setUp(self):
        self.bot = unitility.AutoBot()
        self.interface = interface.Interface(self.bot)
        self.interface.do_stats = unitility.ProtoObject()

    def testAgain(self):
        """Test playing a game and then playing again."""
        self.bot.replies = ['win', 'y', 'loss', 'n', '!']
        self.interface.play_game(unitility.TestGame, '')
        self.assertEqual(2, len(self.bot.results))

    def testCheat(self):
        """Test playing a game with cheating."""
        self.bot.replies = ["& setattr(self, 'flags', 2)", 'win', 'n', '!']
        self.interface.play_game(unitility.TestGame, '')
        check = '\nStatistics were calculated with the following options: cheat.\n'
        self.assertIn(check, self.bot.info)

    def testGipf(self):
        """Test playing a game with gipfing."""
        self.bot.replies = ["& setattr(self, 'flags', 8)", 'win', 'n', '!']
        self.interface.play_game(unitility.TestGame, '')
        check = '\nStatistics were calculated with the following options: gipf.\n'
        self.assertIn(check, self.bot.info)

    def testMultiFilter(self):
        """Test playing a game with multiple statistics blocks."""
        self.bot.replies = ["& setattr(self, 'flags', 130)", 'win', 'n', '!']
        self.interface.play_game(unitility.TestGame, 'cheat xyzzy')
        check = '\nStatistics were calculated with the following options: cheat xyzzy.\n'
        self.assertIn(check, self.bot.info)

    def testNoFilter(self):
        """Test playing a game without statistics blocks."""
        self.bot.replies = ['win', 'n', '!']
        self.interface.play_game(unitility.TestGame, '')
        self.assertEqual(('Unit / ',), self.interface.do_stats.args)

    def testNotAgain(self):
        """Test playing a game without playing again."""
        self.bot.replies = ['win', 'n', '!']
        self.interface.play_game(unitility.TestGame, '')
        self.assertEqual(1, len(self.bot.results))

    def testOptionError(self):
        """Test catching an error in the options."""
        self.bot.replies = ['win', 'n', '!']
        self.assertFalse(self.interface.play_game(unitility.TestGame, 'error'))

    def testXyzzy(self):
        """Test playing a game with xyzzy."""
        self.bot.replies = ["& setattr(self, 'flags', 128)", 'win', 'n', '!']
        self.interface.play_game(unitility.TestGame, '')
        check = '\nStatistics were calculated with the following options: xyzzy.\n'
        self.assertIn(check, self.bot.info)


class InterfaceShowMenuTest(unittest.TestCase):
    """Tests of setting up the interface menu. (unittest.TestCase)"""

    def setUp(self):
        self.bot = unitility.AutoBot()
        self.interface = interface.Interface(self.bot)
        self.interface.categories = TEST_CATEGORIES.copy()
        self.interface.games = TEST_GAMES[:]
        self.interface.do_home('')

    def testSubCategoryDict(self):
        """Test generatirng sub-category menu data."""
        check = {'A': 'Null', 'B': 'Unit', '<': 'Previous Menu', '!': 'Quit'}
        self.assertEqual(check, self.interface.show_menu(TEST_CATEGORIES['sub-categories']['Unit Games']))

    def testSubCategoryText(self):
        """Test displaying a sub-category menu."""
        check = ['\n', 'Home Menu > Unit Games\n', '\n', 'A: Null\n', 'B: Unit\n', '<: Previous Menu\n']
        check += ['!: Quit\n']
        self.interface.titles = ['Home Menu', 'Unit Games']
        self.interface.show_menu(TEST_CATEGORIES['sub-categories']['Unit Games'])
        self.assertEqual(check, self.bot.info)

    def testTopLevelDict(self):
        """Test generating top level menu data."""
        check = {'A': 'Unit Games Category', 'B': 'Flip', 'C': 'Sorter', '!': 'Quit'}
        categories = TEST_CATEGORIES.copy()
        self.assertEqual(check, self.interface.show_menu(categories))

    def testTopLevelText(self):
        """Test displaying the top level menu."""
        check = ['\n', 'Home Menu\n', '\n', 'A: Unit Games Category\n', 'B: Flip\n', 'C: Sorter\n']
        check += ['!: Quit\n']
        self.interface.show_menu(TEST_CATEGORIES.copy())
        self.assertEqual(check, self.bot.info)


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


class StatisticsBinResultsTest(unittest.TestCase):
    """Tests of Statistics.bin_results. (unittest.TestCase)"""

    def setUp(self):
        test_results = [results[:] for results in TEST_RESULTS]
        for results in test_results:
            results[-2] = 0
        self.stats = interface.Statistics(test_results)

    def testGameRecord(self):
        """Test the game win/loss/draw calculation."""
        self.assertEqual([5, 6, 1], self.stats.game_wld)

    def testPlayerRecord(self):
        """Test the player win/loss/draw calculation."""
        self.assertEqual([12, 10, 3], self.stats.player_wld)


class StatisticsBinResultsMatchTest(unittest.TestCase):
    """Tests of Statistics.bin_results with match play. (unittest.TestCase)"""

    def setUp(self):
        test_results = [results[:] for results in TEST_RESULTS]
        for results in test_results:
            results[-2] = 256
        self.stats = interface.Statistics(test_results)

    def testGameRecord(self):
        """Test the game win/loss/draw calculation with match play."""
        self.assertEqual([6, 4, 2], self.stats.game_wld)

    def testPlayerRecord(self):
        """Test the player win/loss/draw calculation with match play."""
        self.assertEqual([12, 10, 3], self.stats.player_wld)


class StatisticsDunderTest(unittest.TestCase):
    """Tests of the other dunder methods for the Statistics class. (unittest.TestCase)"""

    def setUp(self):
        self.stats = interface.Statistics([result[:] for result in TEST_RESULTS], title = 'Test Statistics')

    def testBool(self):
        """Test boolean conversion of statistics."""
        self.assertTrue(bool(self.stats))

    def testBoolNot(self):
        """Test boolean conversion of empty statistics."""
        self.assertFalse(bool(interface.Statistics([])))

    def testRepr(self):
        """Test the debugging text representation."""
        self.assertEqual('<Statistics object with Test Statistics for 7 results>', repr(self.stats))

    def testReprOne(self):
        """Test the debugging text representation with one result."""
        self.stats.results['overall'] = self.stats.results['overall'][:1]
        self.assertEqual('<Statistics object with Test Statistics for 1 result>', repr(self.stats))


class StatisticsFilterResultsTest(unittest.TestCase):
    """Tests of the Statistics's results filtering. (untittest.TestCase)"""

    def testFilterAll(self):
        """Test filtering with nothing allowed."""
        check = [result[:] for result in TEST_RESULTS]
        for index in (11, 5, 4, 3, 0):
            del check[index]
        self.stats = interface.Statistics([result[:] for result in TEST_RESULTS])
        self.assertEqual(check, self.stats.results['overall'])

    def testFilterAllowCheating(self):
        """Test filtering with cheating allowed."""
        check = [result[:] for result in TEST_RESULTS]
        for index in (11, 5, 3):
            del check[index]
        self.stats = interface.Statistics([result[:] for result in TEST_RESULTS], 'cheat')
        self.assertEqual(check, self.stats.results['overall'])

    def testFilterAllowGipf(self):
        """Test filtering with gipf wins allowed."""
        check = [result[:] for result in TEST_RESULTS]
        for index in (11, 4, 3, 0):
            del check[index]
        self.stats = interface.Statistics([result[:] for result in TEST_RESULTS], 'gipf')
        self.assertEqual(check, self.stats.results['overall'])

    def testFilterAllowXyzzy(self):
        """Test filtering with xyzzy allowed."""
        check = [result[:] for result in TEST_RESULTS]
        for index in (5, 4, 0):
            del check[index]
        self.stats = interface.Statistics([result[:] for result in TEST_RESULTS], 'xyzzy')
        self.assertEqual(check, self.stats.results['overall'])

    def testFilterNone(self):
        """Test not filtering any results."""
        check = [result[:] for result in TEST_RESULTS]
        self.stats = interface.Statistics([result[:] for result in TEST_RESULTS], 'cheat gipf xyzzy')
        self.assertEqual(check, self.stats.results['overall'])


class StatisticsStringTest(unittest.TestCase):
    """Tests of the full output for a Statistics object."""

    def setUp(self):
        self.stats = interface.Statistics([result[:] for result in TEST_RESULTS], title = 'Test Statistics')
        self.text = str(self.stats)

    def testEmpty(self):
        """Test the output for no statistics."""
        stats = interface.Statistics([])
        self.assertEqual('\nNo statistics are available for those settings.', str(stats))

    def testGameRecord(self):
        """Test the game win/loss/draw output."""
        self.assertIn('Overall Win-Loss-Draw: 2-4-1', self.text)

    def testPlayerRecord(self):
        """Test the player win/loss/draw calculation."""
        self.assertIn('Player Win-Loss-Draw: 7-7-1', self.text)

    def testScoresLosing(self):
        """Test the losing scores output."""
        self.assertIn('Losing Scores: 0 : 3.00 / 3.5 : 5', self.text)

    def testScoresOverall(self):
        """Test the overall scores output."""
        self.assertIn('Overall Scores: 0 : 2.29 / 3.0 : 5', self.text)

    def testScoresWinning(self):
        """Test the winning scores output."""
        self.assertIn('Winning Scores: 0 : 2.00 / 2.0 : 4', self.text)

    def testStreakCurrent(self):
        """Test the current streak output."""
        self.assertIn('You are currently on a 2 game losing streak.', self.text)

    def testStreakDrawing(self):
        """Test the drawing streak output."""
        self.assertIn('Longest drawing streak: 1', self.text)

    def testStreakLosing(self):
        """Test the losing streak output."""
        self.assertIn('Longest losing streak: 2', self.text)

    def testStreakDrawing(self):
        """Test the drawing streak output."""
        self.assertIn('Longest drawing streak: 1', self.text)

    def testStreakWinning(self):
        """Test the winning streak output."""
        self.assertIn('Longest winning streak: 2', self.text)

    def testTitle(self):
        """Test outputting the title of the statistics."""
        self.assertIn('Test Statistics\n---------------', self.text)

    def testTurnsLosing(self):
        """Test the losing turns output."""
        self.assertIn('Losing Turns: 2 : 4.75 / 4.5 : 8', self.text)

    def testTurnsOverall(self):
        """Test the overall turns output."""
        self.assertIn('Overall Turns: 1 : 6.71 / 5.0 : 18', self.text)

    def testTurnsWinning(self):
        """Test the winning turns output."""
        self.assertIn('Winning Turns: 1 : 5.00 / 5.0 : 9', self.text)


class ValveTest(unittest.TestCase):
    """Tests of the RandomValve class. (unittest.TestCase)"""

    def setUp(self):
        self.valve = interface.RandomValve()

    def testRepr(self):
        """Test a random valve's debugging text representation."""
        self.assertEqual('<RandomValve 0.1000/0.1000>', repr(self.valve))

    def testReprReset(self):
        """Test a random valve's debugging text representation after it blows."""
        # Run the valve until it blows.
        for check in itertools.cycle('abc'):
            if self.valve.blow(check):
                break
        # Check the repr.
        self.assertEqual('<RandomValve 0.1000/0.1000>', repr(self.valve))

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
