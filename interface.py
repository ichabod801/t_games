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

import tgames.full_credits as full_credits
import tgames.game as game
import tgames.other_cmd as other_cmd
import tgames.player as player
import tgames.utility as utility


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

When the game is over you will be shown your overall statistics for that game.
From the interface you can see your statistics for any game by typing 'stats'
and the name of the game. You can also type 'stats cat' for all games in the
category you are currently in, or just 'stats' for stats for all of the games
you have played.

You can get this help text by typing help or ?
"""


class Interface(other_cmd.OtherCmd):
    """
    A menu interface for playing games. (OtherCmd)

    Attributes:
    categories: The tree of categories and games. (dict)
    focus: The menu's current location in the category tree. (dict)
    game: The game being played. (game.Game)
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
        self.games, self.categories = game.load_games()
        self.valve = RandomValve()

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
        self.human.tell(full_credits.FULL_CREDITS)
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
            game_name, options = arguments.split('/', 1)
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

    def do_stats(self, arguments):
        """
        Show game statistics. (bool)

        parameters:
        arguments: The game to show statistics for. (str)
        """
        # Process the arguments.
        arguments, slash, options = arguments.partition('/')
        arguments = arguments.strip()
        options = options.strip().lower()
        xyzzy = 'xyzzy' in options
        gipf = 'gipf' in options
        # Handle overall stats.
        if not arguments:
            self.show_stats(self.human.results, 'Overall Statistics', gipf = gipf, xyzzy = xyzzy)
            games = sorted(set([result[0] for result in self.human.results]))
            # Show the stats for the individual games.
            for game in games:
                relevant = [result for result in self.human.results if result[0] == game]
                self.show_stats(relevant, gipf = gipf, xyzzy = xyzzy)
        # Handle specific game stats.
        elif arguments.lower() in self.games:
            game_class = self.games[arguments.lower()]
            relevant = [result for result in self.human.results if result[0] == game_class.name]
            self.show_stats(relevant, gipf = gipf, xyzzy = xyzzy)
        # Handle category stats.
        elif arguments.lower() == 'cat':
            # Find all of the games in the category
            search = [self.focus]
            games = []
            while search:
                category = search.pop()
                games.extend(category['games'])
                search.extend(list(category['sub-categories'].values()))
            names = [game.name for game in games]
            # Get and show the overall stats.
            relevant = [result for result in self.human.results if result[0] in names]
            self.show_stats(relevant, 'Category Statistics', gipf = gipf, xyzzy = xyzzy)
            # Show the stats for the individual games.
            games = sorted(set([result[0] for result in relevant]))
            for game in games:
                relevant = [result for result in self.human.results if result[0] == game]
                self.show_stats(relevant, gipf = gipf, xyzzy = xyzzy)
        else:
            self.human.tell('You have never played that game.')

    def menu(self):
        """Run the game selection menu. (None)"""
        # Start at the top category.
        self.focus = self.categories
        previous = []
        # Loop through player choices.
        while True:
            # Show the menu and get the possible choices.
            menu_map = self.show_menu(self.focus)
            letter = self.human.ask('What is your selection? ').strip()
            # Check for menu choices.
            if letter.upper() in menu_map:
                choice = menu_map[letter.upper()]
                # Check for sub-category choices.
                if choice[:-9] in self.focus['sub-categories']:
                    previous.append(self.focus)
                    self.focus = self.focus['sub-categories'][choice[:-9]]
                # Check for special choices.
                elif choice == 'Previous Menu':
                    self.focus = previous.pop()
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
        self.game = game_class(self.human, options, self)
        # Play the game until the player wants to stop.
        while True:
            results = self.game.play()
            self.human.store_results(self.game.name, results)
            self.do_stats(self.game.name)
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

    def show_stats(self, results, title = '', gipf = False, xyzzy = False):
        """
        Show the statistics for a set of game results. (None)

        If the title is blank, it is taken from the game name in the first result.

        Parameters:
        results: The game results to generate stats for. (list of list)
        title: The title to print for the statistics. (str)
        """
        # Check for empty results.
        if not results:
            self.human.tell('You have never played that game.')
            return None
        # Process parameters.
        if not title:
            title = results[0][0] + ' Statistics'
        if not gipf:
            results = [result for result in results if not result[5] & 8]
        if not xyzzy:
            results = [result for result in results if not result[5] & 128]
        # Calculate total win-loss-draw and get data for streaks.
        # Prep for loop.
        wins = []
        game_wld = [0, 0, 0]
        player_wld = [0, 0, 0]
        # Loop through results storing totals and streak data.
        for name, win, loss, draw, score, flags in results:
            if not loss and not win:
                game_wld[2] += 1
                wins.append(0)
            elif not loss:
                game_wld[0] += 1
                wins.append(1)
            else:
                game_wld[1] += 1
                wins.append(-1)
            player_wld[0] += win
            player_wld[1] += loss
            player_wld[2] += draw
        # Get streaks.
        current_streak, streak_type, longest_streaks = utility.streaks(wins)
        # Get score data.
        scores = [result[4] for result in results]
        # Display the statistics to the user.
        # Display the title.
        self.human.tell(title)
        self.human.tell('-' * len(title))
        # Display win-loss-draw
        self.human.tell('Overall Win-Loss-Draw: {}-{}-{}'.format(*game_wld))
        self.human.tell('Player Win-Loss-Draw: {}-{}-{}'.format(*player_wld))
        # Display scores.
        self.human.tell('Lowest Score: {}'.format(min(scores)))
        self.human.tell('Average Score: {:.1f}'.format(utility.mean(scores)))
        self.human.tell('Median Score: {}'.format(utility.median(scores)))
        self.human.tell('Highest Score: {}'.format(max(scores)))
        # Display streaks.
        if longest_streaks[1]:
            self.human.tell('Longest winning streak: {}'.format(longest_streaks[1]))
        if longest_streaks[-1]:
            self.human.tell('Longest losing streak: {}'.format(longest_streaks[-1]))
        if longest_streaks[0]:
            self.human.tell('Longest drawing streak: {}'.format(longest_streaks[0]))
        streak_name = ('drawing', 'winning', 'losing')[streak_type]
        self.human.tell('You are currently on a {} game {} streak.'.format(current_streak, streak_name))
        self.human.tell()


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
    interface = Interface(player.Tester())
    interface.menu()


