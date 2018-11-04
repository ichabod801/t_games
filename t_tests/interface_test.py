"""
interface_test.py

Unit testing of t_games/interface.py

Classes:
InterfaceCommandTest: Tests of Interface command handling. (unittest.TestCase)
InterfaceGameTest: Tests of the Interface's game handling. (unittest.TestCase)
InterfaceTextTest: Tests of the Interface's text handling. (unittest.TestCase)
ValveTest: Tests of the RandomValve class. (unittest.TestCase)
"""


import itertools
import unittest

import t_games.interface as interface
import t_tests.unitility as unitility


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
        check = ['Bisley (Bisl)\n', 'Canfield (Demon, Canf)\n']
        check += ['Crazy Eights (Rockaway, Swedish Rummy, CrEi)\n', 'Cribbage (Crib)\n']
        check += ['Forty Thieves (Big Forty, Le Cadran, Napoleon at St Helena, Roosevelt at San Juan, FoTh)\n']
        check += ['FreeCell (Free)\n', 'Klondike (Seven Up, Sevens, Klon)\n']
        check += ['Monte Carlo (Weddings, MoCa)\n', 'Ninety-Nine (99)\n', 'Pyramid (Pyra)\n']
        check += ['Quadrille (Captive Queens, La Francaise, Partners, Quad)\n', 'Spider (Spid)\n']
        check += ['Strategy (Stra)\n']
        self.interface.focus = self.interface.categories['sub-categories']['Card Games']
        self.bot.replies = ['']
        self.interface.do_games('')
        self.assertEqual(check, self.bot.info[1:])

    def testGamesTerminal(self):
        """Test do_games with a terminal category."""
        check = ["Liar's Dice (Doubting Dice, Schummeln, Liars Dice, LiDi)\n", 'Pig\n']
        check += ['Solitaire Dice (SoDi)\n', 'Yacht (Yach)\n']
        self.interface.focus = self.interface.categories['sub-categories']['Dice Games']
        self.bot.replies = ['']
        self.interface.do_games('')
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
