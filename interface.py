"""
interface.py

The interface for the tgames game suite.

!! Add options after / for menu selections.

Contants:
CREDITS: Programming credits and play testers. (str)
HELP_TEXT: General help for the interface. (str)

Classes:
Interface: A menu interface for playing games. (OtherCmd)

Functions:
excel_column: Convert a number into a Excel style column header. (str)
"""


import os
import random
from string import ascii_uppercase

import tgames.game as game
import tgames.other_cmd as other_cmd
import tgames.player as player


# Programming credits and play testers.
CREDITS = """
This interface and the tgames framework was programmed by Craig "Ichabod"
O'Brien.
"""

# General help for the interface.
HELP_TEXT = """
The games are organized into categories. You can use the menu to browse
throught the categories to find the game you want. Just type in the 
letter or letters to the left of the colon to make a selection.

You can see the rules for a game by typing 'rules game-name'. You should
also be able to see the rules from within the game by typing 'rules'.

You can go directly to a game by typing 'play game-name'. If you don't see
the game you want to play, you might try this. Some games are stored with
aliases that are not shown in the menu. For example, 'play Broadsides' will
play the game listed in the menu as 'Battleships'. You can also specify
options for a game with the play command by putting them after the slash.
The options for the games should be specified in the game rules. Options
ending with an equals sign (=) require a value to be specified. Do not put
spaces around the equals sign. That is, use 'win=108' rather than 'win = 108'.
If you play a game through the menu or by the play command without options, 
the game should prompt you to specify the options (if there are any).

You can see the credits (who designed and programmed the game) for any game 
by typing 'credits'.

You can get this help text by typing help or ?
"""


class Interface(other_cmd.OtherCmd):
    """
    A menu interface for playing games. (OtherCmd)

    Attributes:
    human: The player navigating the menu. (player.Player)

    Methods:
    do_credits: Show the programming credits for the interface. (bool)
    do_help: Show the general help text for tgames. (bool)
    load_games: Load all of the games defined locally. (None)
    menu: Run the game selection menu. (None)
    play_game: Play a selected game. (None)
    show_menu: Display the menu options to the user. (dict)

    Overridden Methods:
    __init__
    default
    """

    aliases = {'?': 'help'}

    def __init__(self, human):
        """Set up the interface. (None)"""
        self.human = human
        self.load_games()

    def default(self, line):
        """
        Handle unrecognized user input. (bool)

        If it is a game name, that game is played.

        Parameters:
        line: The unrecognized input. (str)
        """
        # Get game name.
        game_name = line
        if '/' in game_name:
            game_name = game_name.split('/')[0].strip()
        # Play it if it is a valid game.
        if game_name.lower() in self.games:
            self.do_play(line)
        else:
            self.human.tell('That is an invalid selection.')

    def do_credits(self, arguments):
        """
        Show the programming credits for the interface. (bool)

        Parameters:
        arguments: This parameter is ignored. (str)
        """
        self.human.tell(CREDITS)
        self.human.ask('Press Enter to continue: ')
        return True

    def do_help(self, arguments):
        """
        Show the general help text for tgames. (bool)

        Parameters:
        arguments: This parameter is ignored. (str)
        """
        self.human.tell(HELP_TEXT)
        self.human.ask('Press Enter to continue: ')
        return True

    def do_play(self, arguments):
        """
        Play a game with the specified options, if any. (bool)

        Parameters:
        arguments: The game name, with any options specified after a slash. (str)
        """
        # Get the game name and options.
        if '/' in arguments:
            game_name, options = arguments.split('/', maxsplit = 1)
        else:
            game_name = arguments
            options = ''
        game_name = game_name.lower().strip()
        if game_name in self.games:
            # Play the game if known.
            self.play_game(self.games[game_name], options)
            self.human.tell()
        else:
            # Warn about unknown games.
            self.human.tell("\nI don't know how to play that game.")
        return True

    def do_rules(self, arguments):
        """
        Show the rules for the specified game. (bool)

        Parameters:
        arguments: The game name. (str)
        """
        arguments = arguments.lower()
        if arguments in self.games:
            self.human.tell(self.games[arguments].rules)
            self.human.ask('Press Enter to continue: ')
        else:
            self.human.tell("\nI do not know the rules to that game.")
        return True

    def load_games(self):
        """Load all of the games defined locally. (None)"""
        # Import the Python files.
        for package in [name for name in os.listdir('.') if name.endswith('_games')]:
            for module in [name for name in os.listdir(package) if name.endswith('_game.py')]:
                __import__('{}.{}'.format(package, module[:-3]))
        # Search through all of the game.Game sub-classes.
        self.valve = RandomValve()
        self.categories = {'sub-categories': {}, 'games': []}
        self.games = {}
        search = [game.Game]
        while search:
            game_class = search.pop()
            # Store game by name.
            self.games[game_class.name.lower()] = game_class
            for alias in game_class.aka:
                self.games[alias.lower()] = game_class
            # Store game by category
            # !! Once I have non-test games, hide the test games.
            category = self.categories
            for game_category in game_class.categories:
                if game_category not in category['sub-categories']:
                    category['sub-categories'][game_category] = {'sub-categories': {}, 'games': []}
                category = category['sub-categories'][game_category]
            category['games'].append(game_class)
            # Search the full hierarchy of sub-classes.
            search.extend(game_class.__subclasses__())

    def menu(self):
        """Run the game selection menu. (None)"""
        # Start at the top category.
        category = self.categories
        previous = []
        # Loop through player choices.
        while True:
            # Show the menu and get the possible choices.
            menu_map = self.show_menu(category)
            letter = self.human.ask('What is your selection? ').strip()
            # Check for menu choices.
            if letter.upper() in menu_map:
                choice = menu_map[letter.upper()]
                # Check for sub-category choices.
                if choice[:-9] in category['sub-categories']:
                    previous.append(category)
                    category = category['sub-categories'][choice[:-9]]
                # Check for special choices.
                elif choice == 'Previous Menu':
                    category = previous.pop()
                elif choice == 'Quit':
                    break
                # Assume anything else is a game to play.
                else:
                    self.play_game(self.games[choice.lower()])
            # Check for non-menu choices.
            else:
                self.handle_cmd(letter)

    def play_game(self, game_class, options = ''):
        """
        Play a selected game. (None)

        Parameters:
        game_class: The game to play. (subclass of game.Game)
        options: Options specified by the play command. (str)
        """
        # Set up the game.
        game = game_class(self.human, options, self)
        # Play the game until the player wants to stop.
        while True:
            results = game.play()
            if self.human.ask('Would you like to play again? ').lower() not in ('yes', 'y', '1'):
                break

    def show_menu(self, category):
        """
        Display the menu options to the user. (dict)

        The return value is a dictionary of letters to choices.

        Parameters:
        category: The category of games to display a menu for. (dict)
        """
        # Alphabetize the sub-categories and games.
        categories = sorted([sub_category + ' Category' for sub_category in category['sub-categories']])
        games = sorted([game.name for game in category['games']])
        choices = categories + games
        # Add a previous menu option if not at the top.
        if category != self.categories:
            choices.append('Previous Menu')
        # Add a quit option.
        choices.append('Quit')
        # Get letters for the choices.
        pairs = [(excel_column(n + 1), selection) for n, selection in enumerate(choices)]
        # Display the menu.
        for letter, choice in pairs:
            self.human.tell('{}: {}'.format(letter, choice))
        self.human.tell()
        # Return the meaning of the menu letters.
        return dict(pairs)


class RandomValve(object):

    def __init__(self, p = 0.05):
        self.p = p
        self.q = p
        self.last = None

    def blow(self, last):
        check = random.random()
        if last is self.last:
            return False
        self.last = last
        if check < self.q:
            self.q = self.p
            return True
        else:
            self.q += self.q * check
            return False
            

def excel_column(n):
    """
    Convert a number into a Excel style column header. (str)

    Parameters:
    n: A number to convert to letters. (int)
    """
    column = ''
    while n:
        column = ascii_uppercase[(n % 26) - 1] + column
        n //= 27
    return column

if __name__ == '__main__':
    interface = Interface(player.Player('Ichabod'))
    interface.menu()


