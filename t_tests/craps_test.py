"""
craps_test.py

Unit testing of t_games/gambling_games/craps_game.py

Classes:
CrapsBetResolveTest: Testing the resolution of bets in Craps. (unittest.TestCase)
CrapsBetTextTest: A test of the text versions of bets in Craps. (unittest.TestCase)
CrapsBotTest: A test of the Craps bots. (unittest.TestCase)
"""


import unittest

from ..gambling_games import craps_game as craps
from . import unitility


class CrapsBetResolveTest(unittest.TestCase):
    """Testing the resolution of bets in Craps. (unittest.TestCase)"""

    def setDice(self, values):
        """
        Set the values of the dice for testing. (None)

        Parameters:
        values: The values to set the dice to. (list of int)
        """
        for die, value in zip(self.dice, values):
            die.value = value
        self.dice.values = values

    def setUp(self):
        self.player = unitility.AutoBot()
        self.game = craps.Craps(self.player, 'none')
        self.game.point = 8
        self.dice = craps.dice.Pool()

    def testBuyBetLose(self):
        """Test losing a buy bet."""
        bet = craps.BuyBet(self.player, 'buy', 10)
        bet.set_wager(6)
        self.setDice([3, 4])
        self.assertEqual(-12, bet.resolve(self.dice))

    def testBuyBetStay(self):
        """Test a buy bet staying."""
        bet = craps.BuyBet(self.player, 'buy', 9)
        bet.set_wager(6)
        self.setDice([3, 2])
        self.assertEqual(0, bet.resolve(self.dice))

    def testBuyBetWin(self):
        """Test winning a buy bet."""
        bet = craps.BuyBet(self.player, 'buy', 9)
        bet.set_wager(6)
        self.setDice([5, 4])
        self.assertEqual(9, bet.resolve(self.dice))

    def testComeLose(self):
        """Test losing a Come bet."""
        bet = craps.ComeBet(self.player, 'Come', 9)
        bet.set_wager(5)
        self.setDice([3, 4])
        self.assertEqual(-5, bet.resolve(self.dice))

    def testComeLoseNoPoint(self):
        """Test losing a Come bet with no point."""
        bet = craps.ComeBet(self.player, 'Come', 0)
        bet.set_wager(5)
        self.setDice([6, 6])
        self.assertEqual(-5, bet.resolve(self.dice))

    def testComeSetNoPoint(self):
        """Test a Come bet setting it's number with no point."""
        bet = craps.ComeBet(self.player, 'Come', 0)
        bet.set_wager(5)
        self.setDice([1, 4])
        bet.resolve(self.dice)
        self.assertEqual(5, bet.number)

    def testComeStay(self):
        """Test a Come bet staying."""
        bet = craps.ComeBet(self.player, 'Come', 9)
        bet.set_wager(5)
        self.setDice([2, 3])
        self.assertEqual(0, bet.resolve(self.dice))

    def testComeStayNoPoint(self):
        """Test a Come bet staying with no point."""
        bet = craps.ComeBet(self.player, 'Come', 0)
        bet.set_wager(5)
        self.setDice([2, 3])
        self.assertEqual(0, bet.resolve(self.dice))

    def testComeWin(self):
        """Test wining a Come bet."""
        bet = craps.ComeBet(self.player, 'Come', 9)
        bet.set_wager(5)
        self.setDice([4, 5])
        self.assertEqual(5, bet.resolve(self.dice))

    def testComeWinNoPoint(self):
        """Test wining a Come bet with no point."""
        bet = craps.ComeBet(self.player, 'Come', 0)
        bet.set_wager(5)
        self.setDice([3, 4])
        self.assertEqual(5, bet.resolve(self.dice))

    def testDontComeLose(self):
        """Test losing a don't come bet."""
        bet = craps.DontComeBet(self.player, "don't come", 9)
        bet.set_wager(5)
        self.setDice([3, 4])
        self.assertEqual(5, bet.resolve(self.dice))

    def testDontComeLoseNoPoint(self):
        """Test losing a don't come bet with no point."""
        bet = craps.DontComeBet(self.player, "don't come", 0)
        bet.set_wager(5)
        self.setDice([1, 2])
        self.assertEqual(5, bet.resolve(self.dice))

    def testDontComeSetNoPoint(self):
        """Test a don't come bet setting it's number with no point."""
        bet = craps.DontComeBet(self.player, "don't come", 0)
        bet.set_wager(5)
        self.setDice([1, 4])
        bet.resolve(self.dice)
        self.assertEqual(5, bet.number)

    def testDontComeStay(self):
        """Test a don't come bet staying."""
        bet = craps.DontComeBet(self.player, "don't come", 9)
        bet.set_wager(5)
        self.setDice([2, 3])
        self.assertEqual(0, bet.resolve(self.dice))

    def testDontComeStayNoPoint(self):
        """Test a don't come bet staying with no point."""
        bet = craps.DontComeBet(self.player, "don't come", 0)
        bet.set_wager(5)
        self.setDice([2, 3])
        self.assertEqual(0, bet.resolve(self.dice))

    def testDontComeStay(self):
        """Test a don't come bet staying on box cars."""
        bet = craps.DontComeBet(self.player, "don't come", 9)
        bet.set_wager(5)
        self.setDice([6, 6])
        self.assertEqual(0, bet.resolve(self.dice))

    def testDontComeWin(self):
        """Test wining a don't come bet."""
        bet = craps.DontComeBet(self.player, "don't come", 9)
        bet.set_wager(5)
        self.setDice([4, 5])
        self.assertEqual(-5, bet.resolve(self.dice))

    def testDontComeWinNoPoint(self):
        """Test wining a don't come bet with no point."""
        bet = craps.DontComeBet(self.player, "don't come", 0)
        bet.set_wager(5)
        self.setDice([3, 4])
        self.assertEqual(-5, bet.resolve(self.dice))

    def testDontPassLose(self):
        """Test losing a don't pass bet."""
        bet = craps.DontPassBet(self.player, "don't pass", 9)
        bet.set_wager(5)
        self.setDice([3, 4])
        self.assertEqual(5, bet.resolve(self.dice))

    def testDontPassLoseNoPoint(self):
        """Test losing a don't pass bet with no point."""
        bet = craps.DontPassBet(self.player, "don't pass", 0)
        bet.set_wager(5)
        self.setDice([1, 2])
        self.assertEqual(5, bet.resolve(self.dice))

    def testDontPassSetNoPoint(self):
        """Test a don't pass bet setting it's number with no point."""
        bet = craps.DontPassBet(self.player, "don't pass", 0)
        bet.set_wager(5)
        self.setDice([1, 4])
        bet.resolve(self.dice)
        self.assertEqual(5, bet.number)

    def testDontPassStay(self):
        """Test a don't pass bet staying."""
        bet = craps.DontPassBet(self.player, "don't pass", 9)
        bet.set_wager(5)
        self.setDice([2, 3])
        self.assertEqual(0, bet.resolve(self.dice))

    def testDontPassStayNoPoint(self):
        """Test a don't pass bet staying with no point."""
        bet = craps.DontPassBet(self.player, "don't pass", 0)
        bet.set_wager(5)
        self.setDice([2, 3])
        self.assertEqual(0, bet.resolve(self.dice))

    def testDontPassStay(self):
        """Test a don't pass bet staying on box cars."""
        bet = craps.DontPassBet(self.player, "don't pass", 9)
        bet.set_wager(5)
        self.setDice([6, 6])
        self.assertEqual(0, bet.resolve(self.dice))

    def testDontPassWin(self):
        """Test wining a don't pass bet."""
        bet = craps.DontPassBet(self.player, "don't pass", 9)
        bet.set_wager(5)
        self.setDice([4, 5])
        self.assertEqual(-5, bet.resolve(self.dice))

    def testDontPassWinNoPoint(self):
        """Test wining a don't pass bet with no point."""
        bet = craps.DontPassBet(self.player, "don't pass", 0)
        bet.set_wager(5)
        self.setDice([3, 4])
        self.assertEqual(-5, bet.resolve(self.dice))

    def testHardWayLoseNoPoint(self):
        """Test losing a hard way bet with no point."""
        bet = craps.HardWayBet(self.player, 'hard 4', 8)
        bet.set_wager(5)
        self.setDice([5, 3])
        self.assertEqual(-5, bet.resolve(self.dice))

    def testHardWayLoseSeven(self):
        """Test losing a hard way bet with a seven."""
        bet = craps.HardWayBet(self.player, 'hard 4', 8)
        bet.set_wager(5)
        self.setDice([5, 2])
        self.assertEqual(-5, bet.resolve(self.dice))

    def testHardWayLoseTarget(self):
        """Test losing a hard way bet with the target number."""
        bet = craps.HardWayBet(self.player, 'hard 4', 8)
        bet.set_wager(5)
        self.setDice([5, 3])
        self.assertEqual(-5, bet.resolve(self.dice))

    def testHardWayStay(self):
        """Test a hard way bet staying active."""
        bet = craps.HardWayBet(self.player, 'hard 4', 4)
        bet.set_wager(5)
        self.setDice([1, 4])
        self.assertEqual(0, bet.resolve(self.dice))

    def testHardWayStayLazy(self):
        """Test a hard way bet staying active while lazy."""
        bet = craps.HardWayBet(self.player, 'hard 4', 4)
        bet.set_wager(5)
        self.game.point = 0
        self.game.lazy_hard = True
        self.setDice([1, 3])
        self.assertEqual(0, bet.resolve(self.dice))

    def testHardWayWin(self):
        """Test winning a hard way bet."""
        bet = craps.HardWayBet(self.player, 'hard 4', 4)
        bet.set_wager(5)
        self.setDice([2, 2])
        self.assertEqual(35, bet.resolve(self.dice))

    def testHardWayWinBig(self):
        """Test winning a hard way bet with larger payout."""
        bet = craps.HardWayBet(self.player, 'hard 4', 6)
        bet.set_wager(5)
        self.setDice([3, 3])
        self.assertEqual(45, bet.resolve(self.dice))

    def testHardWayWinNoPoint(self):
        """Test winning a hard way bet with no point."""
        bet = craps.HardWayBet(self.player, 'hard 4', 4)
        bet.set_wager(5)
        self.game.point = 0
        self.setDice([2, 2])
        self.assertEqual(35, bet.resolve(self.dice))

    def testLayBetLose(self):
        """Test losing a lay bet."""
        bet = craps.LayBet(self.player, 'lay', 9)
        bet.set_wager(6)
        self.setDice([6, 3])
        self.assertEqual(-4, bet.resolve(self.dice))

    def testLayBetStay(self):
        """Test a lay bet staying."""
        bet = craps.LayBet(self.player, 'lay', 9)
        bet.set_wager(6)
        self.setDice([3, 2])
        self.assertEqual(0, bet.resolve(self.dice))

    def testLayBetWin(self):
        """Test winning a lay bet."""
        bet = craps.LayBet(self.player, 'lay', 6)
        bet.set_wager(6)
        self.setDice([5, 2])
        self.assertEqual(5, bet.resolve(self.dice))

    def testPassLose(self):
        """Test losing a pass bet."""
        bet = craps.PassBet(self.player, 'pass', 8)
        bet.set_wager(5)
        self.setDice([1, 6])
        self.assertEqual(-5, bet.resolve(self.dice))

    def testPassLoseNoPoint(self):
        """Test losing a pass bet with no point."""
        bet = craps.PassBet(self.player, 'pass', 0)
        bet.set_wager(5)
        self.setDice([6, 6])
        self.assertEqual(-5, bet.resolve(self.dice))

    def testPassSetNoPoint(self):
        """Test a pass bet setting it's number with no point."""
        bet = craps.PassBet(self.player, 'pass', 0)
        bet.set_wager(5)
        self.setDice([1, 4])
        bet.resolve(self.dice)
        self.assertEqual(5, bet.number)

    def testPassStay(self):
        """Test a pass bet staying."""
        bet = craps.PassBet(self.player, 'pass', 8)
        bet.set_wager(5)
        self.setDice([2, 3])
        self.assertEqual(0, bet.resolve(self.dice))

    def testPassStayNoPoint(self):
        """Test a pass bet staying with no point."""
        bet = craps.PassBet(self.player, 'pass', 0)
        bet.set_wager(5)
        self.setDice([2, 3])
        self.assertEqual(0, bet.resolve(self.dice))

    def testPassWin(self):
        """Test wining a pass bet."""
        bet = craps.PassBet(self.player, 'pass', 8)
        bet.set_wager(5)
        self.setDice([3, 5])
        self.assertEqual(5, bet.resolve(self.dice))

    def testPassWinNoPoint(self):
        """Test wining a pass bet with no point."""
        bet = craps.PassBet(self.player, 'pass', 0)
        bet.set_wager(5)
        self.setDice([3, 4])
        self.assertEqual(5, bet.resolve(self.dice))

    def testPlaceBetLose(self):
        """Test losing a place bet."""
        bet = craps.PlaceBet(self.player, 'place 9', 9)
        bet.set_wager(5)
        self.setDice([5, 2])
        self.assertEqual(-7, bet.resolve(self.dice))

    def testPlaceBetStay(self):
        """Test a place bet staying."""
        bet = craps.PlaceBet(self.player, 'place 9', 9)
        bet.set_wager(6)
        self.setDice([3, 2])
        self.assertEqual(0, bet.resolve(self.dice))

    def testPlaceBetWin(self):
        """Test winning a place bet."""
        bet = craps.PlaceBet(self.player, 'place 3', 6)
        bet.set_wager(6)
        self.setDice([4, 2])
        self.assertEqual(7, bet.resolve(self.dice))

    def testPropLose(self):
        """Test losing a proposition bet."""
        bet = craps.PropositionBet(self.player, 'horn')
        bet.set_wager(8)
        self.setDice([6, 2])
        self.assertEqual(-8, bet.resolve(self.dice))

    def testPropSpecialOdds(self):
        """Test winning a proposition bet with special odds."""
        bet = craps.PropositionBet(self.player, 'field')
        bet.set_wager(8)
        self.setDice([1, 1])
        self.assertEqual(16, bet.resolve(self.dice))

    def testPropWin(self):
        """Test winning a proposition bet."""
        bet = craps.PropositionBet(self.player, 'craps')
        bet.set_wager(8)
        self.setDice([1, 2])
        self.assertEqual(56, bet.resolve(self.dice))


class CrapsBetTextTest(unittest.TestCase):
    """A test of text versions of the bets in Craps. (unittest.TestCase)"""

    def setUp(self):
        self.player = unitility.AutoBot()
        self.game = craps.Craps(self.player, 'none')

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


#CrapsBotTest = unitility.bot_test(craps.Craps, [craps.Randy], 1, [1])
