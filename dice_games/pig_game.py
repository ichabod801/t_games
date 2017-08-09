"""
pig_game.py

Pig and related variants.
"""

from __future__ import print_function

import tgames.dice as dice
import tgames.game as game
import tgames.player as player
import random


class Pig(game.Game):
    """
    A game of pig. (Game)

    Attributes:
    die: The die that is rolled. (dice.Die)
    turn_score: The current player's turn score. (int)

    Overridden Methods:
    game_over
    handle_options
    set_up
    player_turn
    """

    name = 'Pig'
    categories = ['Dice Games']

    def game_over(self):
        """Check a score being over 100. (bool)"""
        # Check for win.
        if max(self.scores.values()) > 99:
            # Update win/loss/draw.
            human_score = self.scores[self.human.name]
            for name, score in self.scores.items():
                if name != self.human.name:
                    if score > human_score:
                        self.win_loss_draw[1] += 1
                    elif score < human_score:
                        self.win_loss_draw[0] += 1
                    else:
                        self.win_loss_draw[2] += 1
                # Declare the winner when found.
                if score > 99:
                    self.human.tell('{} won with {} points.'.format(name, score))
            return True

    def handle_options(self):
        """Handle game options and set up players. (None)"""
        self.bot = PigBotValue(taken_names = [self.human.name])
        self.players = [self.bot, self.human]
        random.shuffle(self.players)

    def set_up(self):
        """Set up the game. (None)"""
        self.die = dice.Die()

    def player_turn(self, player):
        """
        Have one player roll until terminal number or they choose to stop. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
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
    """
    A bot for playing the game of Pig. (player.Bot)

    Overridden Methods:
    __init__
    __ask__
    __tell__
    """

    def __init__(self, taken_names = [], initial = ''):
        """
        Set the bot's name. (None)

        Parameters:
        taken_names: Names already used by a player. (list of str)
        initial: The first letter of the bot's name. (str)
        """
        super(PigBot, self).__init__(taken_names, initial)
        self.scores = {}
        self.turn_score = 0

    def ask(self, prompt):
        """
        Get information from the player. (str)

        Parameters:
        prompt: The question being asked of the player. (str)
        """
        return random.choice(('yes', 'no'))

    def tell(self, text):
        """
        Give information to the player. (None)

        Parameters:
        The parameters are as per the built-in print function.
        """
        out = text.replace('your', 'their').replace('You', self.name)
        print(out)


class PigBotValue(PigBot):
    """
    A Pig bot that rolls until it exceeds a certain value. (int)

    Attributes:
    value: The the minimum turn score this bot will stop rolling on. (int)
    """

    def __init__(self, value = 21, taken_names = []):
        """
        Set the bot's value. (None)

        Parameters:
        value: The the minimum turn score this bot will stop rolling on. (int)
        taken_names: Names already used by a player. (list of str)
        """
        super(PigBotValue, self).__init__(taken_names, 'v')
        self.value = value

    def ask(self, prompt):
        """
        Get information from the player. (str)

        Parameters:
        prompt: The question being asked of the player. (str)
        """
        # Stop if the value is met or exceeded.
        if self.game.turn_score < self.value:
            return 'roll'
        else:
            return 'stop'


if __name__ == '__main__':
    try:
        input = raw_input
    except NameError:
        pass
    name = input('What is your name? ')
    pig = Pig(player.Player(name), '')
    pig.play()