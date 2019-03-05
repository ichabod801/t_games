"""
prisoner_test.py

Classes:
AllCooperateTest: Tests of an always cooperate bot. (unittest.TestCase)
AllDefectTest: Tests of an always defect bot. (unittest.TestCase)
GradualTest: Tests of a gradual bot. (unittest.TestCase)
MajorityHardTest: Tests of the hard-majr bot. (unittest.TestCase)
NaiveProbeTest: Tests of the naive-probe bot. (unittest.TestCase)
PrisonerMethodTest: Tests of the PrisonerMethodBot. (unittest.TestCase)
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


class MajorityHardTest(unittest.TestCase):
    """Tests of the hard-majr bot. (unittest.TestCase)"""

    def setUp(self):
        self.human = unitility.AutoBot()
        self.game = prisoner.PrisonersDilemma(self.human, 'hard-majr')
        self.bot = [player for player in self.game.players if player != self.human][0]
        self.bot.set_up()

    def testCooperate(self):
        """Test hard-majr's response to cooperation."""
        self.bot.history = {self.human.name: ['cooperate']}
        self.assertEqual('cooperate', self.bot.get_move(self.human.name))

    def testDefect(self):
        """Test hard-majr's response to defection."""
        self.bot.history = {self.human.name: ['defect']}
        self.assertEqual('defect', self.bot.get_move(self.human.name))

    def testEven(self):
        """Test hard-majr's response to an even history."""
        self.bot.history = {self.human.name: ['cooperate', 'cooperate', 'defect', 'defect']}
        self.assertEqual('defect', self.bot.get_move(self.human.name))

    def testInitial(self):
        """Test hard-majr's initial move."""
        self.bot.history = {self.human.name: []}
        self.assertEqual('defect', self.bot.get_move(self.human.name))

    def testMajorityDefect(self):
        """Test hard-majr's response to mostly defections."""
        self.bot.history = {self.human.name: ['defect', 'cooperate', 'cooperate', 'defect', 'defect']}
        self.assertEqual('defect', self.bot.get_move(self.human.name))

    def testMajorityCooperate(self):
        """Test hard-majr's response to mostly cooperations."""
        self.bot.history = {self.human.name: ['defect', 'cooperate', 'cooperate', 'defect', 'cooperate']}
        self.assertEqual('cooperate', self.bot.get_move(self.human.name))


class NaiveProbeTest(unittest.TestCase):
    """Tests of the naive-probe bot. (unittest.TestCase)"""

    def setUp(self):
        # Set up a random module you can manipulate.
        self.random_hold = prisoner.random
        self.mock_random = unitility.MockRandom([0.5, 0.6, 0.7, 0.95, 0.1, 0.2, 0.3, 0.4])
        prisoner.random = self.mock_random
        # Set up the game and the bot.
        self.human = unitility.AutoBot()
        self.game = prisoner.PrisonersDilemma(self.human, 'naive-probe')
        self.bot = [player for player in self.game.players if player != self.human][0]
        self.bot.set_up()

    def tearDown(self):
        prisoner.random = self.random_hold

    def testCooperate(self):
        """Test naive-probe's response to cooperation."""
        self.bot.history = {self.human.name: ['cooperate']}
        self.assertEqual('cooperate', self.bot.get_move(self.human.name))

    def testDefect(self):
        """Test naive-probe's response to defection."""
        self.bot.history = {self.human.name: ['defect']}
        self.assertEqual('d', self.bot.get_move(self.human.name))

    def testDefectRandom(self):
        """Test naive-probe's random defection."""
        self.bot.history = {self.human.name: ['cooperate'] * 10}
        for turn in range(4):
            self.bot.get_move(self.human.name)
        self.assertEqual('defect', self.bot.get_move(self.human.name))

    def testInitial(self):
        """Test naive-probe's initial move."""
        self.bot.history = {self.human.name: []}
        self.assertEqual('cooperate', self.bot.get_move(self.human.name))


class PavlovTest(unittest.TestCase):
    """Test of the PavlovBot. (unittest.TestCase)"""

    def setUp(self):
        self.human = unitility.AutoBot()
        self.game = prisoner.PrisonersDilemma(self.human, 'pavlov')
        self.bot = [player for player in self.game.players if player != self.human][0]
        self.bot.set_up()
        self.me_key = 'Me vs. {}'.format(self.human.name)

    def testCCC(self):
        """Test grim's response to reward after cooperation."""
        self.bot.next_move = 'cooperate'
        self.bot.history = {self.me_key: ['cooperate'], self.human.name: ['cooperate']}
        self.assertEqual('cooperate', self.bot.get_move(self.human.name))

    def testCCD(self):
        """Test grim's response to sucker bet after cooperation."""
        self.bot.next_move = 'cooperate'
        self.bot.history = {self.me_key: ['cooperate'], self.human.name: ['defect']}
        self.assertEqual('defect', self.bot.get_move(self.human.name))

    def testCDC(self):
        """Test grim's response to temptation after cooperation."""
        self.bot.next_move = 'cooperate'
        self.bot.history = {self.me_key: ['defect'], self.human.name: ['cooperate']}
        self.assertEqual('cooperate', self.bot.get_move(self.human.name))

    def testCDD(self):
        """Test grim's response to punishment after cooperation."""
        self.bot.next_move = 'cooperate'
        self.bot.history = {self.me_key: ['defect'], self.human.name: ['defect']}
        self.assertEqual('defect', self.bot.get_move(self.human.name))

    def testDCC(self):
        """Test grim's response to reward after defection."""
        self.bot.next_move = 'defect'
        self.bot.history = {self.me_key: ['cooperate'], self.human.name: ['cooperate']}
        self.assertEqual('defect', self.bot.get_move(self.human.name))

    def testDCD(self):
        """Test grim's response to sucker bet after defection."""
        self.bot.next_move = 'defect'
        self.bot.history = {self.me_key: ['cooperate'], self.human.name: ['defect']}
        self.assertEqual('cooperate', self.bot.get_move(self.human.name))

    def testDDC(self):
        """Test grim's response to temptation after defection."""
        self.bot.next_move = 'defect'
        self.bot.history = {self.me_key: ['defect'], self.human.name: ['cooperate']}
        self.assertEqual('defect', self.bot.get_move(self.human.name))

    def testDDD(self):
        """Test grim's response to punishment after defection."""
        self.bot.next_move = 'defect'
        self.bot.history = {self.me_key: ['defect'], self.human.name: ['defect']}
        self.assertEqual('cooperate', self.bot.get_move(self.human.name))

    def testInitial(self):
        """Test grim's initial move."""
        self.bot.history = {self.human.name: []}
        self.assertEqual('cooperate', self.bot.get_move(self.human.name))


class PrisonerMethodTest(unittest.TestCase):
    """Tests of the PrisonerMethodBot. (unittest.TestCase)"""

    def setUp(self):
        self.human = unitility.AutoBot()
        self.game = prisoner.PrisonersDilemma(self.human, 'grim')
        self.bot = [player for player in self.game.players if player != self.human][0]
        self.bot.set_up()

    def testCooperate(self):
        """Test grim's response to cooperation."""
        self.bot.history = {self.human.name: ['cooperate']}
        self.assertEqual('cooperate', self.bot.get_move(self.human.name))

    def testDefect(self):
        """Test grim's response to defection."""
        self.bot.history = {self.human.name: ['defect']}
        self.assertEqual('defect', self.bot.get_move(self.human.name))

    def testDefectAny(self):
        """Test grim's response to a single, old defection."""
        self.bot.history = {self.human.name: ['defect', 'cooperate', 'cooperate', 'cooperate']}
        self.assertEqual('defect', self.bot.get_move(self.human.name))

    def testInitial(self):
        """Test grim's initial move."""
        self.bot.history = {self.human.name: []}
        self.assertEqual('cooperate', self.bot.get_move(self.human.name))


if __name__ == '__main__':
    unittest.main()
