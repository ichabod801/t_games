"""
pig_game.py

Pig and related variants.
"""

from __future__ import print_function

import dice
import game
import player
import random


class Pig(game.Game):
    """
    A game of pig. (Game)
    """

    name = 'Pig'
    categories = ['Dice Games']

    def game_over(self):
        if max(self.scores.values()) > 99:
            human_score = self.scores[self.human.name]
            for name, score in self.scores.items():
                if score > 99:
                    self.human.tell('{} won with {} points.'.format(name, score))
                if name != self.human.name:
                    if score > human_score:
                        self.win_loss_draw[1] += 1
                    elif score < human_score:
                        self.win_loss_draw[0] += 1
                    else:
                        self.win_loss_draw[2] += 1
            return True

    def handle_options(self):
        """Handle game options and set up players. (None)"""
        self.bot = PigBotValue(taken_names = [self.human.name])
        self.players = [self.bot, self.human]
        random.shuffle(self.players)

    def set_up(self):
        """Set up the game. (None)"""
        self.die = dice.Die()
        super(Pig, self).set_up()

    def player_turn(self, player):
        self.turn_score = 0
        while True:
            roll = self.die.roll()
            if roll == 1:
                player.tell('You rolled a 1, your turn is over.')
                break
            else:
                self.turn_score += roll
                player.tell('You rolled a {}, your turn score is {}.'.format(roll, self.turn_score))
            move = player.ask('Would you like to roll or stop? ')
            if move.lower() in ('s', 'stop', 'whoa'):
                self.scores[player.name] += self.turn_score
                break
        player.tell("{}'s score is now {}".format(player.name, self.scores[player.name]))
        print()


class PigBot(player.Bot):

    def __init__(self, taken_names = [], initial = ''):
        """
        Set the bot's name. (None)

        If initial is empty, the bot's name can start with any letter.

        Parameters:
        taken_names: Names already used by a player. (list of str)
        initial: The first letter of the bot's name. (str)
        """
        super(PigBot, self).__init__(taken_names, initial)
        self.scores = {}
        self.turn_score = 0

    def ask(self, prompt):
        return random.choice(('yes', 'no'))

    def tell(self, text):
        out = text.replace('your', 'their').replace('You', self.name)
        print(out)


class PigBotValue(PigBot):

    def __init__(self, value = 21, taken_names = []):
        super(PigBotValue, self).__init__(taken_names, 'v')
        self.value = value

    def ask(self, prompt):
        if self.game.turn_score < self.value:
            return 'roll'
        else:
            return 'stop'


if __name__ == '__main__':
    name = input('What is your name? ')
    pig = Pig(player.Player(name))
    pig.play()