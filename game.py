"""
game.py
"""

import itertools
import random

from player import Player

class Game(object):

    aka = []
    categories = ['Test Games', 'Solitaire']
    help = {}
    name = 'Null'
    rules = 'Make whatever move you want. Whether or not you win is random.'

    def __init__(self, human, options):
        self.human = human
        self.raw_options = options
        self.handle_options()
        self.win_loss_draw = [0, 0, 0]
        self.turns = 0

    def clean_up(self):
        self.scores[self.human.name] = -self.turns

    def game_over(self):
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