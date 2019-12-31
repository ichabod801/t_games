"""
gin_rummy_test.py

Unit testing of gin_rummy_game.py

Classes:
GinBotSortTest: Tests of sorting a hand by the bot. (unittest.TestCase)
ParseMeldTest: Test parsing melds by input by a player. (unittest.TestCase)
SpreadTest: Tests of spreading cards at the end of a hand. (unittest.TestCase)
ValidateMeldTest: Test of validating melds. (unittest.TestCase)
"""


import unittest

from t_games import cards
from t_games.card_games import gin_rummy_game as gin
from t_games.t_tests import unitility


BotTest = unitility.bot_test(gin.GinRummy, [gin.GinBot, gin.TrackingBot], 10, [2])


class GinBotSortTest(unittest.TestCase):
    """Tests of sorting a hand by the bot. (unittest.TestCase)"""
    # Note that order is massaged in the check values for these tests, because it doesn't matter.

    def setHand(self, text):
        """
        Set up the bot's hand for a test. (None)

        Parameters:
        text: A space delimited list of cards to put in the bot's hand. (str)
        """
        self.bot.hand.cards = card_text(text)

    def setUp(self):
        self.maxDiff = None
        self.game = gin.GinRummy(unitility.AutoBot(), 'easy')
        self.game.set_up()
        self.bot = self.game.players[1]
        self.bot.set_up()
        self.bot.debug = False
        self.check = {'attacks': [], 'full-run': [], 'full-set': [], 'part-run': [],
            'part-set': [], 'deadwood': []}

    def testAllCategories(self):
        """Test a hand with something in each tracking list."""
        self.setHand('2c 3c 4c ad ah as 6d 7d 5h 5s')
        self.check['full-run'] = [self.bot.hand.cards[:3]]
        self.check['full-set'] = [self.bot.hand.cards[3:6]]
        self.check['part-run'] = [self.bot.hand.cards[6:8]]
        self.check['part-set'] = [self.bot.hand.cards[8:]]
        self.bot.sort_hand()
        self.assertEqual(self.check, self.bot.tracking)

    def testDoubleBreak(self):
        """Test breaking a run only once."""
        self.setHand('as 2s 3s 4s ac ad 4c 4d 5h 6s')
        self.check['full-set'] = [card_text('4c 4d 4s')]
        self.check['full-run'] = [card_text('as 2s 3s')]
        self.check['part-set'] = [card_text('ac ad')]
        self.check['deadwood'] = card_text('5h 6s')
        self.bot.sort_hand()
        self.assertEqual(self.check, self.bot.tracking)

    def testFullRun(self):
        """Test tracking a full run."""
        self.setHand('ac 2c 3c 4d 5h 6s 7c 8d 9h ts')
        self.check['full-run'] = [self.bot.hand.cards[:3]]
        self.check['deadwood'] = self.bot.hand.cards[3:]
        self.check['deadwood'].sort(key = lambda card: (card.suit, card.rank_num))
        self.bot.sort_hand()
        self.assertEqual(self.check, self.bot.tracking)

    def testFullSet(self):
        """Test tracking a full set."""
        self.setHand('jc jd jh qs kc ad 2h 3s 4c 5d')
        self.check['full-set'] = [self.bot.hand.cards[:3]]
        self.check['deadwood'] = self.bot.hand.cards[3:]
        self.check['deadwood'].sort(key = lambda card: (card.suit, card.rank_num))
        self.bot.sort_hand()
        self.assertEqual(self.check, self.bot.tracking)

    def testGin(self):
        """Test tracking gin."""
        self.setHand('4h 5h 6h 7h, qc qd qh kc kd kh')
        self.check['full-run'] = [self.bot.hand.cards[:4]]
        self.check['full-set'] = [self.bot.hand.cards[4:7], self.bot.hand.cards[7:]]
        self.bot.sort_hand()
        self.assertEqual(self.check, self.bot.tracking)

    def testPartialRun(self):
        """Test tracking a partial run."""
        self.setHand('6h 7h 8s 9c td jh qs kc ad 2h')
        self.check['part-run'] = [self.bot.hand.cards[:2]]
        self.check['deadwood'] = self.bot.hand.cards[2:]
        self.check['deadwood'].sort(key = lambda card: (card.suit, card.rank_num))
        self.bot.sort_hand()
        self.assertEqual(self.check, self.bot.tracking)

    def testPartialSet(self):
        """Test tracking a partial set."""
        self.setHand('3c 3s 4d 5h 6s 7c 8d 9h ts jc')
        self.check['part-set'] = [self.bot.hand.cards[:2]]
        self.check['deadwood'] = self.bot.hand.cards[2:]
        self.check['deadwood'].sort(key = lambda card: (card.suit, card.rank_num))
        self.bot.sort_hand()
        self.assertEqual(self.check, self.bot.tracking)

    def testRunFiveVsSetMiddle(self):
        """Test a set intersecting the middle of a five-card run."""
        self.setHand('6d 7d 8d 8h 8s 9d td jc jd js')
        self.bot.debug = True
        self.check['full-run'] = [self.bot.hand.cards[:3] + self.bot.hand.cards[5:7]]
        self.check['full-set'] = [card_text('jc js jd')]
        self.check['part-set'] = [self.bot.hand.cards[3:5]]
        self.bot.sort_hand()
        self.assertEqual(self.check, self.bot.tracking)

    def testRunFourVsSetHigh(self):
        """Test a set intersecting the high end of a four-card run."""
        self.setHand('5c 6c 7c 8d 8h 8c 9s tc jd qh')
        self.check['full-run'] = [self.bot.hand.cards[:3]]
        self.check['full-set'] = [self.bot.hand.cards[3:6]]
        self.check['deadwood'] = self.bot.hand.cards[6:]
        self.check['deadwood'].sort(key = lambda card: (card.suit, card.rank_num))
        self.bot.sort_hand()
        self.assertEqual(self.check, self.bot.tracking)

    def testRunFourVsSetLow(self):
        """Test a set intersecting the low end of a four-card run."""
        self.setHand('ts js qs kc kd ks ah 2s 3c 4d')
        self.check['full-run'] = [self.bot.hand.cards[:3]]
        self.check['full-set'] = [self.bot.hand.cards[3:6]]
        self.check['deadwood'] = self.bot.hand.cards[6:]
        self.check['deadwood'].sort(key = lambda card: (card.suit, card.rank_num))
        self.bot.sort_hand()
        self.assertEqual(self.check, self.bot.tracking)

    def testRunVsSetHigh(self):
        """Test a set intersecting the high end of a run."""
        self.setHand('3c 4c 5d 5h 5c 6s 7c 8d 9h ts')
        self.check['part-run'] = [self.bot.hand.cards[:2]]
        self.check['full-set'] = [self.bot.hand.cards[2:5]]
        self.check['deadwood'] = self.bot.hand.cards[5:]
        self.check['deadwood'].sort(key = lambda card: (card.suit, card.rank_num))
        self.bot.sort_hand()
        self.assertEqual(self.check, self.bot.tracking)

    def testRunVsSetLow(self):
        """Test a set intersecting the low end of a run."""
        self.setHand('8c 9c tc 8d 8h js qc kd ah 2s')
        self.check['full-run'] = [self.bot.hand.cards[:3]]
        self.check['part-set'] = [self.bot.hand.cards[3:5]]
        self.check['deadwood'] = self.bot.hand.cards[5:]
        self.check['deadwood'].sort(key = lambda card: (card.suit, card.rank_num))
        self.bot.sort_hand()
        self.assertEqual(self.check, self.bot.tracking)

    def testRunVsSetMiddle(self):
        """Test a set intersecting the middle of a run."""
        self.setHand('jc qc kc qd qh as 2c 3d 4h 5s')
        self.check['full-run'] = [self.bot.hand.cards[:3]]
        self.check['part-set'] = [self.bot.hand.cards[3:5]]
        self.check['deadwood'] = self.bot.hand.cards[5:]
        self.check['deadwood'].sort(key = lambda card: (card.suit, card.rank_num))
        self.bot.sort_hand()
        self.assertEqual(self.check, self.bot.tracking)

    def testSetFourVsTwoRun(self):
        """Test a set intersecting with two runs."""
        self.setHand('5c 6c 7c 5d 6d 7h 7s 7d 2s 3h')
        self.check['full-run'] = [self.bot.hand.cards[:3]]
        self.check['part-run'] = [self.bot.hand.cards[3:5]]
        self.check['full-set'] = [self.bot.hand.cards[5:8]]
        self.check['deadwood'] = list(reversed(self.bot.hand.cards[8:]))
        self.bot.sort_hand()
        self.assertEqual(self.check, self.bot.tracking)


class ParseMeldTest(unittest.TestCase):
    """Test parsing melds by input by a player. (unittest.TestCase)"""

    def setUp(self):
        self.human = unitility.AutoBot()
        self.game = gin.GinRummy(self.human, 'none')
        self.game.set_up()

    def testBasicRun(self):
        """Test parsing a basic run."""
        hand = [cards.Card(*text) for text in ('AS', '2S', 'KC', 'AC', '6D', '6H', 'JS', '3S')]
        self.assertEqual(['as', '2s', '3s'], self.game.parse_meld('as 2s 3s', hand))

    def testBasicSet(self):
        """Test parsing a basic set."""
        hand = [cards.Card(*text) for text in ('AS', '2S', 'KC', 'AC', '6D', '6H', 'JS', '6S')]
        self.assertEqual(['6d', '6h', '6s'], self.game.parse_meld('6D 6H 6S', hand))

    def testInvalidMeld(self):
        """Test parsing a basic set."""
        hand = [cards.Card(*text) for text in ('AS', '2S', 'KC', 'AC', '6D', '6H', 'JS', '6S')]
        self.assertEqual(['6d', '6h', '7h'], self.game.parse_meld('6D 6H 7h', hand))

    def testShortRun(self):
        """Test parsing a shorthand run."""
        hand = [cards.Card(*text) for text in ('AS', '2S', 'KS', 'AC', '6D', '6H', 'JS', 'QS')]
        self.assertEqual(['JS', 'QS', 'KS'], self.game.parse_meld('js-k', hand))

    def testShortRunDoubleSuit(self):
        """Test parsing a shorthand run with suit specified at start and end."""
        hand = [cards.Card(*text) for text in ('AS', '2S', 'KS', 'AC', '6D', '6H', '4H', '5H')]
        self.assertEqual(['4H', '5H', '6H'], self.game.parse_meld('4h-6h', hand))

    def testShortRunEndSuit(self):
        """Test parsing a shorthand run with the suit at the end."""
        hand = [cards.Card(*text) for text in ('AS', '2S', 'KS', 'AC', '6D', '6H', '7D', '8D')]
        self.assertEqual(['6D', '7D', '8D'], self.game.parse_meld('6-8D', hand))

    def testShortRunErrorRank(self):
        """Test parsing a shorthand run with a band rank."""
        hand = [cards.Card(*text) for text in ('AS', '2S', 'KS', 'AC', '6D', '6H', '7D', '8D')]
        self.assertEqual(['error'], self.game.parse_meld('6-FD', hand))

    def testShortRunErrorSuitless(self):
        """Test parsing a shorthand run with a bad suit."""
        hand = [cards.Card(*text) for text in ('AS', '2S', 'KS', 'AC', '6D', '6H', '7D', '8D')]
        self.assertEqual(['error'], self.game.parse_meld('6-8', hand))

    def testShortRunNumAlpha(self):
        """Test parsing a shorthand run crossing the 9/T line."""
        hand = [cards.Card(*text) for text in ('AS', '2S', 'TS', 'AC', '6D', '6H', 'JS', '9S')]
        self.assertEqual(['9S', 'TS', 'JS'], self.game.parse_meld('9s-j', hand))

    def testShortRunSpaceAfter(self):
        """Test parsing a shorthand run with a space after the dash."""
        hand = [cards.Card(*text) for text in ('AS', '2S', 'KS', 'AC', '6D', '6H', 'JS', 'QS')]
        self.assertEqual(['JS', 'QS', 'KS'], self.game.parse_meld('js- k', hand))

    def testShortRunSpaceBefore(self):
        """Test parsing a shorthand run with a space before the dash."""
        hand = [cards.Card(*text) for text in ('AS', '2S', 'KS', 'AC', '6D', '6H', 'JS', 'QS')]
        self.assertEqual(['JS', 'QS', 'KS'], self.game.parse_meld('js -k', hand))

    def testShortRunSpaceBoth(self):
        """Test parsing a shorthand run with a space before and after the dash."""
        hand = [cards.Card(*text) for text in ('AS', '2S', 'KS', 'AC', '6D', '6H', 'JS', 'QS')]
        self.assertEqual(['JS', 'QS', 'KS'], self.game.parse_meld('js - k', hand))

    def testShortSet(self):
        """Test parsing a shorthand set."""
        hand = [cards.Card(*text) for text in ('AS', '2S', 'KS', 'AC', '6D', 'AH', 'JS', 'QS')]
        self.assertEqual(['AS', 'AC', 'AH'], self.game.parse_meld('a', hand))

    def testShortSetErrorBad(self):
        """Test parsing a shorthand set with a bad rank."""
        hand = [cards.Card(*text) for text in ('AS', '2S', 'KS', 'AC', '6D', 'AH', 'JS', 'QS')]
        self.assertEqual(['error'], self.game.parse_meld('i', hand))

    def testShortSetErrorMissing(self):
        """Test parsing a shorthand set with a rank not in hand."""
        hand = [cards.Card(*text) for text in ('AS', '2S', 'KS', 'AC', '6D', 'AH', 'JS', 'QS')]
        self.assertEqual([], self.game.parse_meld('8', hand))

    def testShortSetNumber(self):
        """Test parsing a shorthand set using a number rank."""
        hand = [cards.Card(*text) for text in ('AS', '2S', 'KS', 'AC', '6D', '6H', '6S', 'QS')]
        self.assertEqual(['6D', '6H', '6S'], self.game.parse_meld('6', hand))


class SpreadTest(unittest.TestCase):
    """Tests of spreading cards at the end of a hand. (unittest.TestCase)"""

    def setHand(self, text):
        """
        Set up a hand of cards for a test. (None)

        Parameters:
        text: A space delimited list of cards. (str)
        """
        self.game.hands[self.human.name].cards = card_text(text)

    def setUp(self):
        self.human = unitility.AutoBot()
        self.game = gin.GinRummy(self.human, 'none')
        self.game.set_up()

    def testBadMeld(self):
        """Test spreading with a bad meld specification."""
        self.setHand('qh qs qc ad 2d 3d 4h 4s 4c 5d')
        self.human.replies = ['q', 'a-3', 'ad-3', '4', '']
        scoring_sets = [card_text(spread) for spread in ('qh qs qc', 'ad 2d 3d', '4h 4s 4c')]
        unspread = cards.Hand(self.game.deck)
        unspread.cards = [cards.Card(*'5D')]
        spread = cards.Hand(self.game.deck)
        spread.cards = self.game.hands[self.human.name].cards[:-1]
        self.assertEqual((scoring_sets, unspread, spread), self.game.spread(self.human))
        self.assertEqual(["\nInvalid meld specification: 'a-3'.\n"], self.human.errors)

    def testBasic(self):
        """Test spreading some basic runs and sets."""
        self.setHand('ac 2c 3c 4d 4h 4s 5c 6c 7c 8d')
        self.human.replies = ['ac 2c 3c', '4d 4h 4s', '5c 6c 7c', '']
        spreads = [card_text(spread) for spread in self.human.replies[:-1]]
        deadwood = [cards.Card(*'8D')]
        self.assertEqual((spreads, deadwood), self.game.spread(self.human))

    def testCancel(self):
        """Test resetting during spreading."""
        self.setHand('qh qs qc kd ah 2s 3c 4d 5h 6s')
        self.human.replies = ['q', 'cancel']
        self.game.player_index = 0
        self.assertEqual(([], card_text('qh qs qc kd ah 2s 3c 4d 5h 6s')), self.game.spread(self.human))

    def testCancelFail(self):
        """Test resetting during spreading."""
        self.setHand('7c 8c 9c td jh qs kc ad 2h 3s')
        self.human.replies = ['7c-9', 'cancel', '']
        self.game.player_index = 1
        self.game.players.append(unitility.AutoBot())
        self.game.players[-1].name = 'Not {}'.format(self.human.name)
        spreads = [card_text('7c 8c 9c')]
        deadwood = card_text('td jh qs kc ad 2h 3s')
        self.assertEqual((spreads, deadwood), self.game.spread(self.human))
        self.assertEqual(['\nThe defending player may not cancel.\n'], self.human.errors)

    def testGin(self):
        """Test spreading a basic gin hand."""
        self.setHand('9h 9s 9c 9d th jh qh ks kc kd')
        self.human.replies = ['9h 9s 9c 9d', 'th jh qh', 'ks kc kd', '']
        spreads = [card_text(spread) for spread in self.human.replies[:-1]]
        deadwood = []
        self.assertEqual((spreads, deadwood), self.game.spread(self.human))

    def testInvalid(self):
        """Test spreading an invalid meld."""
        self.setHand('kh ks kc ad 2d 3d 4h 5s 6s 7c')
        self.human.replies = ['kh ks kc', 'ad 2d 3d', '4h 5s 6s', '']
        spreads = [card_text(spread) for spread in self.human.replies[:2]]
        deadwood = card_text('4h 5s 6s 7c')
        self.assertEqual((spreads, deadwood), self.game.spread(self.human))
        self.assertEqual(['That is not a valid meld.\n'], self.human.errors)

    def testLayoffHigh(self):
        """Test laying off onto the high end of a run."""
        self.setHand('8d 9d td jh js jd qh qs qd kc')
        self.human.replies = ['8d 9d td', 'jh js jd', 'qh qs qd', 'kc', '']
        spreads = [card_text(spread) for spread in self.human.replies[:-1]]
        deadwood = []
        attack = [card_text('tc jc qc')]
        actual = self.game.spread(self.human, attack)
        self.assertEqual((spreads, deadwood), actual)

    def testLayoffLow(self):
        """Test laying off onto the high end of a run."""
        self.setHand('ad ah as 2d 3d 4d 5h 5s 5c 6d')
        self.human.replies = ['ad ah as', '2d 3d 4d', '5h 5s 5c', '6d', '']
        spreads = [card_text(spread) for spread in self.human.replies[:-1]]
        deadwood = []
        attack = [card_text('7d 8d 9d')]
        actual = self.game.spread(self.human, attack)
        self.assertEqual((spreads, deadwood), actual)

    def testLayoffSet(self):
        """Test laying off onto a set."""
        self.setHand('7h 8h 9h ts js qs kc kd kh as')
        self.human.replies = ['7h 8h 9h', 'ts js qs', 'kc kd kh', 'as', '']
        spreads = [card_text(spread) for spread in self.human.replies[:-1]]
        deadwood = []
        attack = [card_text('ac ad ah')]
        actual = self.game.spread(self.human, attack)
        self.assertEqual((spreads, deadwood), actual)

    def testLayoffTwo(self):
        """Test laying off two cards onto a run."""
        self.setHand('2c 3c 4c 5d 5h 5s 6c 7c 8d 9h')
        self.human.replies = ['2c 3c 4c', '5d 5h 5s', '6c 7c', '']
        spreads = [card_text(spread) for spread in self.human.replies[:-1]]
        deadwood = card_text('8d 9h')
        attack = [card_text('8c 9c tc')]
        self.assertEqual((spreads, deadwood), self.game.spread(self.human, attack))

    def testLayoffTwoSplit(self):
        """Test laying off two cards onto a run one at a time."""
        self.setHand('ts js qs kc kd kh 4h 5h ad 2c')
        self.human.replies = ['ts js qs', 'kc kd kh', '4h', '5h', '']
        spreads = [card_text(spread) for spread in self.human.replies[:-1]]
        deadwood = card_text('ad 2c')
        attack = [card_text('ah 2h 3h')]
        self.assertEqual((spreads, deadwood), self.game.spread(self.human, attack))

    def testMultiDead(self):
        """Test spreading with multiple dead cards."""
        self.setHand('4c 4d 4h 5s 6s 7s 8h 9s tc jd')
        self.human.replies = ['4', '5s-7s', '']
        spreads = [card_text(spread) for spread in ('4c 4d 4h', '5s 6s 7s')]
        deadwood = card_text('8h 9s tc jd')
        self.assertEqual((spreads, deadwood), self.game.spread(self.human))

    def testNoCards(self):
        """Test spreading without the cards in hand."""
        self.setHand('6h 7h 8h ks kd kh 9c tc jc qd')
        self.human.replies = ['6h-8', 'k', '9h-j', '9c-j', '']
        spreads = [card_text(spread) for spread in ('6h 7h 8h', 'ks kd kh', '9c tc jc')]
        deadwood = [cards.Card(*'QD')]
        self.assertEqual((spreads, deadwood), self.game.spread(self.human))
        self.assertEqual(["You do not have all of those cards.\n"], self.human.errors)

    def testReset(self):
        """Test resetting during spreading."""
        self.setHand('7h 7s 7c 7d 8d 9d th ts tc jd')
        self.human.replies = ['7', 'reset', '7h 7s 7c', '7d 8d 9d', 'th ts tc', '']
        spreads = [card_text(spread) for spread in self.human.replies[2:-1]]
        deadwood = [cards.Card(*'JD')]
        self.assertEqual((spreads, deadwood), self.game.spread(self.human))

    def testShorthand(self):
        """Test spreading using shorthand."""
        self.setHand('ah as ac 2d 3d 4d 5h 5s 5c 6d')
        self.human.replies = ['a', '2d-4', '5', '']
        spreads = [card_text(spread) for spread in ('ah as ac', '2d 3d 4d', '5h 5s 5c')]
        deadwood = [cards.Card(*'6D')]
        self.assertEqual((spreads, deadwood), self.game.spread(self.human))


class ValidateMeldTest(unittest.TestCase):
    """Test of validating melds entered by players. (unittest.TestCase)"""

    def setUp(self):
        self.human = unitility.AutoBot()
        self.game = gin.GinRummy(self.human, 'none')
        self.game.set_up()

    def testAceKingFail(self):
        """Test an ace-king run without the high-low option."""
        self.assertFalse(self.game.validate_meld(['qs', 'ks', 'as']))

    def testAceKingPass(self):
        """Test an ace-king run without the high-low option."""
        self.game = gin.GinRummy(self.human, 'high-low')
        self.game.set_up()
        self.assertTrue(self.game.validate_meld(['QC', 'KC', 'AC']))

    def testBadRank(self):
        """Test a rank that isn't in the deck."""
        self.assertFalse(self.game.validate_meld(['2d', '3d', 'fd']))

    def testBasicRun(self):
        """Test a basic run."""
        self.assertTrue(self.game.validate_meld(['2s', '3s', '4s']))

    def testBasicRunAlpha(self):
        """Test a basic run with alphabetical ranks."""
        self.assertTrue(self.game.validate_meld(['js', 'qs', 'ks']))

    def testBasicRunNumAlpha(self):
        """Test a basic run crossing the 9/T ranks."""
        self.assertTrue(self.game.validate_meld(['8C', '9C', 'TC']))

    def testBasicSet(self):
        """Test a basic run."""
        self.assertTrue(self.game.validate_meld(['5C', '5D', '5H']))

    def testBrokenRun(self):
        """Test a broken run."""
        self.assertFalse(self.game.validate_meld(['3H', '5H', '6H']))

    def testEightRun(self):
        """Test a four card run."""
        self.assertTrue(self.game.validate_meld(['ah', '2h', '3h', '4h', '5h', '6h', '7h', '8h']))

    def testFourRun(self):
        """Test a four card run."""
        self.assertTrue(self.game.validate_meld(['6d', '7d', '8d', '9d']))

    def testFourSet(self):
        """Test a four card set."""
        self.assertTrue(self.game.validate_meld(['AC', 'AD', 'AS', 'AH']))

    def testHinge(self):
        """Test three cards making a partial set and a partial run."""
        self.assertFalse(self.game.validate_meld(['ac', 'ad', '2d']))

    def testMixedCase(self):
        """Test a run with mixed case."""
        self.assertTrue(self.game.validate_meld(['TC', 'JC', 'QC', 'kc']))

    def testShortRun(self):
        """Test a two card run."""
        self.assertTrue(self.game.validate_meld(['9C', 'TC']))

    def testShortSet(self):
        """Test a two card set."""
        self.assertTrue(self.game.validate_meld(['jd', 'jh']))

    def testSingleton(self):
        """Test one card."""
        self.assertTrue(self.game.validate_meld(['QS']))


def card_text(text):
    """
    Create a list of cards from a string. (list of cards.Card)

    Parameters:
    text: A space delimited list of cards. (str)
    """
    return [cards.Card(*card_text.upper()) for card_text in text.split()]


if __name__ == '__main__':
    unittest.main()