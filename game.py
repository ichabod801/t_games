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
        self.win_loss_draw = [0, 0, 0]
        self.turns = 0

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
        self.set_up()
        for player in itertools.cycle(self.players):
            while self.player_turn(player):
                pass
            self.turns += 1
            if self.game_over():
                break
        self.clean_up()
        return self.win_loss_draw + [self.scores[self.human.name]]

    def player_turn(self, player):
        move = player.ask('What is your move, {}? '.format(player.name))

    def set_up(self):
        self.players = [self.human]
        self.scores = {self.human.name: 0}

if __name__ == '__main__':
    craig = Player('Craig')
    game = Game(craig, '')
    result = game.play()
    print(result)