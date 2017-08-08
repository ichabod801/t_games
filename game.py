"""
game.py

The base game object for tgames.

Classes:
Game: A game with a text interface. (object)
Sorter: A test game of sorting a sequence. (Game)
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


class Sorter(Game):
    """
    A test game of sorting a sequence. (Game)

    Attributes:
    length: The length of the sequences to sort. (int)
    minimum: The minimum number of swaps to sort the sequence. (int)
    sequence: The sequence to sort. (list of int)

    Overridden Methods:
    handle_options
    player_turn
    set_up
    """

    name = 'Sorter'

    def game_over(self):
        """Check for the game being over. (bool)"""
        # Check for sorted sequences.
        if self.sequence == sorted(self.sequence):
            # Check if it is a win or a loss.
            if self.turns == self.minimum:
                self.win_loss_draw[0] = 1
                self.human.tell('You won!')
            else:
                self.win_loss_draw[1] = 1
                self.human.tell('You lost. The sequence could be sorted in {} swaps.'.format(self.minimum))
            # Set the score and end the game.
            self.scores[self.human.name] = self.minimum - self.turns
            return True

    def handle_options(self):
        """Set the length of the sequence to sort. (None)"""
        # Set the default options
        self.length = 5
        # If no options, ask for manual setting of options.
        if not self.raw_options.strip():
            self.raw_options = self.human.ask('Enter the length of the sequence to sort (return for 5): ')
        # Read any specified options
        if self.raw_options.isdigit():
            self.length = int(self.raw_options)

    def player_turn(self, player):
        """
        Get two numbers to swap. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        # Get the move.
        player.tell('The current sequence is: ', str(self.sequence)[1:-1])
        move = player.ask('Pick two numbers to swap: ')
        # Parse the move.
        try:
            if ',' in move:
                numbers = [int(x) for x in move.split(',')]
            else:
                numbers = [int(x) for x in move.split()]
        except ValueError:
            # Handle invalid moves.
            player.tell('Invalid input. Please enter two numbers separated by a space or a comma.')
            return True
        # Make the move.
        ndxs = [self.sequence.index(x) for x in numbers]
        self.sequence[ndxs[0]], self.sequence[ndxs[1]] = self.sequence[ndxs[1]], self.sequence[ndxs[0]]

    def set_up(self):
        """Set up the sequence and minimum swaps. (None)"""
        # Set up base attributes.
        super(Sorter, self).set_up()
        # Set up the sequence to sort.
        self.sequence = list(range(self.length))
        while self.sequence == sorted(self.sequence):
            random.shuffle(self.sequence)
        # Determine the minimum number of swaps.
        self.minimum = 0
        check = self.sequence[:]
        for num_index, num in enumerate(check):
            if num_index != num:
                target_index = check.index(num_index)
                check[num_index], check[target_index] = check[target_index], check[num_index]
                self.minimum += 1


if __name__ == '__main__':
    craig = Player('Craig')
    game = Game(craig, '')
    result = game.play()
    print(result)