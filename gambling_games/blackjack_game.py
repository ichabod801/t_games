"""
blackjack_game.py

Blackjack.

Classes:
Blackjack: A game of Blackjack. (game.Game)
Blackjack: A hand of Blackjack. (cards.Hand)
"""


import tgames.cards as cards
import tgames.game as game


class Blackjack(game.Game):
    """
    A game of Blackjack. (game.Game)
    """

    def do_bet(self, arguments):
        """
        Handle bets.

        Parameters:
        arguments: The amount bet. (str)
        """
        if self.phase != 'bet':
            self.human.tell('You have already bet this hand.')
        elif not arguments.strip().isdigit():
            self.human.tell('Invalid bet ({}).'.format(arguments))
        elif self.limit and int(arguments) > self.limit:
            self.human.tell('The betting limit is {} bucks.'.format(self.limit))
        elif int(arguments) > self.score[self.human.name]:
            self.human.tell('You only have {} bucks left to bet.'.format(self.score[self.human.name]))
        else:
            self.bet = int(arguments)
            self.score[self.human.name] -= self.bet
            self.deal()
            self.phase = 'play'

    def handle_options(self):
        """Handle the game options. (None)"""
        self.stake = 100
        self.limit = 5
        self.decks = 4
        self.bet = 0

    def player_turn(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        self.show_status()
        move = self.human.ask("What's your play? ")
        return self.handle_cmd(move)

    def set_up(self):
        """Set up the game. (None)"""
        self.scores = {self.human.name: self.stake}
        self.deck = Deck(decks = self.decks)
        self.phase = 'bet'

    def show_status(self):
        """Show the current game situation to the player. (None)"""
        if self.phase == 'bet':
            text = 'You have {} bucks. The dealer is waiting for your bet.'
            text.format(self.scores[self.human.name])
        elif self.phase == 'play':
            text = '???'
        self.human.tell(text)


class BlackjackHand(cards.Hand):
    """
    A hand of Blackjack. (cards.Hand)

    Class Attributes:
    card_values: A mapping of card ranks to score values. (dict of str: int)

    Attributes:
    soft: A flag for the hand being soft (ace = 11).

    Overridden Methods:
    score
    """

    card_values = dict(zip('23456789TAJQK', list(range(2, 12)) + [10] * 3))

    def score(self):
        """Score the hand. (int)"""
        score = sum([card_values[card.rank] for card in self.cards])
        if score > 21:
            ace_count = len([card for card in self.cards if card.rank == 'A'])
            while score > 21 and ace_count:
                score -= 10
                ace_count -= 1
                self.soft = False
        else:
            self.soft = True
        return score