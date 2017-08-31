"""
rps_game.py

Rock-paper-scissors.

!! Implement the Iocaine Powder bot.

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

import tgames.game as game
import tgames.player as player
import tgames.utility as utility


# Credits for Rock-Paper-Scissors.
CREDITS = """
Game Design: Traditional
Game Programming: Craig "Ichabod" O'Brien
Special Thanks: Matt Groening
"""

# Rules for Rock-Paper-Scissors.
RULES = """
Each player chooses one of rock, paper, or scissors. Rock beats scissors, 
paper beats rock, and scissors beats paper. If players choose the same thing, 
both players choose again.

If the lizard-spock options is chosen, players may also choose lizard or 
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
        if prompt == 'What is your move? ':
            return 'rock'
        else:
            return ''

    def tell(self, text):
        pass


class Memor(player.Bot):
    """
    An RPS bot with a memory. (Bot)

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
        super(Memor, self).__init__(taken_names, initial = 'm')
        self.file_path = 'rps_memor_data{}.txt'
        self.losses = {}
        self.memory = {}

    def __del__(self):
        """Garbage collect the instance. (None)"""
        if '{}' not in self.file_path:
            with open(self.file_path, 'w') as data_file:
                for move, count in self.memory.items():
                    data_file.write('{}:{}\n'.format(move, count))

    def ask(self, prompt):
        if not self.memory:
            self.set_up()
        if prompt == 'What is your move? ':
            moves, counts = zip(*self.memory.items())
            cum = [sum(counts[:index]) for index in range(1, len(moves) + 1)]
            choice = random.random() * cum[-1]
            guess = moves[bisect.bisect(cum, choice)]
            return random.choice(self.losses[guess])
        else:
            return ''

    def load_data(self):
        with open(self.file_path) as data_file:
            for line in data_file:
                key, value = line.split(':')
                if key in self.memory:
                    self.memory[key] = int(value)

    def set_up(self):
        data_tag = ''
        if self.game.wins == self.game.lizard_spock:
            data_tag = '_ls'
        if hasattr(self.game.human, 'folder_path'):
            self.file_path = os.path.join(self.game.human.folder_path, self.file_path.format(data_tag))
            if os.path.exists(self.file_path):
                self.load_data()
        self.losses = {move: [] for move in self.game.wins}
        for move, beats in self.game.wins.items():
            for loss in beats:
                self.losses[loss].append(move)
        self.memory = {move: 1 for move in self.game.wins}

    def tell(self, text):
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

    def __init__(self, taken_names):
        """
        Set up the bot. (None)

        Parameters:
        taken_names: The names already taken. (list of str)
        """
        super(Randy, self).__init__(taken_names, initial = 'r')

    def ask(self, prompt):
        if prompt == 'What is your move? ':
            return random.choice(list(self.game.wins.keys()))
        else:
            return ''

    def tell(self, text):
        pass


class Lisa(Randy):
    """
    An anti-Bart bot. (Bot)

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
        if prompt == 'What is your move? ':
            if self.last_attack == 'rock':
                return 'paper'
            else:
                return super(Lisa, self).ask(prompt)
        else:
            return ''

    def tell(self, text):
        if text in self.game.wins:
            self.last_attack = text
        

class RPS(game.Game):
    """
    A game of rock-paper-scissors. (Game)

    Class Attributes:
    bots: The bots available as options for play. (dict of str: Bot)
    lizard_spock: A wins attribute for the lizard-spock option. (dict)
    wins: What each move beats. (dict of str: list of str)

    Attributes:
    bot: The non-human player. (player.Bot)
    match: The number of games in a match. (int)
    moves: The moves made keyed to the player's names. (dict of str: str)

    Overridden Methods:
    game_over
    handle_options
    player_turn
    set_up
    """

    aka = ['rps', 'rock paper scissors', 'roshambo']
    bots = {'bart': Bart, 'lisa': Lisa, 'memor': Memor, 'randy': Randy}
    categories = ['Other Games', 'Other Games']
    credits = CREDITS
    lizard_spock = {'rock': ['scissors', 'lizard'], 'scissors': ['paper', 'lizard'], 
        'paper': ['rock', 'spock'], 'lizard': ['paper', 'spock'], 'spock': ['scissors', 'rock']}
    name = 'Rock-Paper-Scissors'
    rules = RULES
    wins = {'rock': ['scissors'], 'scissors': ['paper'], 'paper': ['rock']}

    def game_over(self):
        """Check for the end of the game. (bool)"""
        # Only check if both players have moved.
        if not self.turns % 2:
            move = self.moves[self.human.name]
            bot_move = self.moves[self.bot.name]
            # Check for bot win.
            if move in self.wins[bot_move]:
                self.human.tell('{} beats {}, you lose.'.format(bot_move, move))
                self.win_loss_draw[1] += 1
            # Check for human win.
            elif bot_move in self.wins[move]:
                self.human.tell('{} beats {}, you win!'.format(move, bot_move))
                self.win_loss_draw[0] += 1
            # Otherwise assume tie.
            else:
                self.human.tell('You both played {}, play again.'.format(move))
                self.win_loss_draw[2] += 1
            # Update the players.
            self.human.tell('The score is now {}-{}-{}.'.format(*self.win_loss_draw))
            self.bot.tell(move)
        return sum(self.win_loss_draw[:2]) == self.match

    def handle_options(self):
        """Handle any game options. (None)"""
        # Set default options
        self.bot_class = Memor
        self.match = 3
        # Check for no options
        if self.raw_options == 'none':
            pass
        # Check for passed options.
        elif self.raw_options:
            self.flags |= 1
            for word in self.raw_options.lower().split():
                # Lizard Spock
                if word == 'lizard-spock':
                    self.wins = self.lizard_spock
                # Match
                elif word.startswith('match='):
                    try:
                        self.match = int(word.split('=')[1])
                    except ValueError:
                        self.human.tell('Invalid value for match option: {!r}.'.format(word.split('=')[1]))
                # Bots.
                elif word in self.bots:
                    self.bot_class = self.bots[word]
        # Ask for options.
        else:
            if self.human.ask('Would you like to change the options? ').lower().strip() in utility.YES:
                self.flags |= 1
                # Check for lizard Spock.
                lizard_spock = self.human.ask('Would you like to add lizard and Spock? ')
                if lizard_spock in utility.YES:
                    self.wins = self.lizard_spock
                # Check for match number.
                while True:
                    match = self.human.ask('How many games to play in match (return for 3)? ').strip()
                    if not match:
                        break
                    elif match.isdigit():
                        self.match = int(match)
                        break
                    else:
                        self.human.tell('Please enter an integer.')
                # Check for bot opponent.
                while True:
                    bot = self.human.ask('Which bot would you like to play against (return for Memor)? ')
                    bot = bot.lower().strip()
                    if bot in self.bots:
                        self.bot_class = self.bots[bot]
                        break
                    elif not bot:
                        break
                    else:
                        self.human.tell('I do not recognize that type of bot.')
                        known = ', '.join(sorted(self.bots.keys()))
                        self.human.tell('The bots I know are:', known)
        # Set up players.
        self.bot = self.bot_class([self.human.name])
        self.players = [self.human, self.bot]

    def player_turn(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        move = player.ask('What is your move? ').lower().strip()
        if move in self.wins:
            self.moves[player.name] = move
        else:
            return self.handle_cmd(move)

    def set_up(self):
        """Set up the game. (None)"""
        self.moves = {player.name: '' for player in self.players}


if __name__ == '__main__':
    try:
        input = raw_input
    except NameError:
        pass
    name = input('What is your name? ')
    rps = RPS(player.Player(name), '')
    rps.play()
