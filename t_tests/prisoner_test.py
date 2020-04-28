"""
prisoner_test.py

to test:
tit-2tat (t2): Add a Tit for Two Tats bot.
2tit-tat (2t): Add a Two Tits for Tat bot.

Classes:
AllCooperateTest: Tests of an always cooperate bot. (unittest.TestCase)
AllDefectTest: Tests of an always defect bot. (unittest.TestCase)
GradualTest: Tests of a gradual bot. (unittest.TestCase)
MajorityHardTest: Tests of the hard-majr bot. (unittest.TestCase)
MajoritySoftTest: Tests of the soft-majr bot. (unittest.TestCase)
NaiveProbeTest: Tests of the naive-probe bot. (unittest.TestCase)
PavlovTest: Test of the PavlovBot. (unittest.TestCase)
PrisonerMethodTest: Tests of the PrisonerMethodBot. (unittest.TestCase)
ProberTest: Tests of the Prober bot. (unittest.TestCase)
Prober2Test: Tests of the Prober II bot. (ProberTest)
Prober3Tests of the Prober III bot. (ProberTest)
SoftGrudgeTest: Tests of an soft-grudge bot. (unittest.TestCase)
TitForTatTest: Test of the Tit for Tat bot. (unittest.TestCase)
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
        self.bot.set_up()
        self.bot.foe_data = self.bot.data[self.human]

    def testCooperate(self):
        """Test all-co's response to cooperation."""
        self.bot.foe_data['them'] = ['cooperate']
        self.assertEqual('cooperate', self.bot.get_move())

    def testDefect(self):
        """Test all-co's response to defection."""
        self.bot.foe_data['them'] = ['defect']
        self.assertEqual('cooperate', self.bot.get_move())

    def testInitial(self):
        """Test all-co's initial move."""
        self.assertEqual('cooperate', self.bot.get_move())


class AllDefectTest(unittest.TestCase):
    """Tests of an always defect bot. (unittest.TestCase)"""

    def setUp(self):
        self.human = unitility.AutoBot()
        self.game = prisoner.PrisonersDilemma(self.human, 'all-def')
        self.bot = [player for player in self.game.players if player != self.human][0]
        self.bot.set_up()
        self.bot.foe_data = self.bot.data[self.human]

    def testCooperate(self):
        """Test all-def's response to cooperation."""
        self.bot.foe_data['them'] = ['cooperate']
        self.assertEqual('defect', self.bot.get_move())

    def testDefect(self):
        """Test all-def's response to defection."""
        self.bot.foe_data['them'] = ['defect']
        self.assertEqual('defect', self.bot.get_move())

    def testInitial(self):
        """Test all-def's initial move."""
        self.assertEqual('defect', self.bot.get_move())


class GradualTest(unittest.TestCase):
    """Tests of a gradual bot. (unittest.TestCase)"""

    def setUp(self):
        self.human = unitility.AutoBot()
        self.game = prisoner.PrisonersDilemma(self.human, 'gradual')
        self.bot = [player for player in self.game.players if player != self.human][0]
        self.bot.set_up()
        self.bot.foe_data = self.bot.data[self.human]

    def testCooperate(self):
        """Test all-def's response to cooperation."""
        self.bot.foe_data['them'] = ['cooperate']
        self.assertEqual('cooperate', self.bot.get_move())

    def testDefect(self):
        """Test all-def's response to defection."""
        human_moves = ['defect', 'cooperate', 'cooperate']
        bot_moves = []
        for human_move in human_moves:
            self.bot.foe_data['them'].append(human_move)
            bot_moves.append(self.bot.get_move())
        bot_check = ['defect', 'cooperate', 'cooperate']
        self.assertEqual(bot_check, bot_moves)

    def testDefectCount(self):
        """Test all-def's updating retaliations."""
        self.bot.foe_data['them'] = ['defect']
        self.bot.get_move()
        self.assertEqual(1, self.bot.foe_data['retaliations'])

    def testDefectTwo(self):
        """Test all-def's response to the second defection."""
        self.bot.foe_data['retaliations'] = 1
        human_moves = ['defect', 'cooperate', 'defect', 'cooperate']
        bot_moves = []
        for human_move in human_moves:
            self.bot.foe_data['them'].append(human_move)
            bot_moves.append(self.bot.get_move())
        bot_check = ['defect', 'defect', 'cooperate', 'cooperate']
        self.assertEqual(bot_check, bot_moves)

    def testInitial(self):
        """Test all-def's initial move."""
        self.assertEqual('cooperate', self.bot.get_move())


class MajorityHardTest(unittest.TestCase):
    """Tests of the hard-majr bot. (unittest.TestCase)"""

    def setUp(self):
        self.human = unitility.AutoBot()
        self.game = prisoner.PrisonersDilemma(self.human, 'hard-majr')
        self.bot = [player for player in self.game.players if player != self.human][0]
        self.bot.set_up()
        self.bot.foe_data = self.bot.data[self.human]

    def testCooperate(self):
        """Test hard-majr's response to cooperation."""
        self.bot.foe_data['them'] = ['cooperate']
        self.assertEqual('cooperate', self.bot.get_move())

    def testDefect(self):
        """Test hard-majr's response to defection."""
        self.bot.foe_data['them'] = ['defect']
        self.assertEqual('defect', self.bot.get_move())

    def testEven(self):
        """Test hard-majr's response to an even history."""
        self.bot.foe_data['them'] = ['cooperate', 'cooperate', 'defect', 'defect']
        self.assertEqual('defect', self.bot.get_move())

    def testInitial(self):
        """Test hard-majr's initial move."""
        self.assertEqual('defect', self.bot.get_move())

    def testMajorityDefect(self):
        """Test hard-majr's response to mostly defections."""
        self.bot.foe_data['them'] = ['defect', 'cooperate', 'cooperate', 'defect', 'defect']
        self.assertEqual('defect', self.bot.get_move())

    def testMajorityCooperate(self):
        """Test hard-majr's response to mostly cooperations."""
        self.bot.foe_data['them'] = ['defect', 'cooperate', 'cooperate', 'defect', 'cooperate']
        self.assertEqual('cooperate', self.bot.get_move())


class MajoritySoftTest(unittest.TestCase):
    """Tests of the soft-majr bot. (unittest.TestCase)"""

    def setUp(self):
        self.human = unitility.AutoBot()
        self.game = prisoner.PrisonersDilemma(self.human, 'soft-majr')
        self.bot = [player for player in self.game.players if player != self.human][0]
        self.bot.set_up()
        self.bot.foe_data = self.bot.data[self.human]

    def testCooperate(self):
        """Test soft-majr's response to cooperation."""
        self.bot.foe_data['them'] = ['cooperate']
        self.assertEqual('cooperate', self.bot.get_move())

    def testDefect(self):
        """Test soft-majr's response to defection."""
        self.bot.foe_data['them'] = ['defect']
        self.assertEqual('defect', self.bot.get_move())

    def testEven(self):
        """Test soft-majr's response to an even history."""
        self.bot.foe_data['them'] = ['cooperate', 'cooperate', 'defect', 'defect']
        self.assertEqual('cooperate', self.bot.get_move())

    def testInitial(self):
        """Test soft-majr's initial move."""
        self.assertEqual('cooperate', self.bot.get_move())

    def testMajorityDefect(self):
        """Test soft-majr's response to mostly defections."""
        self.bot.foe_data['them'] = ['defect', 'cooperate', 'cooperate', 'defect', 'defect']
        self.assertEqual('defect', self.bot.get_move())

    def testMajorityCooperate(self):
        """Test soft-majr's response to mostly cooperations."""
        self.bot.foe_data['them'] = ['defect', 'cooperate', 'cooperate', 'defect', 'cooperate']
        self.assertEqual('cooperate', self.bot.get_move())


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
        self.bot.foe_data = self.bot.data[self.human]

    def tearDown(self):
        prisoner.random = self.random_hold

    def testCooperate(self):
        """Test naive-probe's response to cooperation."""
        self.bot.foe_data['them'] = ['cooperate']
        self.assertEqual('cooperate', self.bot.get_move())

    def testDefect(self):
        """Test naive-probe's response to defection."""
        self.bot.foe_data['them'] = ['defect']
        self.assertEqual('defect', self.bot.get_move())

    def testDefectRandom(self):
        """Test naive-probe's random defection."""
        self.bot.foe_data['them'] = ['cooperate'] * 10
        for turn in range(4):
            self.bot.get_move()
        self.assertEqual('defect', self.bot.get_move())

    def testInitial(self):
        """Test naive-probe's initial move."""
        self.assertEqual('cooperate', self.bot.get_move())


class PavlovTest(unittest.TestCase):
    """Test of the PavlovBot. (unittest.TestCase)"""

    def setUp(self):
        self.human = unitility.AutoBot()
        self.game = prisoner.PrisonersDilemma(self.human, 'pavlov')
        self.bot = [player for player in self.game.players if player != self.human][0]
        self.bot.set_up()
        self.bot.foe_data = self.bot.data[self.human]

    def testCC(self):
        """Test pavlov's response to reward."""
        self.bot.foe_data['me'] = ['cooperate']
        self.bot.foe_data['them'] = ['cooperate']
        self.assertEqual('cooperate', self.bot.get_move())

    def testCD(self):
        """Test pavlov's response to sucker bet."""
        self.bot.foe_data['me'] = ['cooperate']
        self.bot.foe_data['them'] = ['defect']
        self.assertEqual('defect', self.bot.get_move())

    def testDC(self):
        """Test pavlov's response to temptation."""
        self.bot.foe_data['me'] = ['defect']
        self.bot.foe_data['them'] = ['cooperate']
        self.assertEqual('defect', self.bot.get_move())

    def testDD(self):
        """Test pavlov's response to punishment."""
        self.bot.foe_data['me'] = ['defect']
        self.bot.foe_data['them'] = ['defect']
        self.assertEqual('cooperate', self.bot.get_move())

    def testInitial(self):
        """Test grim's initial move."""
        self.assertEqual('cooperate', self.bot.get_move())


class PrisonerMethodTest(unittest.TestCase):
    """Tests of the PrisonerMethodBot. (unittest.TestCase)"""

    def setUp(self):
        self.human = unitility.AutoBot()
        self.game = prisoner.PrisonersDilemma(self.human, 'grim')
        self.bot = [player for player in self.game.players if player != self.human][0]
        self.bot.set_up()
        self.bot.foe_data = self.bot.data[self.human]

    def testCooperate(self):
        """Test grim's response to cooperation."""
        self.bot.foe_data['them'] = ['cooperate']
        self.assertEqual('cooperate', self.bot.get_move())

    def testDefect(self):
        """Test grim's response to defection."""
        self.bot.foe_data['them'] = ['defect']
        self.assertEqual('defect', self.bot.get_move())

    def testDefectAny(self):
        """Test grim's response to a single, old defection."""
        self.bot.foe_data['grim'] = True
        self.assertEqual('defect', self.bot.get_move())

    def testInitial(self):
        """Test grim's initial move."""
        self.assertEqual('cooperate', self.bot.get_move())


class ProberTest(unittest.TestCase):
    """Tests of the Prober bot. (unittest.TestCase)"""

    def setUp(self):
        self.human = unitility.AutoBot()
        self.game = prisoner.PrisonersDilemma(self.human, 'prober')
        self.bot = [player for player in self.game.players if player != self.human][0]
        self.bot.set_up()
        self.bot.foe_data = self.bot.data[self.human]

    def testSingleCooperate(self):
        """Test prober's response to cooperate in single response mode."""
        self.trigger(['defect', 'cooperate', 'cooperate'])
        self.bot.foe_data['them'].append('cooperate')
        self.assertEqual('d', self.bot.get_move()[0])

    def testSingleDefect(self):
        """Test prober's response to defect in single response mode."""
        self.trigger(['cooperate', 'cooperate', 'cooperate'])
        self.bot.foe_data['them'].append('cooperate')
        self.assertEqual('d', self.bot.get_move()[0])

    def testTFTCooperate(self):
        """Test prober's response to cooperate in TFT mode."""
        self.trigger(['cooperate', 'defect', 'cooperate'])
        self.bot.foe_data['them'].append('cooperate')
        self.assertEqual('c', self.bot.get_move()[0])

    def testTFTDefect(self):
        """Test prober's response to cooperate in TFT mode."""
        self.trigger(['cooperate', 'cooperate', 'defect'])
        self.bot.foe_data['them'].append('defect')
        self.assertEqual('d', self.bot.get_move()[0])

    def testInitial(self):
        """Test prober's initial move."""
        first_moves = []
        for move in range(3):
            first_moves.append(self.bot.get_move()[0])
            self.bot.foe_data['them'].append('cooperate')
        self.assertEqual(['d', 'c', 'c'], first_moves)

    def trigger(self, moves):
        """
        Trigger the prober's decision about long term play. (None)

        Parameters:
        moves: The human moves to trigger prober with. (list of str)
        """
        self.bot.foe_data['them'] = moves
        self.bot.get_move()


class Prober2Test(ProberTest):
    """Tests of the Prober II bot. (unittest.TestCase)"""

    def setUp(self):
        self.human = unitility.AutoBot()
        self.game = prisoner.PrisonersDilemma(self.human, 'prober-2')
        self.bot = [player for player in self.game.players if player != self.human][0]
        self.bot.set_up()
        self.bot.foe_data = self.bot.data[self.human]

    def testSingleCooperate(self):
        """Test prober's response to cooperate in single response mode."""
        self.trigger(['defect', 'defect', 'cooperate'])
        self.bot.foe_data['them'].append('cooperate')
        self.assertEqual('c', self.bot.get_move()[0])

    def testSingleDefect(self):
        """Test prober's response to defect in single response mode."""
        self.trigger(['cooperate', 'defect', 'cooperate'])
        self.bot.foe_data['them'].append('cooperate')
        self.assertEqual('c', self.bot.get_move()[0])

    def testTFTCooperate(self):
        """Test prober's response to cooperate in TFT mode."""
        self.trigger(['cooperate', 'cooperate', 'cooperate'])
        self.bot.foe_data['them'].append('cooperate')
        self.assertEqual('c', self.bot.get_move()[0])

    def testTFTDefect(self):
        """Test prober's response to cooperate in TFT mode."""
        self.trigger(['cooperate', 'defect', 'defect'])
        self.bot.foe_data['them'].append('defect')
        self.assertEqual('d', self.bot.get_move()[0])

    def testInitial(self):
        """Test prober's initial move."""
        first_moves = []
        for move in range(3):
            first_moves.append(self.bot.get_move()[0])
            self.bot.foe_data['them'].append('cooperate')
        self.assertEqual(['d', 'c', 'c'], first_moves)


class Prober3Test(ProberTest):
    """Tests of the Prober III bot. (unittest.TestCase)"""

    def setUp(self):
        self.human = unitility.AutoBot()
        self.game = prisoner.PrisonersDilemma(self.human, 'prober-3')
        self.bot = [player for player in self.game.players if player != self.human][0]
        self.bot.set_up()
        self.bot.foe_data = self.bot.data[self.human]

    def testSingleCooperate(self):
        """Test prober's response to cooperate in single response mode."""
        self.trigger(['defect', 'cooperate'])
        self.bot.foe_data['them'].append('cooperate')
        self.assertEqual('d', self.bot.get_move()[0])

    def testSingleDefect(self):
        """Test prober's response to defect in single response mode."""
        self.trigger(['cooperate', 'cooperate'])
        self.bot.foe_data['them'].append('cooperate')
        self.assertEqual('d', self.bot.get_move()[0])

    def testTFTCooperate(self):
        """Test prober's response to cooperate in TFT mode."""
        self.trigger(['defect', 'defect'])
        self.bot.foe_data['them'].append('cooperate')
        self.assertEqual('c', self.bot.get_move()[0])

    def testTFTDefect(self):
        """Test prober's response to cooperate in TFT mode."""
        self.trigger(['cooperate', 'defect'])
        self.bot.foe_data['them'].append('defect')
        self.assertEqual('d', self.bot.get_move()[0])

    def testInitial(self):
        """Test prober's initial move."""
        first_moves = []
        for move in range(2):
            first_moves.append(self.bot.get_move()[0])
            self.bot.foe_data['them'].append('cooperate')
        self.assertEqual(['d', 'c'], first_moves)


class SoftGrudgeTest(unittest.TestCase):
    """Tests of an always soft-grudge bot. (unittest.TestCase)"""

    def setUp(self):
        self.human = unitility.AutoBot()
        self.game = prisoner.PrisonersDilemma(self.human, 'soft-grudge')
        self.bot = [player for player in self.game.players if player != self.human][0]
        self.bot.set_up()
        self.bot.foe_data = self.bot.data[self.human]

    def testCooperate(self):
        """Test soft-grudge's response to cooperation."""
        self.bot.foe_data['them'] = ['cooperate']
        self.assertEqual('cooperate', self.bot.get_move())

    def testDefect(self):
        """Test soft-grudge's response to defection."""
        self.bot.foe_data['them'] = ['defect']
        actual = [self.bot.get_move()[0] for move in range(6)]
        self.assertEqual(list('ddddcc'), actual)

    def testInitial(self):
        """Test soft-grudge's initial move."""
        self.bot.history = {self.human.name: []}
        self.assertEqual('cooperate', self.bot.get_move())


class TitForTatTest(unittest.TestCase):
    """Test of the Tit for Tat bot. (unittest.TestCase)"""

    def setUp(self):
        self.human = unitility.AutoBot()
        self.game = prisoner.PrisonersDilemma(self.human, 'tit-tat')
        self.bot = [player for player in self.game.players if player != self.human][0]
        self.bot.set_up()
        self.bot.foe_data = self.bot.data[self.human]

    def testCC(self):
        """Test tit for tat's response to reward."""
        self.bot.foe_data['me'] = ['cooperate']
        self.bot.foe_data['them'] = ['cooperate']
        self.assertEqual('cooperate', self.bot.get_move())

    def testCD(self):
        """Test tit for tat's response to sucker bet."""
        self.bot.foe_data['me'] = ['cooperate']
        self.bot.foe_data['them'] = ['defect']
        self.assertEqual('defect', self.bot.get_move())

    def testDC(self):
        """Test tit for tat's response to temptation."""
        self.bot.foe_data['me'] = ['defect']
        self.bot.foe_data['them'] = ['cooperate']
        self.assertEqual('cooperate', self.bot.get_move())

    def testDD(self):
        """Test tit for tat's response to punishment."""
        self.bot.foe_data['me'] = ['defect']
        self.bot.foe_data['them'] = ['defect']
        self.assertEqual('defect', self.bot.get_move())

    def testInitial(self):
        """Test grim's initial move."""
        self.assertEqual('cooperate', self.bot.get_move())


class TitTwoTatTest(unittest.TestCase):
    """Test of the Tit for Two Tats bot. (unittest.TestCase)"""

    def setUp(self):
        self.human = unitility.AutoBot()
        self.game = prisoner.PrisonersDilemma(self.human, 'tit-2tat')
        self.bot = [player for player in self.game.players if player != self.human][0]
        self.bot.set_up()
        self.bot.foe_data = self.bot.data[self.human]

    def testCC(self):
        """Test tit for two tat's response to reward."""
        self.bot.foe_data['me'] = ['cooperate']
        self.bot.foe_data['them'] = ['cooperate']
        self.assertEqual('cooperate', self.bot.get_move())

    def testCD(self):
        """Test tit for two tat's response to sucker bet."""
        self.bot.foe_data['me'] = ['cooperate']
        self.bot.foe_data['them'] = ['defect']
        self.assertEqual('cooperate', self.bot.get_move())

    def testDC(self):
        """Test tit for two tat's response to temptation."""
        self.bot.foe_data['me'] = ['defect']
        self.bot.foe_data['them'] = ['cooperate']
        self.assertEqual('cooperate', self.bot.get_move())

    def testDD(self):
        """Test tit for two tat's response to punishment."""
        self.bot.foe_data['me'] = ['defect']
        self.bot.foe_data['them'] = ['defect']
        self.assertEqual('cooperate', self.bot.get_move())

    def testInitial(self):
        """Test tit for two tat's initial move."""
        self.assertEqual('cooperate', self.bot.get_move())

    def testTwoTats(self):
        """Test tit for two tat's response to two defections."""
        self.bot.foe_data['me'] = ['cooperate', 'cooperate']
        self.bot.foe_data['them'] = ['defect', 'defect']
        self.assertEqual('defect', self.bot.get_move())

    def testTwoTits(self):
        """Test tit for two tat's second respons to getting triggered."""
        self.bot.foe_data['me'] = ['cooperate', 'cooperate']
        self.bot.foe_data['them'] = ['defect', 'defect']
        actual = [self.bot.get_move()]
        self.bot.foe_data['them'].append('cooperate')
        actual.append(self.bot.get_move())
        self.assertEqual(['defect', 'cooperate'], actual)


class TwoTitTatTest(unittest.TestCase):
    """Test of the Two Tits for Tat bot. (unittest.TestCase)"""

    def setUp(self):
        self.human = unitility.AutoBot()
        self.game = prisoner.PrisonersDilemma(self.human, '2tit-tat')
        self.bot = [player for player in self.game.players if player != self.human][0]
        self.bot.set_up()
        self.bot.foe_data = self.bot.data[self.human]

    def testCC(self):
        """Test two tit for tat's response to reward."""
        self.bot.foe_data['me'] = ['cooperate']
        self.bot.foe_data['them'] = ['cooperate']
        self.assertEqual('cooperate', self.bot.get_move())

    def testCD(self):
        """Test two tit for tat's response to sucker bet."""
        self.bot.foe_data['me'] = ['cooperate']
        self.bot.foe_data['them'] = ['defect']
        self.assertEqual('defect', self.bot.get_move())

    def testDC(self):
        """Test two tit for tat's response to temptation."""
        self.bot.foe_data['me'] = ['defect']
        self.bot.foe_data['them'] = ['cooperate']
        self.assertEqual('cooperate', self.bot.get_move())

    def testDD(self):
        """Test two tit for tat's response to punishment."""
        self.bot.foe_data['me'] = ['defect']
        self.bot.foe_data['them'] = ['defect']
        self.assertEqual('defect', self.bot.get_move())

    def testInitial(self):
        """Test grim's initial move."""
        self.assertEqual('cooperate', self.bot.get_move())

    def testTwoTats(self):
        """Test two tit for tat's response to two defections."""
        self.bot.foe_data['me'] = ['cooperate', 'cooperate']
        self.bot.foe_data['them'] = ['defect', 'defect']
        self.assertEqual('defect', self.bot.get_move())

    def testTwoTits(self):
        """Test two tit for tat's second respons to getting triggered."""
        self.bot.foe_data['me'] = ['cooperate', 'cooperate']
        self.bot.foe_data['them'] = ['defect', 'defect']
        actual = [self.bot.get_move()]
        self.bot.foe_data['them'].append('cooperate')
        actual.append(self.bot.get_move())
        self.assertEqual(['defect', 'defect'], actual)



if __name__ == '__main__':
    unittest.main()
