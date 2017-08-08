"""
interface.py

The interface for the tgames game suite.

Classes:
Interface: A menu interface for playing games. (object)

Functions:
excel_column: Convert a number into a Excel style column header. (str)
"""

import os
from string import ascii_uppercase

import game
import player

class Interface(object):
    """
    A menu interface for playing games. (object)

    Attributes:
    human: The player navigating the menu. (player.Player)

    Methods:
    load_games: Load all of the games defined locally. (None)
    menu: Run the game selection menu. (None)
    play_game: Play a selected game. (None)
    show_menu: Display the menu options to the user. (dict)

    Overridden Methods:
    __init__
    """

    def __init__(self, human):
        """Set up the interface. (None)"""
        self.human = human
        self.load_games()

    def load_games(self):
        """Load all of the games defined locally. (None)"""
        # Import the Python files.
        for dir_path, dir_name, file_names in os.walk('.'):
            for file_name in file_names:
                if file_name.endswith('_game.py'):
                    __import__(file_name[:-3])
        # Search through all of the game.Game sub-classes.
        self.categories = {'sub-categories': {}, 'games': []}
        self.games = {}
        search = [game.Game]
        while search:
            game_class = search.pop()
            # Store game by name.
            self.games[game_class.name.lower()] = game_class
            for alias in game_class.aka:
                self.games[alias] = game_class
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
            elif letter.lower().startswith('play'):
                game_name, slash, options = letter[4:].strip().partition('/')
                game_name = game_name.strip()
                if game_name in self.games:
                    self.play_game(self.games[game_name], options.strip())
                    self.human.tell()
                else:
                    self.human.tell("I don't know how to play that game.")
            # Give an error for everything else.
            else:
                self.human.tell('That is not a valid selection.')

    def play_game(self, game_class, options = ''):
        """
        Play a selected game. (None)

        Parameters:
        game_class: The game to play. (subclass of game.Game)
        options: Options specified by the play command. (str)
        """
        # Set up the game.
        game = game_class(self.human, options)
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


