"""
cribbage_game.py

A game of Cribbage.

To Do (not in order)
    options:
        auction
        cut throat
        solo
        partnership
        solitaire?
        match play
            default free play
            official
            long-match
            triple-skunk

Constants:
Credits: The credits for Cribbage. (str)

Classes:
Cribbage: A game of Cribbage. (game.Game)
CribBot: A bot for playing Cribbage. (player.Bot)
CribCard: A card for a game of Cribbage. (cards.Card)
"""


import collections
import itertools
import random


import tgames.cards as cards
import tgames.game as game
import tgames.player as player
import tgames.utility as utility


CREDITS = """
Game Design: John Suckling
Game Programming: Craig "Ichabod" O'Brien
"""

ENTER_TEXT = 'Please press enter to continue: '

RULES = """
Each player is dealt six cards, five in a three or four player game. Each 
player then discards down to four cards. Discarded cards go into the Crib,
which is an extra hand that is scored by the dealer. In a three player game
a fourth card is dealt to the crib from the deck.

After discarding, a starter card is revealed. If it is a jack, the dealer
gets two points (for his heels). Then players play cards starting with the 
player to the left of the dealer. The sequence of played cards can be used to 
score points. If the total reaches 15 (aces count one, face cards count 10), 
the player scores 2 points. If a pair is made with the previous card, 2 
points are scored. Note that pairs are counted separately, so three of the 
same rank in a row counts as three pairs, and four of the same rank in a row 
counts as six pairs. If a straight of n cards is made with the last n cards, 
n points are scored.

The total of the cards played cannot go over 31. If a player can't play a card
that keeps the total 31 or under, they pass by saying 'go.' If everyone 
passes, the last player to play a card scores a point. If the total reaches
31, the last player to play a card scores 2 points. Once play is done the
sequence starts over again with a total of 0.

Once everyone has played all of their cards, the players' hands are scored,
with the addition of the starter card. Every combination of cards totalling
15 scores 2 points. Every pair scores 2 points, with pairs counted as above.
Straights count for the number of the cards in the straight. If you have a
pair in the straight, the two straights both score (or all three if you have
three of a kind in the straight, or all four if you have two pair in the
straight). A flush not counting the starter card counts four points. If the
starter card is the same suit as the four in the hand you score five points.
Finally, a jack of the same suit as the starter card (his nobs) scores one
point.

The role of dealer then passes to the left, and a new hand and starter are
dealt. This continues until someone reaches 121 points. Note that the dealer's
hand is scored last, to offset the advantage of the crib in tight games.

Options:
auto-go: Don't prompt players who must go.
auto-score: Don't prompt the user after a player scores.
cards=: The number of cards dealt (defaults = 6).
discards=: The number of cards discarded (defaults = 2).
double-skunk=: The score needed to avoid a double skunk (default = 0).
fast: Equivalent to auto-go auto-score no-cut no-pick.
five-card (5-card): equivalent to one-go cards=5 discards=1 target-score=61
    skunk=31 last=3
last=: The initial score of the last player to play (default = 0).
match=: The number of games to play in a match. (default = 1).
    Match results only make sense for two player games.
match-scores=: How to score wins/skunks/double skunks
    acc: 2/3/3
    long: 3/4/4
    free: 1/2/3
    four: 1/2/4
    or you can enter three numbers separated by slashes.
    defaults to acc (American Cribbage Congress).
n-bots: The number of bots to play against.
no-cut: Skip cutting the deck before the deal.
no-pick: Skip picking a card to see who deals first.
one-go: There is only one round of play, that is, only one go.
seven-card (7-card): equivalent to cards=7 target-score=181 skunk=151
skunk=: The score needed to avoid a skunk (defualt = 91, only in match play).
target-score= (win=): The score needed to win (default = 121).
"""


class Cribbage(game.Game):
    """
    A game of Cribbage. (game.Game)

    Attributes:
    cards_played: The cards played so far this round. (str)
    deck: The deck of cards used in the game. (cards.Deck)
    hands: The player's hands in the game. (dict of str: cards.Hand)
    in_play: The cards each player has played. (dict of str: cards.Hand)
    starter: The starter card. (cards.Card)
    """

    aka = ['Crib']
    categories = ['Card Games', 'Matching Game']
    credits = CREDITS
    name = 'Cribbage'
    num_options = 8
    rules = RULES

    def __str__(self):
        """Human readable text representation. (str)"""
        lines = ['\nScores\n------\n']
        for player in self.players:
            lines.append('{}: {}'.format(player.name, self.scores[player.name]))
        lines.append('\nRunning Total: {}'.format(self.card_total))
        player = self.players[self.player_index]
        hand = self.hands[player.name]
        lines.append('\nCards in Hand: {}'.format(hand.show_player()))
        if self.phase != 'discard':
            lines.append('\nStarter Card: {}.'.format(self.starter))
            lines.append('\nCards played: {}\n'.format(self.in_play['Play Sequence']))
        return '\n'.join(lines)

    def deal(self):
        """Deal the cards. (None)"""
        # Discard and shuffle.
        for hand in self.hands.values():
            hand.discard()
        self.in_play['Play Sequence'].cards = []
        for hand in self.in_play.values():
            hand.discard()
        self.deck.shuffle()
        # Find the dealer and the player on their left.
        self.dealer_index = (self.dealer_index + 1) % len(self.players)
        dealer = self.players[self.dealer_index]
        self.player_index = self.dealer_index
        print('\nThe current dealer is {}.'.format(dealer.name))
        # Score the last bonus.
        if self.last and max(self.scores.values()) == 0:
            last_index = (self.dealer_index - 1) % len(self.players)
            last_name = self.players[last_index].name
            self.scores[last_name] += self.last
            self.human.tell('{} scores {} points for being last.'.format(last_name, self.last))
            if not self.auto_score:
                self.human.ask(ENTER_TEXT)
        # Cut the deck.
        if not self.no_cut:
            left = (self.dealer_index + 1) % len(self.players)
            query = 'Enter a number to cut the deck: '
            cut_index = self.players[left].ask_int(query, cmd = False, default = 0)
            self.deck.cut(cut_index)
        # Deal the cards
        for card in range(self.cards):
            for player in self.players:
                self.hands[player.name].draw()
        for card in range(4 - len(self.players) * self.discards):
            self.hands['The Crib'].draw()
        # Dummy starter card.
        self.starter = CribCard('X', 'S')
        # Reset the tracking variables.
        self.phase = 'discard'

    def game_over(self):
        """Check for the end of the game. (None)"""
        if max(self.scores.values()) >= self.target_score:
            # Determine the winner.
            scores = [(score, name) for name, score in self.scores.items()]
            scores.sort(reverse = True)
            self.human.tell('{1} wins with {0} points.'.format(*scores[0]))
            # Check for skunk.
            game_score = self.match_scores[0]
            if scores[1][0] < self.skunk:
                games_score = self.match_scores[1]
                self.human.tell('{1} got skunked with {0} points.'.format(*scores[1]))
            elif scores[1][0] < self.double_skunk:
                games_score = self.match_scores[1]
                self.human.tell('{1} got double skunked with {0} points.'.format(*scores[1]))
            # Calcualte win/loss/draw stats.
            human_score = self.scores[self.human.name]
            for score, name in scores:
                if name == self.human.name:
                    continue
                elif score < human_score:
                    self.win_loss_draw[0] += game_score
                elif score > human_score:
                    self.win_loss_draw[1] += game_score
                elif score == human_score:
                    self.win_loss_draw[2] += game_score
            return max(self.win_loss_draw) >= self.match
        else:
            return False

    def handle_options(self):
        """Handle the game option settings. (None)"""
        super(Cribbage, self).handle_options()
        # Set up the players (bots).
        self.players = [self.human]
        taken_names = [self.human.name]
        for bot in range(self.n_bots):
            self.players.append(CribBot(taken_names))
            taken_names.append(self.players[-1].name)
        # Set up match play.
        if self.match > 1:
            self.flags |= 256
            if self.match_scores == 'acc':
                self.match_scores = (2, 3, 3)
            elif self.match_scores == 'long':
                self.match_scores = (3, 4, 4)
            elif self.match_scores == 'free':
                self.match_scores = (1, 2, 3)
            elif self.match_scores == 'four':
                self.match_scores = (1, 2, 4)
            else:
                try:
                    self.match_scores = [int(score) for score in self.match_scores.split('/')]
                    check = self.match_scores[2]
                except (ValueError, IndexError):
                    warning = 'Invalid setting for match-scores option: {!r}.'
                    self.human.error(warning.format(self.match_scores))
                    self.match_scores = (2, 3, 3)
        else:
            self.match = 1
            self.match_scores = (1, 1, 1)

    def player_action(self, player):
        """
        Allow the player to do something.

        Parameters:
        player: The current player. (player.Player)
        """
        if self.phase == 'deal':
            self.deal()
            return False
        player.tell(self)
        if self.phase == 'discard':
            return self.player_discards(player)
        elif self.phase == 'play':
            return self.player_play(player)

    def player_discards(self, player):
        """
        Allow the player to discard cards.

        Parameters:
        player: The current player. (player.Player)
        """
        discard_word, s = [('', ''), (' two', 's')][self.discards != 1]
        query = 'Which{} card{} would you like to discard to the crib, {}? '
        answer = player.ask(query.format(discard_word, s, player.name))
        discards = cards.Card.card_re.findall(answer)
        if not discards:
            return self.handle_cmd(answer)
        elif len(discards) != self.discards:
            player.error('You must discard {} card{}.'.format(utility.number_word(self.discards), s))
            return True
        elif not all(card in self.hands[player.name] for card in discards):
            player.error('You do not have all of those cards in your hand.')
            return True
        else:
            for card in discards:
                self.hands[player.name].shift(card, self.hands['The Crib'])
            if len(self.hands['The Crib']) == 4:
                self.phase = 'play'
                self.starter = self.deck.deal(up = True)
                # Check for heels.
                if self.starter.rank == 'J':
                    self.human.tell('The dealer got their heels.')
                    if not self.auto_score:
                        self.human.ask(ENTER_TEXT)
                    dealer = self.players[self.dealer_index]
                    self.scores[dealer.name] += 2
                    if self.scores[dealer.name] >= self.target_score:
                        self.force_win
                        return False
            return False

    def player_play(self, player):
        """
        Allow the player to play a card.

        Parameters:
        player: The current player. (player.Player)
        """
        hand = self.hands[player.name]
        in_play = self.in_play[player.name]
        playable = [card for card in hand if card + self.card_total <= 31]
        if not playable:
            player.tell('You have no playable cards and must go.')
            if not self.auto_score:
                player.ask(ENTER_TEXT)
            self.go_count += 1
            if self.go_count == len(self.players):
                self.human.tell('\nEveryone has passed.')
                self.scores[player.name] += 1
                self.human.tell('{} scores 1 for the go.'.format(player.name))
                if not self.auto_score:
                    self.human.ask(ENTER_TEXT)
                self.reset()
            return False
        answer = player.ask('Which card would you like to play, {}? '.format(player.name))
        card = CribCard.card_re.match(answer)
        if card:
            card = CribCard(*answer[:2].upper())
            if card not in hand:
                player.error('You do not have that card in your hand.')
                return True
            if card + self.card_total > 31:
                player.error('That card would put the running total over 31.')
                return True
            else:
                hand.shift(card, in_play)
                self.in_play['Play Sequence'].cards.append(in_play.cards[-1])
                self.card_total += card
                self.score_sequence(player)
                self.go_count = 0
                if self.card_total == 31:
                    self.human.tell('\nThe count has reached 31.')
                    self.scores[player.name] += 2
                    self.human.tell('{} scores 2 points for reaching 31.'.format(player.name))
                    if not self.auto_score:
                        self.human.ask(ENTER_TEXT)
                    self.reset()
                return False
        else:
            return self.handle_cmd(answer)

    def reset(self):
        """Reset the game after a pegging round. (None)"""
        self.card_total = 0
        self.go_count = 0
        self.in_play['Play Sequence'].cards = []
        # Player names are used to get hands to avoid checking the crib for cards.
        if (not any(self.hands[player.name] for player in self.players)) or self.one_go:
            if not self.score_hands():
                self.deal() # Only deal if no one wins.

    def score_fifteens(self, cards):
        """
        Score any sets totalling to fifteen in the given cards. (int)

        Parameters:
        cards: The cards to score. (list of CribCard)
        """
        fifteens = 0
        for size in range(2, 6):
            for sub_cards in itertools.combinations(cards, size):
                if sum(sub_cards) == 15:
                    fifteens += 1
        return fifteens

    def score_flush(self, cards):
        """
        Score any flushes in the given cards. (int)

        Parameters:
        cards: The cards to score. (list of CribCard)
        """
        score = 0
        suits = set([card.suit for card in cards])
        if len(suits) == 1:
            if self.starter.suit in suits:
                size = 5
            else:
                size = 4
            # Crib can't score 4 flush.
            if cards[0] not in self.hands['The Crib'] or size == 5:
                score = size
        return score

    def score_hands(self):
        """
        Score the hands after a round of play. (bool)

        The return value is a flag for someone winning the game.
        """
        # Loop through the players, starting on the dealer's left.
        player_index = (self.dealer_index + 1) % len(self.players)
        names = [player.name for player in self.players[player_index:] + self.players[:player_index]]
        for name in names + ['The Crib']:
            self.human.tell()
            hand_score = 0
            # Score the crib to the dealer.
            if name == 'The Crib':
                cards = self.hands['The Crib'].cards
                name = self.players[self.dealer_index].name
                message = 'Now scoring the crib for the dealer ({}): {} + {}'
            else:
                cards = self.hands[name].cards + self.in_play[name].cards
                message = "Now scoring {}'s hand: {} + {}"
            self.human.tell(message.format(name, ', '.join([str(card) for card in cards]), self.starter))
            # Check for flushes. (four in hand or five with starter)
            suit_score = self.score_flush(cards)
            if suit_score:
                hand_score += suit_score
                message = '{} scores {} points for a {}-card flush.'
                self.human.tell(message.format(name, suit_score, utility.number_word(suit_score)))
            # Check for his nobs (jack of suit of starter)
            nob = CribCard('J', self.starter.suit)
            if nob in cards:
                hand_score += 1
                self.human.tell('{} scores one for his nob.'.format(name))
            # Add the starter for the scoring categories below.
            cards.append(self.starter)
            # Check for 15s.
            fifteens = self.score_fifteens(cards)
            if fifteens:
                hand_score += 2 * fifteens
                s = ['', 's'][fifteens > 1]
                message = '{} scores {} for {} combination{} adding to 15.'
                self.human.tell(message.format(name, 2 * fifteens, utility.number_word(fifteens), s))
            # Check for pairs.
            rank_data = self.score_pairs(cards)
            for rank, count, pair_score in rank_data:
                hand_score += pair_score
                rank_name = CribCard.rank_names[CribCard.ranks.index(rank)].lower()
                if rank_name == 'six':
                    rank_name = 'sixe'
                message = '{} scores {} for getting {} {}s.'
                self.human.tell(message.format(name, pair_score, utility.number_word(count), rank_name))
            # Check for runs.
            for run_length, run_count in self.score_runs(cards):
                hand_score += run_length * run_count
                # Update the user.
                if run_count == 1:
                    message = '{0} scored {1} points for a {1} card run.'
                else:
                    message = '{0} scored {3} points for {2} runs of length {1}.'
                self.human.tell(message.format(name, run_length, run_count, run_length * run_count))
            # Announce and record total.
            self.human.tell('{} scored a total of {} points for this hand.'.format(name, hand_score))
            self.scores[name] += hand_score
            # Check for a win.
            if self.scores[name] >= self.target_score:
                self.human.tell('{} has won with {} points.'.format(name, self.scores[name]))
                return True
            elif not self.auto_score:
                self.human.ask(ENTER_TEXT)
        return False

    def score_pairs(self, cards):
        """
        Score any pairs in the given cards. (list of tuple)

        The tuples returned are the rank, the number cards of that rank, and the score
        for that rank.

        Parameters:
        cards: The cards to score. (list of CribCard)
        """
        rank_counts = collections.Counter([card.rank for card in cards])
        rank_data = []
        for rank, count in rank_counts.most_common():
            if count < 2:
                break
            pair_score = utility.choose(count, 2) * 2
            rank_data.append((rank, count, pair_score))
        return rank_data

    def score_runs(self, cards):
        """
        Score any straights in the given cards. (list of tuple)

        Parameters:
        cards: The cards to score. (int)
        """
        # Check for pairs or adjacent ranks.
        ranks = sorted([CribCard.ranks.index(card.rank) for card in cards])
        diffs = [second - first for first, second in zip(ranks, ranks[1:])]
        run = []
        for diff in diffs:
            if diff < 2:
                run.append(diff)
            elif len(run) > 1:
                break
            else:
                run = []
        # Record any runs that occurred.
        run_data = []
        if len(run) > 1 and run.count(1) > 1:
            # Check pair count to determine the number of runs.
            pairs = [index for index, diff in enumerate(run) if diff == 0]
            run_count = [1, 2, 4][len(pairs)]
            # Adjust for three of a kind as opposed to two pair.
            if len(pairs) == 2 and pairs[1] - pairs[0] == 1:
                run_count = 3
            # Update the score.
            run_length = run.count(1) + 1
            run_data.append((run_length, run_count))
        return run_data

    def score_sequence(self, player):
        """
        Score cards as they are played in sequence. (None)

        Parameters:
        player: The player who is scoring. (player.Player)
        """
        played = self.in_play['Play Sequence']
        # Check for a total of 15.
        if self.card_total == 15:
            self.scores[player.name] += 2
            self.human.tell('{} scores 2 points for reaching 15.'.format(player.name))
            if not self.auto_score:
                self.human.ask(ENTER_TEXT)
        # Count the cards of the same rank.
        rank_count = 1
        for play_index in range(-2, -len(played) - 1, -1):
            if played.cards[play_index].rank != played.cards[-1].rank:
                break
            rank_count += 1
        # Score any pairs.
        if rank_count > 1:
            pair_score = utility.choose(rank_count, 2) * 2
            self.scores[player.name] += pair_score
            message = '{} scores {} for getting {} cards of the same rank.'
            self.human.tell(message.format(player.name, pair_score, utility.number_word(rank_count)))
            if not self.auto_score:
                self.human.ask(ENTER_TEXT)
        # Check for runs.
        run_count = 0
        for run_index in range(-3, -len(played) - 1, -1):
            values = sorted([CribCard.ranks.index(card.rank) for card in played.cards[run_index:]])
            diffs = [second - first for first, second in zip(values, values[1:])]
            if diffs and all([diff == 1 for diff in diffs]):
                run_count = len(values)
        # Score any runs.
        if run_count:
            self.scores[player.name] += run_count
            message = '{} scores {} for getting a {}-card straight.'
            self.human.tell(message.format(player.name, run_count, utility.number_word(run_count)))
            if not self.auto_score:
                self.human.ask(ENTER_TEXT)

    def set_options(self):
        """Set the game options. (None)"""
        # Set the hand options
        self.option_set.add_option('cards', converter = int, default = 6, valid = (5, 6, 7),
            question = 'How many cards should be dealt? (return for 6)? ')
        self.option_set.add_option('discards', converter = int, default = 2, valid = (1, 2),
            question = 'How many cards should be discarded (return for 2)? ')
        # Set the play options.
        self.option_set.add_option('one-go', 
            question = 'Should there only be one round of play, or one go? bool')
        # Set the score options.
        self.option_set.add_option('target-score', ['win'], int, default = 121, check = lambda x: x > 0,
            question = 'How many points should it take to win (return for 121)? ')
        self.option_set.add_option('skunk', [], int, default = 91, check = lambda x: x > 0,
            question = 'How many points should it take to avoid a skunk (return for 91)? ')
        self.option_set.add_option('double-skunk', [], int, default = 0, check = lambda x: x > -1,
            question = 'How many points should it take to avoid a double skunk (return for 0)? ')
        self.option_set.add_option('last', [], int, default = 0, check = lambda x: x > -1,
            question = 'How many points should the last player get for being last (return for 0)? ')
        # Set the number of opponents.
        self.option_set.add_option('n-bots', converter = int, default = 1, valid = (1, 2, 3),
            question = 'How many bots would you like to play against (return for 1)? ')
        # Set the match options.
        self.option_set.add_option('match', converter = int, default = 1,
            question = 'How many games for match play (return for single game)? ')
        self.option_set.add_option('match-scores', valid = ('acc', 'long', 'free', 'four'), 
            default = 'acc', question = 'Should match scores be ACC, long, free, or triple? ')
        # Set the variant groups.
        five_card = 'one-go cards=5 discards=1 win=61 skunk=31 last=3'
        self.option_set.add_group('five-card', five_card)
        self.option_set.add_group('5-card', five_card)
        seven_card = 'cards=7 win=181 skunk=151'
        self.option_set.add_group('seven-card', seven_card)
        self.option_set.add_group('7-card', seven_card)
        # Interface options (do not count in num_options)
        self.option_set.add_group('fast', 'auto-go auto-score no-cut no-pick')
        self.option_set.add_option('auto-go', 
            question = 'Should prompts be skipped when you must go? bool')
        self.option_set.add_option('auto-score', 
            question = 'Should prompts be skipped when players score? bool')
        self.option_set.add_option('no-cut', 
            question = 'Should cutting the deck be skipped? bool')
        self.option_set.add_option('no-pick', 
            question = 'Should picking cards for first deal be skipped? bool')

    def set_up(self):
        """Set up the game. (None)"""
        # Set the players.
        random.shuffle(self.players)
        # set up the tracking variables.
        self.phase = 'deal'
        self.card_total = 0
        self.go_count = 0
        # Set up the deck.
        self.deck = cards.Deck(card_class = CribCard)
        self.deck.shuffle()
        # Set up the hands.
        self.hands = {player.name: cards.Hand(self.deck) for player in self.players}
        self.hands['The Crib'] = cards.Hand(self.deck)
        self.in_play = {player.name: cards.Hand(self.deck) for player in self.players}
        self.in_play['Play Sequence'] = cards.Hand(self.deck)
        # Pick the dealer.
        if self.no_pick:
            random.shuffle(self.players)
            self.dealer_index = -1
        else:
            players = self.players
            while True:
                cards_picked = []
                for player in self.players:
                    query = 'Enter a number to pick a card: '
                    card_index = player.ask_int(query, cmd = False, default = 0)
                    card = self.deck.pick(card_index)
                    self.human.tell('{} picked the {}.'.format(player, card.name))
                    self.deck.discard(card)
                    cards_picked.append((card, player))
                cards_picked.sort()
                if cards_picked[0][0].rank == cards_picked[1][0].rank:
                    self.human.tell('Tie! Pick again.')
                    players = [plyr for crd, plyr in cards_picked if crd.rank == cards_picked[0][0].rank]
                else:
                    break
            self.dealer_index = self.players.index(cards_picked[0][1]) - 1


class CribBot(player.Bot):
    """
    A bot for playing Cribbage. (player.Bot)
    """

    def ask(self, query):
        """
        Respond to a question from the game. (str)

        Parameters:
        query: The question the game asked. (str)
        """
        hand = self.game.hands[self.name]
        if 'discard' in query:
            dealer = self.name == self.game.players[self.game.dealer_index].name
            possibles = []
            for keepers in itertools.combinations(hand, self.game.cards - self.game.discards):
                discards = [card for card in hand if card not in keepers]
                if dealer:
                    score = self.score_four(keepers) + self.score_discards(discards)
                else:
                    score = self.score_four(keepers) - self.score_discards(discards)
                possibles.append((score, discards))
            possibles.sort(reverse = True)
            return ' '.join([str(card) for card in possibles[0][1]])
        elif 'no playable' in query:
            self.game.human.tell('\n{} calls "go."'.format(self.name))
            return ''
        elif 'play' in query:
            playable = [card for card in hand if 31 - card >= self.game.card_total]
            sums = [card for card in playable if card + self.game.card_total in (1, 2, 3, 4, 15, 31)]
            if sums:
                play = sums[0]
            playable.sort()
            if self.game.card_total:
                last_card = self.game.in_play['Play Sequence'].cards[-1]
                pairs = [card for card in playable if card.rank == last_card.rank]
                if pairs:
                    play = pairs[0]
                else:
                    playable.sort()
                    play = playable[-1]
            else:
                play = playable[0]
            self.game.human.tell('\n{} played the {}.'.format(self.name, play.name.lower()))
            return str(play)
        elif query.startswith('Enter a number'):
            return str(random.randint(1, 121))
        elif query.startswith('Please press enter'):
            return ''
        else:
            raise player.BotError('Unexepected question to CribBot: {!r}'.format(query))

    def tell(self, message):
        """
        The the bot some information. (None)

        Parameters:
        message: The information to tell the bot. (str)
        """
        if isinstance(message, Cribbage):
            pass
        else:
            super(CribBot, self).tell(message)

    def score_discards(self, cards):
        """
        'Score' a potential set of descards. (float)

        The score given here is a postive rating of how bad an idea it is to
        discard those card(s).

        Parameters:
        cards: The cards to score. (list of CribCard)
        """
        score = 0
        if len(cards) == 2:
            if sum(cards) == 15 or cards[0].rank == cards[1].rank:
                score += 2
            if abs(cards[0] - cards[1]) == 1:
                score += 0.75
            if cards[0].suit == cards[1].suit:
                score += 0.25
        ranks = sorted([card.rank for card in cards])
        score += (ranks.count('5') + ranks.count('J')) / 2.0
        if ranks in (['4', 'A'], ['6', '8'], ['6', '9'], ['7', '9']):
            score += 0.5
        return score

    def score_four(self, cards):
        """
        Score a potential set of four cards. (int)

        Parameters:
        cards: The cards to score. (list of CribCard)
        """
        score = self.game.score_flush(cards) + self.game.score_fifteens(cards)
        score += sum([pair_score for rank, count, pair_score in self.game.score_pairs(cards)])
        score += sum([run_length * run_count for run_length, run_count in self.game.score_runs(cards)])
        return score


class CribCard(cards.Card):
    """
    A card for a game of Cribbage. (cards.Card)

    Attributes:
    value: The numerical value of the card. (int)

    Overridden Methods:
    __init__
    __add__
    __radd__
    """

    def __init__(self, rank, suit):
        """
        Set up the card. (None)

        Parameters:
        rank: The rank of the card. (str)
        suit: The suit of the card. (str)
        """
        super(CribCard, self).__init__(rank, suit)
        self.value = min(self.ranks.index(self.rank), 10)

    def __add__(self, other):
        """
        Add the card as an integer. (int)

        Parameters:
        other: The integer to add to. (int)
        """
        return self.value + other

    def __radd__(self, other):
        """
        Add the card as an integer. (int)

        Parameters:
        other: The integer to add to. (int)
        """
        return self.value + other

    def __rsub__(self, other):
        """
        Subtract the card as an integer. (int)

        Parameters:
        other: The integer to add to. (int)
        """
        return other - self.value

    def __sub__(self, other):
        """
        Subtract the card as an integer. (int)

        Parameters:
        other: The integer to add to. (int)
        """
        return self.value - other


if __name__ == '__main__':
    try:
        input = raw_input
    except NameError:
        pass
    name = input('What is your name? ')
    crib = Cribbage(player.Player(name), '')
    crib.play()