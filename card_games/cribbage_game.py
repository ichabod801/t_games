"""
cribbage_game.py

A game of Cribbage.

Constants:
Credits: The credits for Cribbage. (str)

Classes:
Cribbage: A game of Cribbage. (game.Game)
"""


import collections
import random


import tgames.cards as cards
import tgames.game as game
import tgames.player as player


CREDITS = """
Game Design: John Suckling
Game Programming: Craig "Ichabod" O'Brien
"""


class Cribbage(game.Game):
    """
    A game of Cribbage. (game.Game)

    !! needs game over and reset for redeals.

    Attributes:
    cards_played: The cards played so far this round. (str)
    deck: The deck of cards used in the game. (cards.Deck)
    hands: The player's hands in the game. (dict of str: cards.Hand)
    in_play: The cards each player has played. (dict of str: cards.Hand)
    starter: The starter card. (cards.Card)
    """

    aka = ['Crib']
    categories = ['Card Game', 'Matching Game']
    credits = CREDITS
    name = 'Cribbage'

    def __str__(self):
        """Human readable text representation. (str)"""
        lines = ['\nScores\n------\n']
        for player in self.players:
            lines.append('{}: {}'.format(player.name, self.scores[player.name]))
        lines.append('\nRunning Total: {}'.format(self.card_total))
        player = self.players[self.player_index]
        hand = self.hands[player.name]
        lines.append('\nCards in Hand: {}.'.format(hand.show_player()))
        lines.append('\nCards played: {}\n'.format(self.cards_played))
        return '\n'.join(lines)

    def deal(self):
        """Deal the cards. (None)"""
        # Reset the tracking variables.
        self.card_total = 0
        self.go_count = 0
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
        self.player_index = (self.dealer_index + 1) % len(self.players)
        print('The current dealer is {}.'.format(dealer.name))
        # Deal the cards
        hand_size = [0, 0, 6, 5, 5][len(self.players)]
        for card in range(hand_size):
            for player in self.players:
                self.hands[player.name].draw()
        if len(self.players) == 3:
            self.hands['The Crib'].draw()
        self.starter = self.deck.deal(up = True)
        self.cards_played = str(self.starter)
        # Check for heels.
        if self.starter.rank == 'J':
            print ('The dealer got his heels.')
            self.scores[dealer.name] += 2
            if self.scores[dealer.name] >= self.target_score:
                self.force_win
                return False

    def game_over(self):
        """Check for the end of the game. (None)"""
        if max(self.scores.values()) >= self.target_score:
            # Determine the winner.
            scores = [(score, name) for name, score in self.scores.items()]
            scores.sort(reverse = True)
            self.human.tell('{1} wins with {0} points.'.format(*scores[0]))
            # Calcualte win/loss/draw stats.
            wld_index = 1
            for score, name in scores:
                if name == self.human.name:
                    wld_index = 0
                else:
                    self.win_loss_draw[wld_index] += 1
            return True
        else:
            return False

    def player_action(self, player):
        """
        Allow the player to do something.

        Parameters:
        player: The current player. (player.Player)
        """
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
        discard_word, s = [('', ''), ('two', 's')][self.discard_size != 1]
        query = 'Which {} card{} would you like to discard to the crib, {}? '
        answer = player.ask(query.format(discard_word, s, player.name))
        discards = cards.Card.card_re.findall(answer)
        if not discards:
            return self.handle_cmd(answer)
        elif len(discards) != self.discard_size:
            player.error('You must discard {} card{}.'.format(discard_word, s))
            return True
        elif not all(card in self.hands[player.name] for card in discards):
            player.error('You do not have all of those cards in your hand.')
            return True
        else:
            for card in discards:
                self.hands[player.name].shift(card, self.hands['The Crib'])
            if len(self.hands['The Crib']) == 4:
                self.phase = 'play'
            return False

    def player_play(self, player):
        """
        Allow the player to play a card.

        Parameters:
        player: The current player. (player.Player)
        """
        hand = self.hands[player.name]
        in_play = self.in_play[player.name]
        answer = player.ask('Which card would you like to play, {}? '.format(player.name))
        card = CribCard.card_re.match(answer)
        if answer.lower() == 'go':
            if min([card.value for card in hand]) <= 31 - self.card_total:
                message = 'You must play any cards under rank {} before you can pass.'
                player.error(message.format(32 - self.card_total))
                return True
            else:
                self.go_count += 1
                if self.go_count == len(self.players):
                    self.human.tell('Everyone has passed.')
                    self.scores[player.name] += 1
                    self.human.tell('{} scores 1 for the go.'.format(player.name))
                    self.score_hands()
                return False
        elif card:
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
                self.score_sequence(player)
                self.card_total += card
                self.go_count = 0
                if self.card_total == 31:
                    self.human.tell('The count has reached 31.')
                    self.score_hands()
                return False
        else:
            return self.handle_cmd(answer)

    def score_hands(self):
        """Score the hands after a round of play. (None)"""
        # ?? refactor?
        # Loop through the players, starting on the dealer's left.
        player_index = (self.dealer_index + 1) % len(self.players)
        names = [player.name for player in self.players[player_index:] + self.players[:player_index]]
        for name in names + ['The Crib']:
            # Score the crib to the dealer.
            if name == 'The Crib':
                cards = self.hands['The Crib'].cards
                name = self.players[self.dealer_index].dealer
                self.human.tell('Now scoring the crib for the dealer ({}).'.format(name))
            else:
                cards = self.hands[name].cards + self.in_play[name].cards
            # Check for flushes. (four in hand or five with starter)
            suits = set([card.suit for card in cards])
            if len(suits) == 1:
                if self.starter.suit in suits:
                    size = 5
                else:
                    size = 4
                # !! Crib can't score 4 flush.
                message = '{} scores {} points for a {}-card flush.'
                self.human.tell(message.format(name, size, size))
            # Check for his nobs (jack of suit of starter)
            nob = CribCard('J', self.starter.suit)
            if nob in cards:
                self.scores[name] += 1
                self.human.tell('{} scores one for his nob.'.format(name))
            # Add the starter for the scoring categories below.
            cards.append(self.starter)
            # Check for 15s.
            fifteens = 0
            for size in range(2, 6):
                for cards in itertools.combinations(cards, size):
                    if sum(cards) == 15:
                        fifteens += 1
            if fifteens:
                self.scores[name] += 2 * fifteens
                message = '{} scores {} for {} combinations adding to 15.'
                self.human.tell(message.format(name, 2 * fifteens, fifteens))
            # Check for pairs.
            rank_counts = collections.Counter([card.rank for card in cards])
            for rank, count in rank_counts.most_common():
                if count < 2:
                    break
                pair_score = utility.choose(count, 2) * 2
                self.scores[name] += pair_score
                message = '{} scores {} for getting {} cards of the same rank.'
                self.human.tell(message.format(name, pair_score, count))
            # Check for runs.
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
            # Score any runs that occurred.
            if len(run) > 1 and run.count(1) > 1:
                # Check pair count to determine the number of runs.
                pairs = [index for index, diff in enumerate(run) if diff == 0]
                run_count = [1, 2, 4][len(pairs)]
                # Adjust for three of a kind as opposed to two pair.
                if len(pairs) == 2 and pairs[1] - pairs[0] == 1:
                    run_count = 3
                # Update the score.
                run_length = len(run) + 1
                self.scores[name] += run_length * run_count
                # Update the user.
                if run_count == 1:
                    message = '{0} scored {1} points for a {1} card run.'
                else:
                    message = '{0} scored {3} points for {2} runs of length {1}.'
                self.human.tell(message.format(name, run_length, run_count, run_length * run_count))
            # Check for a win before scoring the dealer/crib.
            if self.scores[name] >= self.target_score:
                self.human.tell('{} has won with {} points.'.format(name, self.scores[name]))
                break

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
            self.player.tell('{} scores 2 points for reaching 15.'.format(player.name))
        # Count the cards of the same rank.
        rank_count = 1
        for play_index in range(-2, -5, -1):
            if played[play_index]cards.rank != played[-1]cards.rank:
                break
            rank_count += 1
        # Score any pairs.
        if rank_count > 1:
            pair_score = utility.choose(rank_count, 2) * 2
            self.scores[player.name] += pair_score
            message = '{} scores {} for getting {} cards of the same rank.'
            self.player.tell(message.format(player.name, pair_score, rank_count))
        # Check for runs.
        run_index = -3
        run_count = 0
        while True:
            values = sorted([card.value for card in played.cards[run_index:]])
            diffs = [second - first for first, second in zip(values, values[1:])]
            if all([diff == 1 for diff in diffs]):
                run_index -= 1
                run_count = len(values)
            else:
                break
        # Score any runs.
        if run_count:
            self.scores[player.name] += run_count
            message = '{0} scores {1} for getting a {1}-card straight.'
            self.player.tell(message.format(player.name, run_count))

    def set_up(self):
        """Set up the game. (None)"""
        # Set the players.
        self.players = [self.human, player.Cyborg([self.human.name])]
        random.shuffle(self.players)
        # set up the tracking variables.
        self.phase = 'discard'
        self.discard_size = [0, 0, 2, 1, 1][len(self.players)]
        self.dealer_index = -1
        self.target_score = 161
        self.skunk = 61
        # Set up the deck.
        self.deck = cards.Deck(card_class = CribCard)
        # Set up the hands.
        self.hands = {player.name: cards.Hand(self.deck) for player in self.players}
        self.hands['The Crib'] = cards.Hand(self.deck)
        self.in_play = {player.name: cards.Hand(self.deck) for player in self.players}
        self.in_play['Play Sequence'] = cards.Hand(self.deck)
        self.deal()


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


if __name__ == '__main__':
    try:
        input = raw_input
    except NameError:
        pass
    name = input('What is your name? ')
    crib = Cribbage(player.Player(name), '')
    crib.play()