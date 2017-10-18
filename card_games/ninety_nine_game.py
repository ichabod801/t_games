"""
ninety_nine_game.py

This is the accumulating game, not the trick taking game.

Constants:
CREDITS: The credits for Ninety-Nine. (str)
RULES: The rules of Ninety-Nine.

Classes:
NinetyNine: A game of Ninety-Nine. (game.Game)
Bot99: A bot for Ninety-Nine. (player.Bot)
"""


import tgames.cards as cards
import tgames.game as game
import tgames.player as player


CREDITS = """
Game Design: Traditional (Romani)
Game Programming: Craig "Ichabod" O'Brien
"""

RULES = """
Each turn you play a card, adding it's value to the running total. If you 
can't play a card without taking the total over 99, you must pass, and lose
one of your three tokens. At that point the hands are redealt and the total
is reset to zero. If you lose all of your tokens, you are out of the game.
The last player with tokens wins.

Cards are face value with face cards being 10, with the following exceptions:
    A: 1 or 11
    4: 0
    10: -10 or 10
    K: 0

In addition, a 4 reverses the order of play and a 3 skips the next player's 
turn.
"""


class NinetyNine(game.Game):
    """
    A game of Ninety-Nine. (game.Game)

    Attributes:
    card_values: The possible values for each rank. (dict of str: tuple)
    deck: The deck of cards for the game. (cards.Deck)
    hands: The players hands of cards, keyed by name. (dict of str:cards.Hand)
    reverse_rank: The rank that reverses the order of play. (str)
    skip_rank: The rank that skips over a player. (str)
    total: The current total rank count. (int)

    Methods:
    deal: Deal a new hand of cards. (None)
    do_pass: Handle passing the turn. (bool)

    Overridden Methods:
    do_quit
    handle_options
    player_turn
    set_up
    """

    aliases = {'p': 'pass'}
    credits = CREDITS
    name = 'Ninety-Nine'
    rules = RULES

    def deal(self):
        """Deal a new hand of cards. (None)"""
        for hand in self.hands.values():
            hand.discard()
        deck.shuffle()
        for card in range(3):
            for hand in self.hands.values():
                hand.draw()

    def do_pass(self, arguments):
        """
        Handle passing the turn. (bool)

        Parameters:
        arguments: The ignored arguments to the command. (None)
        """
        player = self.players[self.player_index]
        self.scores[player.name] -= 1
        message = '{} loses a token. They now have {} tokens.'
        self.human.tell(message.format(player.name, self.scores[player.name]))
        self.deal()
        self.total = 0

    def do_quit(self, arguments):
        """
        Quit the game, which counts as a loss. (bool)

        Overridden due to changing self.players over course of the game.

        Parameters:
        arguments: The modifiers to the quit. (str)
        """
        self.flags |= 4
        self.force_end = 'loss'
        self.win_loss_draw = [0, max(len(self.scores) - 1, 1), 0]
        if arguments.lower() in ('!', 'quit', 'q'):
            self.human.held_inputs = ['!']
        return False

    def game_over(self):
        """Check for the game being over. (bool)"""
        for player in self.players:
            if not self.scores[player.name]:
                self.scores[player.name] = min(self.scores.values()) - 1
        self.players = [player for player in self.players if self.scores[player.name] > 0]
        if in_game == 1:
            human_score = self.scores[self.human.name]
            for score in self.scores.values():
                if score < human_score:
                    self.win_loss_draw[0] += 1
                elif score > human_score:
                    self.win_loss_draw[1] += 1
            return True
        else:
            return False

    def handle_options(self):
        """Handle the game options(None)"""
        # Set default options.
        self.card_values = {rank: (rank_index,) for rank_index, rank in cards.Card.ranks}
        self.card_values['A'] = (1, 11)
        self.card_values['4'] = (0,)
        self.card_values['9'] = (99,) # go to 99
        self.card_values['T'] = (-10, 10)
        self.card_values['J'] = (10,)
        self.card_values['Q'] = (10,)
        self.card_values['K'] = (0,)
        self.reverse_rank = '4'
        self.skip_rank = '3'

    def player_turn(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        hand = self.hands[player.name]
        move = player.ask('What is your move? ')
        card, space, new_total = move.partition(' ')
        card = card.upper()
        if card in hand.cards:
            try:
                new_total = int(new_total)
            except:
                player.tell('Invalid total provided.')
            else:
                values = self.card_values[card[0]]
                if new_total - total in values or (new_total == 99 and 99 in values): 
                    hand.discard(card)
                    self.human.tell('{} plays the {}.'.format(player.name, card))
                    self.total = new_total
                    if card[0] == self.reverse_rank:
                        self.players.reverse()
                        self.player_index = self.players.index(player)
                        self.human.tell('The order of play is reversed.')
                    if card[0] == self.skip_rank:
                        self.player_index = (self.player_index + 1) % len(self.players)
                        name = self.players[self.player_index].name
                        self.human.tell("{}'s turn is skipped.".format(name))
                    hand.draw()
                    return False
                else:
                    player.tell('Incorrect value provided.')
        else:
            return self.handle_cmd(move)
        return True

    def set_up(self):
        """Set up the game. (None)"""
        # Hand out tokens.
        self.scores = {player.name: 3 for player in self.players}
        # Set up deck and hands.
        self.deck = cards.Deck()
        self.hands = {player.name: cards.Hand() for player in self.players}
        # Deal three cards to each player.
        self.deal()
        # Set the tracking variables
        self.total = 0


class Bot99(player.Bot):
    """
    A bot for Ninety-Nine. (player.Bot)

    Overridden Methods:
    ask
    """

    def ask(self, prompt):
        """
        Get information from the player. (str)

        Parameters:
        prompt: The information to get from the player. (str)
        """
        hand = self.game.hands[self.name]
        total = self.game.total
        possibles = []
        for card in hand:
            for value in self.game.card_values[card.rank]:
                if total + value < 100:
                    possibles.append((total + value, card))
                elif value == 99:
                    possibles.append((99, card))
        if possibles:
            possibles.sort()
            return str(possibles[0][1])
        else:
            return 'pass'