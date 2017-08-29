"""
rps_game.py

Rock-paper-scissors.

Classes:
RPS: A game of rock-paper-scissors. (Game)
"""


import random

import tgames.game as game
import tgames.player as player
import tgames.utility as utility


class Randy(player.Bot):
    """
    """

    def __init__(self, human_name):
        super(Randy, self).__init__([human_name], initial = 'r')

    def ask(self, prompt):
        if prompt == 'What is your move? ':
            return random.choice(list(self.game.wins.keys()))

    def tell(self, text):
        pass

class RPS(game.Game):
    """
    A game of rock-paper-scissors. (Game)

    """

    aka = ['rps', 'rock paper scissors', 'roshambo']
    categories = ['Other Games', 'Other Games']
    lizard_spock = {'rock': ['scissors', 'lizard'], 'scissors': ['paper', 'lizard'], 
        'paper': ['rock', 'spock'], 'lizard': ['paper', 'spock'], 'spock': ['scissors', 'rock']}
    name = 'Rock-Paper-Scissors'
    wins = {'rock': ['scissors'], 'scissors': ['paper'], 'paper': ['rock']}

    def game_over(self):
        if not self.turns % 2:
            move = self.moves[self.human.name]
            bot_move = self.moves[self.bot.name]
            if move in self.wins[bot_move]:
                self.human.tell('{} beats {}, you lose.'.format(bot_move, move))
                self.win_loss_draw[1] = 1
            if bot_move in self.wins[move]:
                self.human.tell('{} beats {}, you win!'.format(move, bot_move))
                self.win_loss_draw[0] = 1
            else:
                self.human.tell('You both played {}, play again.'.format(move))
                self.win_loss_draw[2] += 1
            self.bot.tell(move)
        return 1 in self.win_loss_draw[:2]

    def handle_options(self):
        self.bot_class = Randy
        if self.raw_options == 'none':
            pass
        elif self.raw_options:
            self.flags |= 1
            if 'lizard-spock' in options:
                self.wins = self.lizard_spock
        else:
            lizard_spock = self.human.ask('Would you like to add lizard and Spock? ')
            if lizard_spock in utility.YES:
                self.flags |= 1
                self.wins = self.lizard_spock

    def player_turn(self, player):
        while True:
            move = player.ask('What is your move? ').lower().strip()
            if move in self.wins:
                break
            else:
                self.handle_cmd(move)

    def set_up(self):
        self.bot = self.bot_class(self.human.name)
        self.players = [self.human, self.bot]
        self.moves = {player.name: '' for player in self.players}


if __name__ == '__main__':
    try:
        input = raw_input
    except NameError:
        pass
    name = input('What is your name? ')
    rps = RPS(player.Player(name), '')
    rps.play()
