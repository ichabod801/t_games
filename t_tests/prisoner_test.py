"""
prisoner_test.py

to test:
prober (pb): Starts with d, c, c. Defects forever if foe cooperates second and
    third move, otherwise plays Tit for Tat.
prober2 (p2): Starts with d, c, c. Cooperates forever if foe plays d, c second
    and third move, otherwise plays Tit for Tat.
prober3 (p3): Starts with d, c. Defects forever if foe plays c on the second
    move, otherwise plays Tit for Tat.
random (rd): Add a Random bot.
remorse-probe (rp): Add a Remorseful Prober Bot (like Naive Prober, but
    cooperates after probing)
soft-grudge (sg): Retailiates four times, followed by two cooperations.
soft-majr (sm): Cooperates on a majority of cooperations, otherwise defects.
tit-tat (tt): Add a Tit for Tat bot.
tit-2tat (t2): Add a Tit for Two Tats bot.
2tit-tat (2t): Add a Two Tits for Tat bot.

Classes:
AllCooperateTest: Tests of an always cooperate bot. (unittest.TestCase)
AllDefectTest: Tests of an always defect bot. (unittest.TestCase)
GradualTest: Tests of a gradual bot. (unittest.TestCase)
MajorityHardTest: Tests of the hard-majr bot. (unittest.TestCase)
NaiveProbeTest: Tests of the naive-probe bot. (unittest.TestCase)
PavlovTest: Test of the PavlovBot. (unittest.TestCase)
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

    def testCC(self):
        """Test pavlov's response to reward."""
        self.bot.next_move = 'cooperate'
        self.bot.history = {self.me_key: ['cooperate'], self.human.name: ['cooperate']}
        self.assertEqual('cooperate', self.bot.get_move(self.human.name))

    def testCD(self):
        """Test pavlov's response to sucker bet."""
        self.bot.next_move = 'cooperate'
        self.bot.history = {self.me_key: ['cooperate'], self.human.name: ['defect']}
        self.assertEqual('defect', self.bot.get_move(self.human.name))

    def testDC(self):
        """Test pavlov's response to temptation."""
        self.bot.next_move = 'defect'
        self.bot.history = {self.me_key: ['defect'], self.human.name: ['cooperate']}
        self.assertEqual('defect', self.bot.get_move(self.human.name))

    def testDD(self):
        """Test pavlov's response to punishment."""
        self.bot.next_move = 'defect'
        self.bot.history = {self.me_key: ['defect'], self.human.name: ['defect']}
        self.assertEqual('cooperate', self.bot.get_move(self.human.name))

    def testInitial(self):
        """Test grim's initial move."""
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


class TitForTatTest(unittest.TestCase):
    """Test of the Tit for Tat bot. (unittest.TestCase)"""

    def setUp(self):
        self.human = unitility.AutoBot()
        self.game = prisoner.PrisonersDilemma(self.human, 'tit-tat')
        self.bot = [player for player in self.game.players if player != self.human][0]
        self.bot.set_up()
        self.me_key = 'Me vs. {}'.format(self.human.name)

    def testCC(self):
        """Test tit for tat's response to reward."""
        self.bot.history = {self.me_key: ['cooperate'], self.human.name: ['cooperate']}
        self.assertEqual('cooperate', self.bot.get_move(self.human.name))

    def testCD(self):
        """Test tit for tat's response to sucker bet."""
        self.bot.history = {self.me_key: ['cooperate'], self.human.name: ['defect']}
        self.assertEqual('d', self.bot.get_move(self.human.name))

    def testDC(self):
        """Test tit for tat's response to temptation."""
        self.bot.history = {self.me_key: ['defect'], self.human.name: ['cooperate']}
        self.assertEqual('cooperate', self.bot.get_move(self.human.name))

    def testDD(self):
        """Test tit for tat's response to punishment."""
        self.bot.history = {self.me_key: ['defect'], self.human.name: ['defect']}
        self.assertEqual('d', self.bot.get_move(self.human.name))

    def testInitial(self):
        """Test grim's initial move."""
        self.assertEqual('cooperate', self.bot.get_move(self.human.name))


if __name__ == '__main__':
    unittest.main()
