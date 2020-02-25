"""
cribbage_game.py

A game of Cribbage.

Copyright (C) 2018-2020 by Craig O'Brien and the t_games contributors.
See the top level __init__.py file for details on the t_games license.

Constants:
CREDITS: The credits for Cribbage. (str)
ENTER_TEXT: Press enter to continue. (str)
OPTIONS: The options for Cribbage. (str)
RULES: The rules for Cribbage. (str)

Classes:
Cribbage: A game of Cribbage. (game.Game)
CribBot: A bot for playing Cribbage. (player.Bot)
"""


import collections
import itertools
import random

from .. import cards
from .. import game
from .. import player
from .. import utility


CREDITS = """
Game Design: John Suckling
Game Programming: Craig "Ichabod" O'Brien
"""

ENTER_TEXT = 'Please press enter to continue: '

OPTIONS = """
auto-go (ag): Don't prompt players who must go.
auto-score (as): Don't prompt the user after a player scores.
cards= (c=): The number of cards dealt (default = 6).
discards= (d=): The number of cards discarded (default = 2).
double-skunk= (ds=): The score needed to avoid a double skunk (default = 0).
fast: Equivalent to auto-go auto-score no-cut no-pick.
five-card (5-card, 5c): equivalent to one-go cards=5 discards=1 target-score=61
    skunk=31 last=3
four-partners (4-partners, 4p): equivalent to n-bots=3 partners cards=5
    discards=1
gonzo (gz): equivalent to target-score=61 match=5 skunk=41 double-skunk=21
    skunk-scores=four
last= (l=): The initial score of the last player to play (default = 0).
match= (m=): The number of games to play in a match. (default = 1).
    Match results only make sense for two player games.
n-bots= (nb=): The number of bots to play against. (default = 1)
no-cut (!c): Skip cutting the deck before the deal.
no-pick (!p): Skip picking a card to see who deals first.
one-go (1g): There is only one round of play, that is, only one go.
partners (p): Pair players off into teams.
seven-card (7-card, 7c): equivalent to cards=7 target-score=181 skunk=151
skunk= (s=): The score to avoid a skunk (defualt = 91, only in match play).
skunk-scores= (ss=): How to score wins/skunks/double skunks
    acc: 2/3/3
    long: 3/4/4
    free: 1/2/3
    four: 1/2/4
    or you can enter three numbers separated by slashes.
    defaults to acc (American Cribbage Congress).
solo (1): The players are teamed against the dealer, and the dealer can swap
    cards with the crib. The dealer scores first, along with the crib.
target-score= (win=): The score needed to win (default = 121).
three-solo (3-solo, 3s): Equivalent to one-go cards=5 discards=1 win=61
    skunk=31 n-bots=2 solo
"""

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
"""


class Cribbage(game.Game):
    """
    A game of Cribbage. (game.Game)

    Attributes:
    auto_go: Flag for not prompting players who must go. (bool)
    auto_score: Flag for not prompting when a player scores. (bool)
    card_total: The running total of cards played this round. (int)
    cards: The number of cards dealt. (int)
    cyborg: A flag for using a cyborg for the bot player. (bool)
    dealer_index: Index of self.players marking the dealer. (int)
    deck: The deck of cards used in the game. (cards.Deck)
    discards: The number of cards discarded. (int)
    double_pairs: A flag for pairs counting double. (bool)
    double_skunk: The score needed to avoid a double skunk. (int)
    go_count: The number of players who have passed consecutively. (int)
    hands: The player's hands in the game. (dict of str: cards.Hand)
    in_play: The cards each player has played. (dict of str: cards.Hand)
    last: The intitial score of the last player to play. (int)
    match: The winning match score. (int)
    match_scores: The match score for each player by name. (dict of str: int)
    n_bots: The number of bots in the game. (int)
    no_cut: A flag for skipping cutting the deck. (bool)
    no_pick: A flag for skipping picking a card to see who deals. (bool)
    phase: The phase of play, either deal, discard, or play. (str)
    one_go: A flag for there only being one round of play. (bool)
    partners: A flag for having teams of players. (bool)
    skip_player: The player whose next discard is skipped. (player.Player)
    skunk: The score needed to avoid being skunked.
    skunk_scores: The match points earned for wins and skunks. (tuple of int)
    solo: A flag for teaming everyone against the dealer. (bool)
    starter: The starter card. (Card)
    target_score: The score needed to win the game. (int)
    teams: The people on each player's team. (dict of str: list)

    Methods:
    add_points: Add points to a player's score. (None)
    deal: Deal the cards. (None)
    player_discards: Allow the player to discard cards. (None)
    player_play: Allow the player to play a card. (None)
    reset: Reset the game after a pegging round. (None)
    score_fifteens: Score any sets totalling to fifteen in the given cards. (int)
    score_flush: Score any flushes in the given cards. (int)
    score_hands: Score the hands after a round of play. (bool)
    score_pairs: Score any pairs in the given cards. (list of tuple)
    score_runs: Score any straights in the given cards. (list of tuple)
    score_sequence: Score cards as they are played in sequence. (None)
    show_match: Show the match scores. (None)

    Overridden Methods:
    __str__
    game_over
    handle_options
    player_action
    set_options
    set_up
    """

    aka = ['Crib']
    categories = ['Card Games']
    credits = CREDITS
    name = 'Cribbage'
    num_options = 11
    options = OPTIONS
    rules = RULES

    def __str__(self):
        """Generate a human readable text representation. (str)"""
        # Show the current scores.
        lines = ['\nScores\n------\n']
        for player in self.players:
            lines.append('{}: {}'.format(player.name, self.scores[player.name]))
        # Show the player's hand.
        hand = self.hands[self.current_player]
        lines.append('\nCards in Hand: {}'.format(hand.show_player()))
        # Show the current cards in play.
        if self.phase != 'discard':
            lines.append('\nStarter Card: {}'.format(self.starter))
            lines.append('\nCards played: {}'.format(self.in_play['Play Sequence']))
        lines.append('\nRunning Total: {}'.format(self.card_total))
        return '\n'.join(lines)

    def add_points(self, scorer, points):
        """
        Add points to a player's score. (None)

        Parameters:
        scorer: The player to get the points. (player.Player or str)
        points: The points they should get.
        """
        # Add his score to all team mates.
        for player in self.teams[scorer]:
            self.scores[player] += points

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
        self.dealer = self.get_next_player(self.dealer)
        self.next_player = self.get_next_player(self.dealer)
        self.dealer_index = self.players.index(self.dealer)
        print('\nThe current dealer is {}.'.format(self.dealer.name))
        # Handle the solo option.
        if self.solo:
            # Set up teams.
            self.teams[dealer] = [dealer]
            non_dealers = [player for player in self.players if player != dealer]
            self.teams.update({player: non_dealers for player in non_dealers})
            # Redirect the crib.
            self.hands['The Crib'] = self.hands[dealer]
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
            left = self.next_player
            query = 'Enter a number to cut the deck: '
            cut_index = left.ask_int(query, cmd = False, default = 0)
            self.deck.cut(cut_index)
        # Deal the cards
        self.deck.deal_n_each(self.cards, self.players)
        for card in range(4 - len(self.players) * self.discards):
            self.hands['The Crib'].draw()
        # Make a dummy starter card.
        self.starter = self.deck.parse_text('XS')
        # Reset the tracking variables.
        self.phase = 'discard'

    def do_gipf(self, arguments):
        """
        Backgammon makes pairs score four points each for one round.

        Craps allows you to discard any one card and get a replacement from the deck.

        Crazy Eights skips the next player's discard.
        """
        game, losses = self.gipf_check(arguments, ('backgammon', 'craps', 'crazy eights'))
        # Backgammon doubles the score for pairs.
        if game == 'backgammon':
            self.human.tell('Pairs score four points each this round.')
            self.double_pairs = True
        # Craps lets you swap a card with one from the deck.
        elif game == 'craps':
            # Get a valid card to discard.
            hand = self.hands[self.human]
            card = self.human.ask_card('Pick a card to replace: ', valid = hand, cmd = False)
            # Replace that card.
            hand.discard(card)
            hand.draw()
        # Crazy Eights skips the next player's play.
        elif game == 'crazy eights':
            next_player = self.skip_player()
            self.human.tell("{}'s next discard will be skipped.".format(next_player))
        # Otherwise I'm confused.
        else:
            self.human.error("I'm sorry, sir, but that is simply not acceptable in this venue.")
        return True

    def game_over(self):
        """Check for the end of the game. (None)"""
        if max(self.scores.values()) >= self.target_score:
            # Reset the teams in solo play.
            if self.solo:
                self.teams = {player: [player] for player in self.players}
            # Determine the winner.
            scores = self.sorted_scores()
            names = ' and '.join(self.teams[scores[0][1]])
            plural = '' if ' and ' in names else 's'
            self.human.tell('\n{} win{} with {} points.'.format(names, plural, scores[0][0]))
            # Check for skunk.
            match_points = self.skunk_scores[0]
            if scores[1][0] < self.double_skunk:
                match_points = self.skunk_scores[2]
                self.human.tell('{1} got double skunked with {0} points.'.format(*scores[1]))
            elif scores[1][0] < self.skunk:
                match_points = self.skunk_scores[1]
                self.human.tell('{1} got skunked with {0} points.'.format(*scores[1]))
            # Record the match scores.
            self.match_scores[scores[0][1]] += match_points
            if self.match > 1:
                self.show_match()
            # Determine end of match.
            if max(self.match_scores.values()) >= self.match:
                if self.match > 1:
                    score_data = self.match_scores
                    points_type = 'match '
                else:
                    score_data = self.scores
                    points_type = ''
                # Calculate win/loss/draw stats.
                human_score = score_data[self.human]
                max_score, max_player = human_score, self.human
                for player, score in score_data.items():
                    if player in self.teams[self.human]:
                        continue
                    elif score < human_score:
                        self.win_loss_draw[0] += 1
                    elif score > human_score:
                        self.win_loss_draw[1] += 1
                    elif score == human_score:
                        self.win_loss_draw[2] += 1
                    if score > max_score:
                        max_score, max_player = score, player
                # Declare the match winner.
                if self.match > 1:
                    self.human.tell('{} won the match with {} match points.'.format(max_player, max_score))
                # Tell human their place, if they didn't win.
                if self.win_loss_draw[1]:
                    place = utility.number_word(self.win_loss_draw[1] + 1, ordinal = True)
                    if not self.win_loss_draw[0]:
                        place = 'last'
                    message = 'You came in {} place with {} {}points.'
                    self.human.tell(message.format(place, human_score, points_type))
                # Halve win/loss/draw for team games, so it's per team not per preson.
                if self.partners:
                    self.win_loss_draw = [x // 2 for x in self.win_loss_draw]
                return True
            else:
                # Reset for the next game in the match.
                self.scores = {player.name: 0 for player in self.players}
                self.deal()
                self.card_total = 0
                self.go_count = 0
                self.in_play['Play Sequence'].cards = []
                return False
        else:
            return False

    def handle_options(self):
        """Handle the game option settings. (None)"""
        super(Cribbage, self).handle_options()
        # Add the human.
        self.players = [self.human]
        taken_names = [self.human]
        # Check for bot class.
        if self.cyborg:
            bot_class = player.Cyborg
            self.flags |= 512
        else:
            bot_class = CribBot
        # Add the bots.
        for bot in range(self.n_bots):
            self.players.append(bot_class(self.players))
        # Warn user for trying to make a team with an odd number of players.
        if self.partners and len(self.players) % 2:
            warning = 'Invalid number of players for the partners option: {}.'
            self.option_set.errors.append(warning.format(len(self.players)))
            self.partners = False
        # Set up match play.
        if self.match > 1:
            self.flags |= 256
            # Set the skunk scores.
            if self.skunk_scores == 'acc':
                self.skunk_scores = (2, 3, 3)
            elif self.skunk_scores == 'long':
                self.skunk_scores = (3, 4, 4)
            elif self.skunk_scores == 'free':
                self.skunk_scores = (1, 2, 3)
            elif self.skunk_scores == 'four':
                self.skunk_scores = (1, 2, 4)
            else:
                # Set custom skunk scores.
                self.skunk_scores = tuple(int(score) for score in self.skunk_scores)
        else:
            # Set dummy values for non-match play.
            self.match = 1
            self.skunk_scores = (1, 1, 1)

    def player_action(self, player):
        """
        Allow the player to do something.

        Parameters:
        player: The current player. (player.Player)
        """
        # Deal the cards when necessary.
        if self.phase == 'deal':
            self.deal()
            return False
        # Give the state of the game.
        player.tell(self)
        # Handle discarding to the crib.
        if self.phase == 'discard':
            return self.player_discards(player)
        # Handle playing cards for pegging.
        elif self.phase == 'play':
            return self.player_play(player)

    def player_discards(self, player):
        """
        Allow the player to discard cards. (None)

        Parameters:
        player: The current player. (player.Player)
        """
        # Handle solo option for dealer.
        if self.solo and player == self.dealer:
            # Handle different discard count.
            discard_save = self.discards
            self.discards = self.cards - self.discards
            # Reset the crib.
            self.hands['The Crib'] = cards.Hand(deck = self.deck)
        # Get the discards.
        discard_plural = utility.num_text(self.discards, 'card')
        query = '\nWhich {} would you like to discard to the crib, {}? '.format(discard_plural, player)
        while True:
            discards = player.ask_card_list(query, self.hands[player], [self.discards])
            if isinstance(discards, str):
                if not self.handle_cmd(discards):
                    return False
            else:
                break
        # Handle discards.
        for card in discards:
            self.hands[player].shift(card, self.hands['The Crib'])
        # Check for starting play after dealer discards.
        if player == self.dealer:
            self.phase = 'play'
            self.starter = self.deck.deal(up = True)
            if self.solo:
                self.discards = discard_save
            # Check for heels.
            if self.starter.rank == 'J':
                self.human.tell('The dealer got their heels.')
                if not self.auto_score:
                    self.human.ask(ENTER_TEXT)
                self.add_points(self.dealer, 2)
        return False

    def player_play(self, player):
        """
        Allow the player to play a card. (None)

        Parameters:
        player: The current player. (player.Player)
        """
        # Get the player information
        hand = self.hands[player]
        in_play = self.in_play[player]
        # Check for playable cards.
        playable = [card for card in hand if card + self.card_total <= 31]
        if not playable:
            # Warn player of no playable cards.
            player.tell('\nYou have no playable cards and must go.')
            if not self.auto_score:
                player.ask(ENTER_TEXT)
            # Update and check go count
            self.go_count += 1
            if self.go_count == len(self.players):
                self.human.tell('\nEveryone has passed.')
                self.add_points(player, 1)
                self.human.tell('{} scores 1 for the go.'.format(player))
                if not self.auto_score:
                    self.human.ask(ENTER_TEXT)
                self.reset()
            return False
        # Get card to play.
        while True:
            query = '\nWhich card would you like to play, {}? '.format(player)
            card = player.ask_card(query, valid = hand)
            if isinstance(card, str):
                if not self.handle_cmd(card):
                    return False
            elif card + self.card_total > 31:
                # Warn the player about unplayable cards.
                player.error('That card would put the running total over 31.')
                return True
            else:
                break
        # Score the card.
        points, message = self.score_sequence(player, card)
        if points:
            self.add_points(player, points)
            # Inform the user.
            self.human.tell(message)
            if not self.auto_score:
                self.human.ask(ENTER_TEXT)
        # Play the card.
        hand.shift(card, in_play)
        self.in_play['Play Sequence'].cards.append(in_play.cards[-1])
        # Update the tracking variables.
        self.card_total += card
        self.go_count = 0
        # Check for end of round
        if self.card_total == 31:
            self.reset()
        return False

    def reset(self):
        """Reset the game after a pegging round. (None)"""
        self.card_total = 0
        self.go_count = 0
        self.in_play['Play Sequence'].cards = []
        # Player names are used to get hands to avoid checking the crib for cards.
        if (not any([self.hands[player] for player in self.players])) or self.one_go:
            if not self.score_hands():
                self.deal()  # Only deal if no one wins.

    def score_fifteens(self, cards):
        """
        Score any sets totalling to fifteen in the given cards. (int)

        Parameters:
        cards: The cards to score. (list of Card)
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
        cards: The cards to score. (list of Card)
        """
        score = 0
        suits = set(card.suit for card in cards)
        if len(suits) == 1:
            # Check for five card flush.
            if self.starter.suit in suits:
                size = self.cards - self.discards + 1
            else:
                size = self.cards - self.discards
            # Crib can't score 4 flush.
            if cards[0] not in self.hands['The Crib'] or size == self.cards - self.discards + 1:
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
        names.append('The Crib')
        # Dealer scores first with the solo option.
        if self.solo:
            names = names[-2:] + names[:-2]
        for name in names:
            self.human.tell()
            # Score the crib to the dealer.
            if name == 'The Crib':
                cards = self.hands['The Crib'][:]
                name = self.dealer.name
                message = 'Now scoring the crib for the dealer ({}): {} + {}'
            else:
                cards = self.hands[name] + self.in_play[name]
                message = "Now scoring {}'s hand: {} + {}"
            self.human.tell(message.format(name, ', '.join([str(card) for card in cards]), self.starter))
            hand_score = self.score_one_hand(cards, name)
            # Announce and record total.
            self.human.tell('{} scored a total of {} points for this hand.'.format(name, hand_score))
            self.add_points(name, hand_score)
            if self.scores[name] >= self.target_score:
                return True
            elif not self.auto_score:
                self.human.ask(ENTER_TEXT)
        self.double_pairs = False
        return False

    def score_one_hand(self, hand, name):
        """
        Score a single hand after a round of play. (int)

        Parameters:
        hand: The cards in the hand. (list of Card)
        name: The name of the player who's hand it is. (str)
        """
        hand_score = 0
        # Check for flushes. (four in hand or five with starter)
        suit_score = self.score_flush(hand)
        if suit_score:
            hand_score += suit_score
            message = '{} scores {} points for a {}-card flush.'
            self.human.tell(message.format(name, suit_score, utility.number_word(suit_score)))
        # Check for his nobs (jack of suit of starter)
        nob = cards.Card('J', self.starter.suit)
        if nob in hand:
            hand_score += 1
            self.human.tell('{} scores one for his nob.'.format(name))
        # Add the starter for the scoring categories below.
        hand.append(self.starter)
        # Check for fifteens.
        fifteens = self.score_fifteens(hand)
        if fifteens:
            hand_score += 2 * fifteens
            # Update the user.
            plural_15 = utility.number_plural(fifteens, 'combination')
            message = '{} scores {} for {} adding to 15.'
            self.human.tell(message.format(name, 2 * fifteens, plural_15))
        # Check for pairs.
        rank_data = self.score_pairs(hand)
        for rank, count, pair_score in rank_data:
            hand_score += pair_score
            # Update the user.
            rank_name = self.deck.rank_set.names[rank].lower()
            if rank_name == 'six':
                rank_name = 'sixe'
            message = '{} scores {} for getting {} {}s.'
            self.human.tell(message.format(name, pair_score, utility.number_word(count), rank_name))
        # Check for runs.
        for run_length, run_count in self.score_runs(hand):
            hand_score += run_length * run_count
            # Update the user.
            if run_count == 1:
                message = '{0} scored {1} points for a {1} card run.'
            else:
                message = '{0} scored {3} points for {2} runs of length {1}.'
            self.human.tell(message.format(name, run_length, run_count, run_length * run_count))
        return hand_score

    def score_pairs(self, cards):
        """
        Score any pairs in the given cards. (list of tuple)

        The tuples returned are the rank, the number cards of that rank, and the score
        for that rank.

        Parameters:
        cards: The cards to score. (list of Card)
        """
        rank_counts = collections.Counter([card.rank for card in cards])
        rank_data = []
        for rank, count in rank_counts.most_common():
            if count < 2:
                break
            pair_score = utility.choose(count, 2) * 2
            if self.double_pairs:
                pair_score *= 2
            rank_data.append((rank, count, pair_score))
        return rank_data

    def score_runs(self, cards):
        """
        Score any straights in the given cards. (list of tuple)

        Parameters:
        cards: The cards to score. (int)
        """
        # Get the numeric ranks of the cards.
        ranks = sorted([card.rank_num for card in cards])
        # Loop through consecutive pairs of ranks.
        run_data = []
        run = []
        run_count, count_mod = 1, 1
        for first, second in zip(ranks, ranks[1:]):
            # Check the difference
            diff = second - first
            if diff < 2:
                # Track the run, accounting for duplicates.
                if diff:
                    run.append(diff)
                    run_count *= count_mod
                    count_mod = 1
                else:
                    count_mod += 1
            else:
                # Store any completed runs.
                if len(run) > 1:
                    run_data.append((len(run) + 1, run_count * count_mod))
                # Reset run tracking.
                run = []
                run_count, count_mod = 1, 1
        # Catch any final run.
        if len(run) > 1:
            run_data.append((len(run) + 1, run_count * count_mod))
        return run_data

    def score_sequence(self, player, card):
        """
        Score cards as they are played in sequence. (int, str)

        The return value is the points scored and any message about the points scored.
        A return of (0, '') means no points were scored.

        Parameters:
        player: The player who is scoring. (player.Player)
        card: The next card to play in sequence. (Card)
        """
        played = list(reversed(self.in_play['Play Sequence'].cards + [card]))
        next_total = self.card_total + card
        points, message = 0, []
        # Check for a total of 15.
        if next_total == 15:
            points += 2
            message.append('{} scores 2 points for reaching 15.'.format(player.name))
        # Count the cards of the same rank.
        rank_count = 1
        for card, previous in zip(played, played[1:]):
            if card.rank != previous.rank:
                break
            rank_count += 1
        # Score any pairs.
        if rank_count > 1:
            pair_score = utility.choose(rank_count, 2) * 2
            if self.double_pairs:
                pair_score *= 2
            points += pair_score
            text = '{} scores {} points for getting {} cards of the same rank.'
            message.append(text.format(player.name, pair_score, utility.number_word(rank_count)))
        # Check for runs.
        run_count = 0
        for run_len in range(3, len(played) + 1):
            values = sorted([card.rank_num for card in played[:run_len]])
            diffs = [second - first for first, second in zip(values, values[1:])]
            if diffs and all([diff == 1 for diff in diffs]):
                run_count = len(values)
        # Score any runs.
        if run_count:
            points += run_count
            text = '{} scores {} points for getting a {}-card straight.'
            message.append(text.format(player.name, run_count, utility.number_word(run_count)))
        # Check for a total of 31.
        if next_total == 31:
            points += 2
            text = '\nThe count has reached 31.\n{} scores 2 points for reaching 31.'
            message.append(text.format(player.name))
        return points, '\n'.join(message)

    def set_options(self):
        """Set the game options. (None)"""
        # Set the hand options.
        self.option_set.add_option('cards', ['c'], converter = int, default = 6, valid = (5, 6, 7),
            question = 'How many cards should be dealt? (return for 6)? ')
        self.option_set.add_option('discards', ['d'], converter = int, default = 2, valid = (1, 2),
            question = 'How many cards should be discarded (return for 2)? ')
        # Set the play options.
        self.option_set.add_option('one-go', ['1g'],
            question = 'Should there only be one round of play, or one go? bool')
        # Set the score options.
        self.option_set.add_option('target-score', ['win'], int, default = 121, check = lambda x: x > 0,
            question = 'How many points should it take to win (return for 121)? ')
        self.option_set.add_option('skunk', ['s'], int, default = 91, check = lambda x: x > 0,
            question = 'How many points should it take to avoid a skunk (return for 91)? ')
        self.option_set.add_option('double-skunk', ['ds'], int, default = 0, check = lambda x: x > -1,
            question = 'How many points should it take to avoid a double skunk (return for 0)? ')
        self.option_set.add_option('last', ['l'], int, default = 0, check = lambda x: x > -1,
            question = 'How many points should the last player get for being last (return for 0)? ')
        self.option_set.add_option('partners', ['p'],
            question = 'Should players be paired off into teams? bool')
        self.option_set.add_option('solo', ['1'],
            question = 'Should players be teamed against the dealer? bool')
        # Set the number of opponents.
        self.option_set.add_option('n-bots', ['nb'], converter = int, default = 1, valid = (1, 2, 3),
            question = 'How many bots would you like to play against (return for 1)? ')
        self.option_set.add_option('cyborg')
        # Set the match options.
        self.option_set.add_option('match', ['m'], converter = int, default = 1,
            question = 'How many games for match play (return for single game)? ')
        self.option_set.add_option('skunk-scores', ['ss'], str.lower, check = skunk_check,
            default = 'acc', question = 'Should match scores be ACC, long, free, or triple? ')
        # Set the variant groups.
        five_card = 'one-go cards=5 discards=1 win=61 skunk=31 last=3'
        self.option_set.add_group('five-card', ['5-card', '5c'], five_card)
        self.option_set.add_group('seven-card', ['7-card', '7c'], 'cards=7 win=181 skunk=151')
        four_partners = 'n-bots=3 partners cards=5 discards=1'
        self.option_set.add_group('four-partners', ['4-partners', '4p'], four_partners)
        three_solo = 'one-go cards=5 discards=1 win=61 skunk=31 n-bots=2 solo'
        self.option_set.add_group('three-solo', ['3-solo', '3s'], three_solo)
        gonzo = 'target-score=49 match=5 skunk=31 double-skunk=18 skunk-scores=four'
        self.option_set.add_group('gonzo', ['gz'], gonzo)
        # Interface options (do not count in num_options)
        self.option_set.add_group('fast', 'auto-go auto-score no-cut no-pick')
        self.option_set.add_option('auto-go', ['ag'],
            question = 'Should prompts be skipped when you must go? bool')
        self.option_set.add_option('auto-score', ['as'],
            question = 'Should prompts be skipped when players score? bool')
        self.option_set.add_option('no-cut', ['!c'],
            question = 'Should cutting the deck be skipped? bool')
        self.option_set.add_option('no-pick', ['!p'],
            question = 'Should picking cards for first deal be skipped? bool')

    def set_up(self):
        """Set up the game. (None)"""
        # Set the players.
        random.shuffle(self.players)
        # set up the tracking variables.
        self.phase = 'deal'
        self.card_total = 0
        self.go_count = 0
        self.match_scores = {player.name: 0 for player in self.players}
        self.double_pairs = False
        self.skip_player = None
        # Set up the deck.
        self.deck = cards.Deck()
        self.deck.shuffle()
        # Set up the hands.
        self.hands = self.deck.player_hands(self.players)
        self.hands['The Crib'] = cards.Hand(deck = self.deck)
        self.in_play = self.deck.player_hands(self.players)
        self.in_play['Play Sequence'] = cards.Hand(deck = self.deck)
        # Pick the dealer.
        if self.no_pick:
            random.shuffle(self.players)
            self.dealer_index = -1
        else:
            players = self.players[:]
            while True:
                # Have every player pick a card.
                cards_picked = []
                for player in players:
                    query = '\nEnter a number to pick a card: '
                    card_index = player.ask_int(query, cmd = False, default = 0)
                    card = self.deck.pick(card_index)
                    self.human.tell('{} picked the {:n}.'.format(player, card))
                    self.deck.discard(card)
                    cards_picked.append((card.rank_num, player))
                # Determine the highest rank.
                cards_picked.sort(reverse = True)
                # Sort players by card, no tie for winner.
                self.players[:len(cards_picked)] = [player for card, player in cards_picked]
                if cards_picked[0][0] == cards_picked[1][0]:
                    self.human.tell('Tie! Pick again.')
                    players = [player for card, player in cards_picked if card == cards_picked[0][0]]
                else:
                    break
            self.dealer_index = -1
        self.dealer = self.players[self.dealer_index]
        # Set up teams.
        self.teams = {player: [player.name] for player in self.players}
        if self.partners:
            self.human.tell('\nThe teams are:')
            num_teams = len(self.players) // 2
            for player_index, player in enumerate(self.players[:num_teams]):
                team_mate = self.players[player_index + num_teams]
                team = [player, team_mate]
                self.teams[player] = team
                self.teams[team_mate] = team
                self.human.tell('{} and {}'.format(player, team_mate))

    def show_match(self):
        """Show the match scores. (None)"""
        self.human.tell('\nMatch Scores\n----- ------')
        for name in sorted(player.name for player in self.players):
            self.human.tell('{}: {}'.format(name, self.match_scores[name]))
        self.human.tell()


class CribBot(player.Bot):
    """
    A bot for playing Cribbage. (player.Bot)

    Methods:
    get_discard: Determine which card to discard to the crib. (str)
    get_play: Get a card to play. (str)
    score_discards: 'Score' a potential set of descards. (float)
    score_four: Score a potential set of kept cards. (int)

    Overridden Methods:
    ask
    ask_int
    tell
    """

    def ask(self, query):
        """
        Respond to a question from the game. (str)

        Parameters:
        query: The question the game asked. (str)
        """
        # Pass when you can't play.
        if 'no playable' in query:
            self.game.human.tell('\n{} calls "go."'.format(self))
            return ''
        # Press enter.
        elif query.startswith('Please press enter'):
            return ''
        # Raise error on unknown question.
        else:
            raise player.BotError('Unexepected question to CribBot: {!r}'.format(query))

    def ask_card(self, prompt, valid = [], default = None, cmd = True):
        """
        Get a card from the player. (cards.Card)

        Parameters:
        prompt: The question asking for the card. (str)
        valid: The valid values for the card. (container of cards.Card)
        default: The default choice. (cards.Card or None)
        cmd: A flag for returning commands for processing. (bool)
        """
        # Play a card for pegging.
        if 'play' in prompt:
            return self.get_play()
        # Raise error on unknown question.
        else:
            raise player.BotError('Unexepected question to CribBot: {!r}'.format(query))

    def ask_card_list(self, prompt, valid = [], valid_lens = [], default = None, cmd = True):
        """
        Get a multiple card response from the human. (int)

        Parameters:
        prompt: The question asking for the card. (str)
        valid: The valid values for the cards. (list of int)
        valid_lens: The valid numbers of values. (list of int)
        default: The default choice. (list or None)
        cmd: A flag for returning commands for processing. (bool)
        """
        # Discard a card.
        if 'discard' in prompt:
            return self.get_discard()
        # Raise error on unknown question.
        else:
            raise player.BotError('Unexepected question to CribBot: {!r}'.format(query))


    def ask_int(self, prompt, low = None, high = None, valid = [], default = None, cmd = True):
        """
        Get an integer response from the human. (int)

        Parameters:
        prompt: The question asking for the interger. (str)
        low: The lowest acceptable value for the integer. (int or None)
        high: The highest acceptable value for the integer. (int or None)
        valid: The valid values for the integer. (container of int)
        default: The default choice. (int or None)
        cmd: A flag for returning commands for processing. (bool)
        """
        # Handle picking cards and cutting the deck.
        if prompt.strip().startswith('Enter a number'):
            return random.randint(1, 121)
        # Raise an error for anything else.
        else:
            raise player.BotError('Unexepected question to CribBot: {!r}'.format(prompt))

    def get_discard(self):
        """Determine which card to discard to the crib. (str)"""
        # Check current game information.
        hand = self.game.hands[self]
        dealer = (self == self.game.players[self.game.dealer_index])
        # Get the possible discard.
        possibles = []
        for keepers in itertools.combinations(hand, len(hand) - self.game.discards):
            discards = [card for card in hand if card not in keepers]
            # Rate discard based on being the dealer and optional rules.
            if dealer and self.game.solo:
                score = self.score_four(keepers) + self.score_four(discards)
            elif dealer:
                score = self.score_four(keepers) + self.score_discards(discards)
            else:
                score = self.score_four(keepers) - self.score_discards(discards)
            possibles.append((score, discards))
        # Discard the highest rated batch.
        possibles.sort(reverse = True)
        return possibles[0][1]

    def get_play(self):
        """Get a card to play. (str)"""
        # Get the playable cards.
        hand = self.game.hands[self]
        playable = [card for card in hand if 31 - card >= self.game.card_total]
        playable.sort()
        # Get the highest scoring play (randomly break ties)
        plays = [(self.game.score_sequence(self, card), card) for card in playable]
        plays.sort(reverse = True)
        best_plays = [play for play in plays if play[0] == plays[0][0]]
        if plays[0][0]:
            play = random.choice(best_plays)[1]
        # Check for the running total being under 15.
        elif self.game.card_total < 15:
            # Get the resulting card total for each card.
            points = [(card + self.game.card_total, card) for card in playable]
            points.sort()
            # Assume they will hoard 5's and 10's.
            no_15 = [card for total, card in points if total not in (5, 10)]
            # If you can, make 15 impossible on the next play.
            if points[0][0] < 5:
                play = points[0][1]
            elif points[-1][0] > 15:
                play = points[-1][1]
            # Otherwise make it as hard as you can.
            elif no_15:
                play = no_15[0]
            else:
                play = playable[-1]
        else:
            # If all else fails, play your biggest card.
            play = playable[0]
        # Make the play.
        self.game.human.tell('\n{} played the {:n}.'.format(self.name, play))
        return play

    def score_discards(self, cards):
        """
        'Score' a potential set of descards. (float)

        The score given here is a postive rating of how bad an idea it is to
        discard those card(s).

        Parameters:
        cards: The cards to score. (list of Card)
        """
        score = 0
        # Account for scoring cards.
        if len(cards) == 2:
            if sum(cards) == 15 or cards[0].rank == cards[1].rank:
                score += 2
            if abs(cards[0] - cards[1]) == 1:
                score += 0.75
            if cards[0].suit == cards[1].suit:
                score += 0.25
        # Account for potentially scoring cards.
        ranks = sorted([card.rank for card in cards])
        score += (ranks.count('5') + ranks.count('J')) / 2.0
        if ranks in (['4', 'A'], ['6', '8'], ['6', '9'], ['7', '9']):
            score += 0.5
        return score

    def score_four(self, cards):
        """
        Score a potential set of kept cards. (int)

        Parameters:
        cards: The cards to score. (list of Card)
        """
        score = self.game.score_flush(cards) + self.game.score_fifteens(cards)
        score += sum([pair_score for rank, count, pair_score in self.game.score_pairs(cards)])
        score += sum([run_length * run_count for run_length, run_count in self.game.score_runs(cards)])
        return score

    def tell(self, message = ''):
        """
        The the bot some information. (None)

        Parameters:
        message: The information to tell the bot. (str)
        """
        if isinstance(message, Cribbage):
            pass
        else:
            super(CribBot, self).tell(message)

def skunk_check(setting):
    """
    Check a skunk-scores option setting. (bool)

    Parameters:
    setting: The option setting to check. (str)
    """
    if setting in ('acc', 'long', 'free', 'four'):
        return True
    else:
        if len(setting) != 3:
            return False
        return(all(num.isdigit() for num in setting))