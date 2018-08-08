"""
rps_game.py

Rock-paper-scissors.

Copyright (C) 2018 by Craig O'Brien and the t_game contributors.
See the top level __init__.py file for details on the t_games license.

Constants:
CREDITS: Credits for Rock-Paper-Scissors. (str)
RULES: Rulse for Rock-Paper-Scissors. (str)

Classes:
Bart: Good old rock. Nothing beats rock. (Bot)
Memor: An RPS bot with a memory. (Bot)
Randy: A random RPS bot. (Bot)
Lisa: An anti-Bart bot. (Ramdy)
RPS: A game of rock-paper-scissors. (Game)
"""


import bisect
import os
import random

import t_games.game as game
import t_games.options as options
import t_games.player as player
import t_games.utility as utility


CREDITS = """
Game Design: Traditional
Game Programming: Craig "Ichabod" O'Brien
Special Thanks: Matt Groening
"""

RULES = """
Each player chooses one of rock, paper, or scissors. Rock beats scissors,
paper beats rock, and scissors beats paper. If players choose the same thing,
both players choose again.

If the lizard-spock option is chosen, players may also choose lizard or
Spock. Lizard beats paper and Spock and loses to rock and scissors. Spock
beats scissors and rock and loses to paper and lizard.

Options:
bart: Play against the Bart bot.
lisa: Play against the Lisa bot.
lizard-spock: Add the lizard and Spock moves.
match=: The number of rounds played. Defaults to 1.
memor: Play against the Memor bot (the default)
randy: Play against the Randy bot.
"""


class Bart(player.Bot):
    """
    Good old rock. Nothing beats rock. (Bot)

    Overridden Methods:
    __init__
    ask
    tell
    """

    def __init__(self, taken_names):
        """
        Set up the bot. (None)

        Parameters:
        taken_names: The names already taken. (list of str)
        """
        super(Bart, self).__init__(taken_names, initial = 'b')

    def ask(self, prompt):
        """
        Get information from the bot. (str)

        Parameters:
        prompt: The question asked of Bart. (str)
        """
        # Play rock.
        if prompt == '\nWhat is your move? ':
            return 'rock'
        else:
            super(Bart, self).ask(prompt)

    def tell(self, text):
        pass


class Memor(player.Bot):
    """
    An RPS bot with a memory. (Bot)

    Attributes:
    file_path: The location of any stored data for the bot. (str)
    losses: The responses that will lose to a given move. (str)
    memory: The record of plays against the bot. (str)

    Methods:
    load_data: Load stored data of previous plays. (None)

    Overridden Methods:
    __init__
    __del__
    ask
    tell
    """

    def __init__(self, taken_names):
        """
        Set up the bot. (None)

        Parameters:
        taken_names: The names already taken. (list of str)
        """
        # Do the standard initialization.
        super(Memor, self).__init__(taken_names, initial = 'm')
        # Set up the memory attributes.
        self.file_path = 'rps_memor_data{}.txt'
        self.losses = {}
        self.memory = {}

    def __del__(self):
        """Garbage collect the instance. (None)"""
        # Save any stored move data.
        if '{}' not in self.file_path:
            with open(self.file_path, 'w') as data_file:
                for move, count in self.memory.items():
                    data_file.write('{}:{}\n'.format(move, count))

    def ask(self, prompt):
        """
        Get information from the bot. (str)

        Parameters:
        prompt: The question asked of the bot. (str)
        """
        # Make sure you have data.
        if not self.memory:
            self.set_up()
        if prompt == '\nWhat is your move? ':
            # Get the cumulative frequency of moves.
            moves, counts = zip(*self.memory.items())
            cum = [sum(counts[:index]) for index in range(1, len(moves) + 1)]
            # Make a weighted random guess of the next player's move.
            choice = random.random() * cum[-1]
            guess = moves[bisect.bisect(cum, choice)]
            # Play something that move loses to.
            return random.choice(self.losses[guess])
        else:
            super(Memor, self).ask(prompt)

    def load_data(self):
        """Load stored data of previous plays. (None)"""
        with open(self.file_path) as data_file:
            for line in data_file:
                key, value = line.split(':')
                if key in self.memory:
                    self.memory[key] = int(value)

    def set_up(self):
        """Set up the bot. (None)"""
        # Store lizard-spock data separately.
        data_tag = ''
        if self.game.wins == self.game.lizard_spock:
            data_tag = '_ls'
        # Check for a true human opponent.
        if hasattr(self.game.human, 'folder_path'):
            # Load any data stored for a human's plays.
            self.file_path = os.path.join(self.game.human.folder_path, self.file_path.format(data_tag))
            if os.path.exists(self.file_path):
                self.load_data()
        else:
            # Seed the initial memory.
            self.memory = {move: 1 for move in self.game.wins}
        # Get a reverse wins dictionary.
        self.losses = {move: [] for move in self.game.wins}
        for move, beats in self.game.wins.items():
            for loss in beats:
                self.losses[loss].append(move)

    def tell(self, text):
        """
        Give information to the bot. (None)

        Parameters:
        text: The information given to the bot. (str)
        """
        if text in self.memory:
            self.memory[text] += 1


class Randy(player.Bot):
    """
    A random RPS bot. (Bot)

    Overridden Methods:
    __init__
    ask
    tell
    """

    def __init__(self, taken_names, initial = 'r'):
        """
        Set up the bot. (None)

        Parameters:
        taken_names: The names already taken. (list of str)
        """
        super(Randy, self).__init__(taken_names, initial)

    def ask(self, prompt):
        """
        Get information from the bot. (str)

        Parameters:
        prompt: The question asked of the bot. (str)
        """
        # Make a completely random move.
        if prompt == '\nWhat is your move? ':
            return random.choice(list(self.game.wins.keys()))
        else:
            super(Randy, self).ask(prompt)

    def tell(self, text):
        """
        Give information to the bot. (None)

        Parameters:
        text: The information given to the bot. (str)
        """
        pass


class Lisa(Randy):
    """
    An anti-Bart bot. (Bot)

    Attributes:
    last_attack: The last move made by Lisa's opponent. (str)

    Overridden Methods:
    __init__
    ask
    tell
    """

    def __init__(self, taken_names):
        """
        Set up the bot. (None)

        Parameters:
        taken_names: The names already taken. (list of str)
        """
        super(Lisa, self).__init__(taken_names, initial = 'l')
        self.last_attack = ''

    def ask(self, prompt):
        """
        Get information from the bot. (str)

        Parameters:
        prompt: The question asked of the bot. (str)
        """
        if prompt == '\nWhat is your move? ' and self.last_attack == 'rock':
            # Assume rock means Bart.
            return 'paper'
        else:
            # Otherwise make a random move.
            return super(Lisa, self).ask(prompt)

    def tell(self, text):
        """
        Give information to the bot. (None)

        Parameters:
        text: The information given to the bot. (str)
        """
        if text in self.game.wins:
            self.last_attack = text


class RPS(game.Game):
    """
    A game of rock-paper-scissors. (Game)

    Class Attributes:
    bot_classes: The bots available as options for play. (dict of str: Bot)
    lizard_spock: A wins attribute for the lizard-spock option. (dict)
    wins: What each move beats. (dict of str: list of str)

    Attributes:
    bot: The non-human player. (player.Bot)
    bot_cls: The name of the bot class. (str)
    loss_draw: A flag for the next loss counting as a draw. (bool)
    match: The number of games in a match. (int)
    moves: The moves made keyed to the player's names. (dict of str: str)

    Overridden Methods:
    game_over
    handle_options
    player_action
    set_options
    set_up
    """

    aka = ['RPS', 'Rock Paper Scissors', 'Roshambo']
    bot_classes = {'bart': Bart, 'lisa': Lisa, 'memor': Memor, 'randy': Randy}
    categories = ['Other Games']
    credits = CREDITS
    lizard_spock = {'rock': ['scissors', 'lizard'], 'scissors': ['paper', 'lizard'],
        'paper': ['rock', 'spock'], 'lizard': ['paper', 'spock'], 'spock': ['scissors', 'rock']}
    name = 'Rock-Paper-Scissors'
    num_options = 3
    rules = RULES
    wins = {'rock': ['scissors'], 'scissors': ['paper'], 'paper': ['rock']}

    def do_gipf(self, arguments):
        """
        No thank you.
        """
        game, losses = self.gipf_check(arguments, ('forty thieves',))
        go = True
        # Forty Thieves turns the next loss into a draw..
        if game == 'forty thieves':
            if not losses:
                self.loss_draw = True
                self.human.tell('\nYour next loss will be a draw.')
        # Otherwise I'm confused.
        else:
            self.human.tell('No thank you.')
        return go

    def game_over(self):
        """Check for the end of the game. (bool)"""
        # Only check if both players have moved.
        if not self.turns % 2:
            move = self.moves[self.human.name]
            bot_move = self.moves[self.bot.name]
            # Check for a bot win.
            if move in self.wins[bot_move] and not self.loss_draw:
                self.human.tell('{} beats {}, you lose.'.format(bot_move, move))
                self.win_loss_draw[1] += 1
            # Check for a human win.
            elif bot_move in self.wins[move]:
                self.human.tell('{} beats {}, you win!'.format(move, bot_move))
                self.win_loss_draw[0] += 1
            # Otherwise assume a tie.
            else:
                if move == bot_move:
                    self.human.tell('You both played {}, play again.'.format(move))
                else:
                    self.human.tell('You should have lost to {}, but you drew.'.format(bot_move))
                    self.loss_draw = False
                self.win_loss_draw[2] += 1
            # Update the players.
            self.human.tell('The score is now {}-{}-{}.'.format(*self.win_loss_draw))
            self.bot.tell(move)
        return sum(self.win_loss_draw[:2]) == self.match

    def handle_options(self):
        """Handle any game options. (None)"""
        # Parse the options.
        super(RPS, self).handle_options()
        # Set the players.
        self.bot = self.bot_classes[self.bot_cls]([self.human.name])
        self.players = [self.human, self.bot]
        # Set match play flag.
        if self.match > 1:
            self.flags |= 256

    def player_action(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        move = player.ask('\nWhat is your move? ').lower()
        # Process game moves.
        if move in self.wins:
            self.moves[player.name] = move
        # Process other commands.
        else:
            return self.handle_cmd(move)

    def set_options(self):
        """Define the options for the game. (None)"""
        # Set the bot options.
        self.option_set.default_bots = [(Memor, ())]
        self.option_set.add_option('bot', valid = ('bart', 'lisa', 'memor', 'randy'),
            converter = options.lower, default = 'memor', target = 'bot_cls',
            question = 'Which bot would you like to play against? ',
            error_text = 'The valid bots are Bart, Lisa, Memor, and Randy.')
        # Set the play options.
        self.option_set.add_option('lizard-spock', target = 'wins', value = self.lizard_spock,
            default = None, question = 'Would you like to play with lizard and Spock? bool')
        self.option_set.add_option('match', [], int, default = 3, check = lambda x: x > 0,
            question = 'How many games should there be in the match? (return for 3)? ')

    def set_up(self):
        """Set up the game. (None)"""
        # Set the tracking variables.
        self.moves = {player.name: '' for player in self.players}
        self.loss_draw = False


if __name__ == '__main__':
    # Play Rock-Paper-Scissors without the full interface.
    try:
        input = raw_input
    except NameError:
        pass
    name = input('What is your name? ')
    rps = RPS(player.Humanoid(name), '')
    rps.play()
