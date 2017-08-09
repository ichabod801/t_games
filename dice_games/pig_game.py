"""
pig_game.py

Pig and related variants.
"""


import dice
import game
import player
import re


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

    def set_up(self):
        """Set up the game. (None)"""
        self.die = Dice.die()
        self.bot = PigBotValue(21)
        self.players = [self.bot, self.human]
        super(Pig, self).set_up()

    def player_turn(self, player):
        turn_score = 0
        while True:
            roll = self.die.roll()
            if roll == 1:
                player.tell('You rolled a 1, your turn is over.')
                break
            else:
                turn_score += roll
                player.tell('You rolled a {}, your turn score is {}.')
            move = player.ask('Would you like to roll or stop? ')
            if move.lower() in ('s', 'stop', 'whoa'):
                self.scores[player.name] += turn_score
                break

class PigBot(player.Bot):

    number_re = re.compile('\d+')

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
        if 'your turn is over' in text:
            self.turn_score = 0

