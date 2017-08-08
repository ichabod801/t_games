"""
game.py

The base game object for tgames.

Classes:
Game: A game with a text interface. (object)
"""

import itertools
import random

from player import Player

class Game(object):
    """
    A game with a text interface. (object)

    !! needs a way to check for commands like help, rules, and so on.

    Class Attributes:
    aka: Other names for the game. (list of str)
    categories: The categories of the game. (list of str)
    help: The help text for the game. (dict of str: str)
    name: The primary name of the game. (str)
    rules: The rules of the game. (str)

    Attributes:
    human: The primary player of the game. (Player)
    raw_options: The options as given by the play command. (str)
    scores: The players' scores in the game. (dict of str: int)
    turns: The number of turns played in the game. (int)
    win_loss_draw: A list of the player's results in the game. (list of int)

    Methods:
    clean_up: Handle any end of game tasks. (None)
    game_over: Check for the end of the game. (bool)
    handle_options: Handle any options for the game. (None)
    play: Play the game. (list of int)
    player_turn: Handle a player's turn or other player actions. (bool)
    set_up: Handle any pre-game tasks. (None)

    Overridden Methods:
    __init__
    """

    aka = []
    categories = ['Test Games', 'Solitaire']
    help = {}
    name = 'Null'
    rules = 'Make whatever move you want. Whether or not you win is random.'

    def __init__(self, human, options):
        """Set up the game. (None)"""
        self.human = human
        self.raw_options = options
        self.handle_options()

    def clean_up(self):
        """Handle any end of game tasks. (None)"""
        self.scores[self.human.name] = -self.turns

    def game_over(self):
        """Check for the end of the game. (bool)"""
        roll = random.randint(1, 3)
        if roll == 1:
            self.human.tell('You lose.')
            self.win_loss_draw[1] = 1
        elif roll == 2:
            self.human.tell('Keep playing.')
        else:
            self.human.tell('You win.')
            self.win_loss_draw[0] = 1
        return sum(self.win_loss_draw)

    def handle_options(self):
        """Handle any options for the game. (None)"""
        pass

    def play(self):
        """
        Play the game. (list of int)

        The return value is the win, loss, draw, and score for the primary player.
        The win/loss/draw is per player for one game. So if you tie for second 
        with five players, your win/loss/draw is 2, 1, 1.
        """
        # Set up the game.
        self.set_up()
        # Loop through the players repeatedly.
        for player in itertools.cycle(self.players):
            # Loop through player actions until their turn is done.
            while self.player_turn(player):
                pass
            # Update tracking.
            self.turns += 1
            # Check for the end of game.
            if self.game_over():
                break
        # Clean up the game.
        self.clean_up()
        # Report the results.
        return self.win_loss_draw + [self.scores[self.human.name]]

    def player_turn(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        The return value is a flag for the player's turn being done.

        Parameters:
        player: The player whose turn it is. (Player)
        """
        move = player.ask('What is your move, {}? '.format(player.name))

    def set_up(self):
        """Handle any pre-game tasks. (None)"""
        self.players = [self.human]
        self.scores = {self.human.name: 0}
        self.win_loss_draw = [0, 0, 0]
        self.turns = 0

if __name__ == '__main__':
    craig = Player('Craig')
    game = Game(craig, '')
    result = game.play()
    print(result)