"""
interface_test.py

Unit testing of t_games/interface.py

Classes:
InterfaceGameTest: Tests of the Interface's game handling. (unittest.TestCase)
InterfaceTextTest: Tests of the Interface's text handling. (unittest.TestCase)
ValveTest: Tests of the RandomValve class. (unittest.TestCase)
"""


import itertools
import unittest

import t_games.interface as interface
import t_tests.unitility as unitility


class InterfaceGameTest(unittest.TestCase):
    """Tests of the Interface's game handling. (unittest.TestCase)"""

    def setUp(self):
        self.bot = unitility.AutoBot()
        self.interface = interface.Interface(self.bot)


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
