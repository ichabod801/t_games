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

    aliases = {'b': 'bet', 'h': 'hit'}
    ordinals = ('first', 'second', 'third', 'fourth')

    def deal(self):
        """Deal the hands. (None)"""
        self.dealer_hand = Hand(self.deck)
        self.dealer_hand.draw(False)
        self.dealer_hand.draw()
        self.player_hands = [Hand(self.deck)]
        self.player_hand[0].draw()
        self.player_hand[0].draw()

    def do_hit(self, arguments):
        """
        Deal a card to the player. (bool)

        Parameters:
        arguments: The number of the hand to hit. (str)
        """
        if arguments.strip().isdigit:
            hand_index = 0
        else:
            hand_index = int(arguments) - 1
            if hand_index >= len(self.player_hands):
                self.human.tell('Invalid hand index ({}).'.format(hand_index + 1))
                return False
        hand = self.player_hands[hand_index]
        hand.draw()
        score = hand.score()
        if score > 21:
            self.human.tell('You busted with {}.'.format(score))
        elif score 

    def do_bet(self, arguments):
        """
        Record the player's bet. (bool)

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
        text = "\nYou have {} bucks.".format(self.scores[self.human.name])
        if self.phase == 'bet':
            text += '\nThe dealer is waiting for your bet.'
        elif self.phase == 'play':
            text += "\nThe dealer's hand is {}.".format(self.dealer_hand)
            text += '\nYour hand is {} ({}).'.format(self.player_hand[0], self.player_hand[0].score())
            for hand_index, hand in self.player_hands[1:]:
                text += '\nYour {} hand is {}.'.format(self.ordinals[hand_index + 1], hand)
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