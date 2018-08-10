"""
player_test.py

Unittesting of t_games/player.py

Classes:
PlayerTextTest: Test the text representation of various play objects. (TestCase)
"""


import unittest
import sys

import t_games.player as player
import unitility


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
