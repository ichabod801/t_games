"""
prisoner_test.py

Classes:
AllCooperateTest: Tests of an always cooperate bot. (unittest.TestCase)
AllDefectTest: Tests of an always defect bot. (unittest.TestCase)
Gradual: Tests of a gradual bot. (unittest.TestCase)
"""


import unittest

from t_games.other_games import prisoner_game as prisoner
from t_games.t_tests import unitility


class AllCooperateTest(unittest.TestCase):
    """Tests of an always cooperate bot. (unittest.TestCase)"""

    def setUp(self):
        self.human = unitility.AutoBot()
        self.game = prisoner.PrisonersDilemma(self.human, 'all-co')
        self.bot = [player for player in self.game.players if player != self.human][0]

    def testCooperate(self):
        """Test all-co's response to cooperation."""
        self.bot.history = {self.human.name: ['cooperate']}
        self.assertEqual('cooperate', self.bot.get_move(self.human.name))

    def testDefect(self):
        """Test all-co's response to defection."""
        self.bot.history = {self.human.name: ['defect']}
        self.assertEqual('cooperate', self.bot.get_move(self.human.name))

    def testInitial(self):
        """Test all-co's initial move."""
        self.bot.history = {self.human.name: []}
        self.assertEqual('cooperate', self.bot.get_move(self.human.name))


class AllDefectTest(unittest.TestCase):
    """Tests of an always defect bot. (unittest.TestCase)"""

    def setUp(self):
        self.human = unitility.AutoBot()
        self.game = prisoner.PrisonersDilemma(self.human, 'all-def')
        self.bot = [player for player in self.game.players if player != self.human][0]

    def testCooperate(self):
        """Test all-def's response to cooperation."""
        self.bot.history = {self.human.name: ['cooperate']}
        self.assertEqual('defect', self.bot.get_move(self.human.name))

    def testDefect(self):
        """Test all-def's response to defection."""
        self.bot.history = {self.human.name: ['defect']}
        self.assertEqual('defect', self.bot.get_move(self.human.name))

    def testInitial(self):
        """Test all-def's initial move."""
        self.bot.history = {self.human.name: []}
        self.assertEqual('defect', self.bot.get_move(self.human.name))


class GradualTest(unittest.TestCase):
    """Tests of a gradual bot. (unittest.TestCase)"""

    def setUp(self):
        self.human = unitility.AutoBot()
        self.game = prisoner.PrisonersDilemma(self.human, 'gradual')
        self.bot = [player for player in self.game.players if player != self.human][0]
        self.bot.set_up()

    def testCooperate(self):
        """Test all-def's response to cooperation."""
        self.bot.history = {self.human.name: ['cooperate']}
        self.assertEqual('cooperate', self.bot.get_move(self.human.name))

    def testDefect(self):
        """Test all-def's response to defection."""
        self.bot.history = {self.human.name: []}
        human_moves = ['defect', 'cooperate', 'cooperate']
        bot_moves = []
        for human_move in human_moves:
            self.bot.history[self.human.name].append(human_move)
            bot_moves.append(self.bot.get_move(self.human.name))
        bot_check = ['d', 'c', 'c']
        self.assertEqual(bot_check, bot_moves)

    def testDefectCount(self):
        """Test all-def's updating retaliations."""
        self.bot.history = {self.human.name: ['defect']}
        self.bot.get_move(self.human.name)
        self.assertEqual(1, self.bot.retaliations)

    def testDefectTwo(self):
        """Test all-def's response to the second defection."""
        self.bot.history = {self.human.name: []}
        self.bot.retaliations = 1
        human_moves = ['defect', 'cooperate', 'defect', 'cooperate']
        bot_moves = []
        for human_move in human_moves:
            self.bot.history[self.human.name].append(human_move)
            bot_moves.append(self.bot.get_move(self.human.name))
        bot_check = ['d', 'd', 'c', 'c']
        self.assertEqual(bot_check, bot_moves)

    def testInitial(self):
        """Test all-def's initial move."""
        self.bot.history = {self.human.name: []}
        self.assertEqual('cooperate', self.bot.get_move(self.human.name))


if __name__ == '__main__':
    unittest.main()
