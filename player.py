"""
player.py

Base player classes for tgames.

Classes:
Player: The base player class. (object)
Human: A human being, with stored data. (Player)
"""

from __future__ import print_function

import os
import sys


if sys.version_info[0] == 2:
    input = raw_input
    

class Player(object):
    """
    The base player class. (object)

    Attributes:
    name: The name of the player. (str)

    Methods:
    ask: Get information from the player. (str)
    tell: Give information to the player. (None)

    Overridden Methods:
    __init__
    """

    def __init__(self, name):
        """
        Save the player's name. (None)

        Parameters:
        name: The name of the player. (str)
        """
        self.name = name

    def ask(self, prompt):
        """
        Get information from the player. (str)

        Parameters:
        prompt: The question being asked of the player. (str)
        """
        return input(prompt)

    def tell(self, *args, **kwargs):
        """
        Give information to the player. (None)

        Parameters:
        The parameters are as per the built-in print function.
        """
        print(*args, **kwargs)


class Human(Player):
    """
    A human being, with stored data. (Player)

    Attributes:
    color: The player's favorite color. (str)
    folder_name: The local folder with the player's data. (str)
    quest: The player's quest. (str)

    Overridden Methods:
    __init__
    """

    def __init__(self):
        while True:
            # Get the user's name.
            self.name = input('What is your name? ')
            # Allow for single or multiple entry of quest and color.
            if ';' in self.name:
                self.name, self.quest, self.color = [word.strip() for word in self.name.split(';')]
            else:
                self.quest = input('What is your quest? ')
                self.color = input('What is your favorite color? ')
            # Check for previous log in.
            self.folder_name = 'player_data/{}-{}-{}/'.format(self.name, self.quest, self.color)
            if not os.path.exists(self.folder_name):
                new_player = input('I have not heard of you. Are you a new player? ')
                if new_player.lower() in ('yes', 'y', '1'):
                    os.mkdir(self.folder_name)
                    break
                print()
            else:
                break