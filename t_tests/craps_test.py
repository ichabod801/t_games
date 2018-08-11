"""
craps_test.py

Unit testing of t_games/gambling_games/craps_game.py

Classes:
CrapsBetTest: A test of the class for bets in Craps. (unittest.TestCase)
"""


import unittest

import t_games.gambling_games.craps_game as craps
import unitility


class CrapsBetTest(unittest.TestCase):
    """A test of the class for bets in Craps. (unittest.TestCase)"""

    def setUp(self):
        self.player = unitility.AutoBot()

    def testReprCome(self):
        """Test the computer readable text for a come bet."""
        bet = craps.ComeBet(self.player, 'come', 0)
        bet.wager = 108
        self.assertEqual('<ComeBet for 108 bucks>', repr(bet))

    def testReprComeNumber(self):
        """Test the computer readable text for a come bet with a number."""
        bet = craps.ComeBet(self.player, 'come', 6)
        bet.wager = 180
        self.assertEqual('<ComeBet on 6 for 180 bucks>', repr(bet))

    def testReprDontCome(self):
        """Test the computer readable text for a don't come bet."""
        bet = craps.DontComeBet(self.player, "don't come", 0)
        bet.wager = 14
        self.assertEqual('<DontComeBet for 14 bucks>', repr(bet))

    def testReprDontPass(self):
        """Test the computer readable text for a don't pass bet."""
        bet = craps.DontPassBet(self.player, "don't pass", 0)
        bet.wager = 32
        self.assertEqual('<DontPassBet for 32 bucks>', repr(bet))

    def testReprDontPassNumber(self):
        """Test the computer readable text for a don't come bet with a number."""
        bet = craps.DontPassBet(self.player, "don't pass", 10)
        bet.wager = 41
        self.assertEqual('<DontPassBet on 10 for 41 bucks>', repr(bet))

    def testReprDontComeNumber(self):
        """Test the computer readable text for a don't come bet with a number."""
        bet = craps.DontComeBet(self.player, "don't come", 9)
        bet.wager = 23
        self.assertEqual('<DontComeBet on 9 for 23 bucks>', repr(bet))

    def testReprHardWay(self):
        """Test the computer readable text for a hard way bet."""
        bet = craps.HardWayBet(self.player, 'hard 8', 8)
        bet.wager = 18
        self.assertEqual('<HardWayBet on 8 for 18 bucks>', repr(bet))

    def testReprOdds(self):
        """Test the computer readable text for an odds bet."""
        parent = craps.PassBet(self.player, 'pass', 4)
        bet = craps.OddsBet(self.player, 'pass odds', 4, parent)
        bet.wager = 50
        self.assertEqual('<OddsBet on 4 for 50 bucks>', repr(bet))

    def testReprPass(self):
        """Test the computer readable text for a pass bet."""
        bet = craps.PassBet(self.player, 'pass', 0)
        bet.wager = 81
        self.assertEqual('<PassBet for 81 bucks>', repr(bet))

    def testReprPassNumber(self):
        """Test the computer readable text for a pass bet with a number."""
        bet = craps.PassBet(self.player, 'pass', 5)
        bet.wager = 81
        self.assertEqual('<PassBet on 5 for 81 bucks>', repr(bet))

    def testReprPlace(self):
        """Test the computer readable text for a hard way bet."""
        bet = craps.PlaceBet(self.player, 'place 3', 3)
        bet.wager = 104
        self.assertEqual('<PlaceBet on 3 for 104 bucks>', repr(bet))

    def testReprProposition(self):
        """Test the computer readable text for a proposition bet."""
        bet = craps.PropositionBet(self.player, 'horn')
        bet.wager = 113
        self.assertEqual('<PropositionBet (Horn) for 113 bucks>', repr(bet))

    def testReprPropositionAlias(self):
        """Test the computer readable text for a proposition bet using an alias."""
        bet = craps.PropositionBet(self.player, '11')
        bet.wager = 122
        self.assertEqual('<PropositionBet (Yo) for 122 bucks>', repr(bet))


if __name__ == '__main__':
    unittest.main()
