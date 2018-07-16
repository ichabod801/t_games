"""
interface.py

The interface for the t_games game suite.

Copyright (C) 2018 by Craig O'Brien and the t_game contributors.
See the top level __init__.py file for details on the t_games license.

Contants:
CREDITS: Programming credits and play testers. (str)
HELP_TEXT: General help for the interface. (str)
LICENSE: Info on the GPLv3 license that t_games uses. (str)
RULES: Some basic guidelines for life. (str)

Classes:
Interface: A menu interface for playing games. (OtherCmd)

Functions:
excel_column: Convert a number into a Excel style column header. (str)
"""


import os
import random
from string import ascii_uppercase

import t_games.full_credits as full_credits
import t_games.game as game
import t_games.other_cmd as other_cmd
import t_games.player as player
import t_games.utility as utility


# Programming credits and play testers.
CREDITS = """
This interface and the t_games framework was programmed by Craig "Ichabod"
O'Brien.
"""

# General help for the interface.
HELP_TEXT = """
The games are organized into categories. You can use the menu to browse
throught the categories to find the game you want. Just type in the 
letter or letters to the left of the colon to make a selection. You can
type home at any point to get back to the top of the menu.

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

You can play a random game by typing 'random'. This will be a random game from
the category you're in currently in the menu system. To play any random game, 
use 'random all'. You can get a list of available games with the games
command. It is also context sensitive, and will only show the games for the 
category that you are in.

You can create shortcuts using the set command. The first word after the set
command is the shortcut, the rest is what it stands for. Once it is set, any
time the first word of a line is a shortcut, it will be replaced with the 
appropriate text. For example, after 'set fc play freecell', you can just
enter 'fc' to play freecell. You could even type 'fc / cells = 5', which 
will translate to 'play freecell / cells = 5'.

You can get this help text by typing help or ?
"""


# Info on the GPLv3 license that t_games uses.
LICENSE = """
Copyright (C) 2018 by Craig O'Brien and the t_game contributors.

This program is free software: you can redistribute it and/or modify it under 
the terms of the GNU General Public License as published by the Free Software 
Foundation, either version 3 of the License, or (at your option) any later 
version.

This program is distributed in the hope that it will be useful, but WITHOUT 
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS 
FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more 
details.

See <http://www.gnu.org/licenses/> for details on this license (GPLv3).
"""


# Some basic guidelines for life.
RULES = """
1. Abstain from causing harm.
2. Abstain from deception.
3. Abstain from taking that which is not freely offered.
4. Abstain from abusing sexuality.
5. Abstain from intoxicating the mind.
"""


class Interface(other_cmd.OtherCmd):
    """
    A menu interface for playing games. (OtherCmd)

    Attributes:
    categories: The tree of categories and games. (dict)
    focus: The menu's current location in the category tree. (dict)
    game: The game being played. (game.Game)
    human: The player navigating the menu. (player.Player)
    previous: Previous menu locations visited. (list)
    titles: The titles of the previous categories visited. (list)

    Class Attributes:
    aliases: Alternate command words. (dict of str: str)
    rules: The rules. (str)
    word_list: The relative location of a word list for word games. (str)

    Methods:
    do_credits: Show the programming credits for the interface. (bool)
    do_help: Show the general help text for t_games. (bool)
    do_play: Play a game with the specified options, if any. (bool)
    do_random: Play a random game. (bool)
    do_rules: Show the rules for the specified game. (bool)
    do_stats: Show game statistics. (bool)
    figure_win_loss_draw: Determine win/loss/draw numbers and streaks. (tuple) 
    filter_results: Filter game results based on user requests. (list of lists)
    load_games: Load all of the games defined locally. (None)
    menu: Run the game selection menu. (None)
    play_game: Play a selected game. (None)
    show_menu: Display the menu options to the user. (dict)

    Overridden Methods:
    __init__
    default
    """

    aliases = {'?': 'help'}
    rules = RULES
    word_list = 'other_games/3of6game.txt'

    def __init__(self, human):
        """Set up the interface. (None)"""
        # Set the attributes.
        self.human = human
        self.games, self.categories = game.load_games()
        self.valve = RandomValve()
        self.aliases = {}
        for cls in reversed(self.__class__.__mro__):
            if hasattr(cls, 'aliases'):
                self.aliases.update(cls.aliases)

    def category_games(self):
        """Get all of the games in the current category. (list of game.Game)"""
        search = [self.focus]
        games = []
        while search:
            category = search.pop()
            games.extend(category['games'])
            search.extend(list(category['sub-categories'].values()))
        return games

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
            self.human.error('That is an invalid selection.')

    def do_credits(self, arguments):
        """
        Show the programming credits for the interface. (bool)

        Parameters:
        arguments: This parameter is ignored. (str)
        """
        self.human.tell(full_credits.FULL_CREDITS)
        self.human.ask('Press Enter to continue: ')
        return True

    def do_games(self, arguments):
        """
        List the available games in the current category. (None)

        Parameters:
        arguments: This parameter is ignored. (str)
        """
        # Get the games in the current context.
        games = self.focus['games'][:]
        search = list(self.focus['sub-categories'].values())
        while search:
            sub_category = search.pop()
            games.extend(sub_category['games'])
            search.extend(sub_category['sub-categories'].values())
        # Sort the games alphabetically.
        games.sort(key = lambda game: game.name)
        # Print the game list with aliases.
        for game in games:
            if game.aka:
                self.human.tell('{} ({})'.format(game.name, ', '.join(game.aka)))
            else:
                self.human.tell(game.name)
        self.human.ask('\nPress Enter to continue: ')
        self.human.tell()

    def do_help(self, arguments):
        """
        Show the general help text for t_games. (bool)

        Parameters:
        arguments: This parameter is ignored. (str)
        """
        # Show help based on arguments.
        if 'license' in arguments.lower():
            self.human.tell(LICENSE)
        else:
            self.human.tell(HELP_TEXT)
        self.human.ask('Press Enter to continue: ')
        return True

    def do_home(self, arguments):
        """
        Go to the top of the menu tree.. (bool)

        Parameters:
        arguments: This parameter is ignored. (str)
        """
        self.focus = self.categories
        self.previous = []
        self.titles = ['Home Menu']

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
            self.human.error("\nI don't know how to play that game.")
        return True

    def do_random(self, arguments):
        """
        Play a random game. (bool)

        Parameters:
        arguments: The arguments for the command. (str)
        """
        if arguments.strip().lower() == 'all':
            game_class = random.choice(list(self.games.values()))
        else:
            game_class = random.choice(self.category_games())
        self.play_game(game_class, '')
        self.human.tell()

    def do_rules(self, arguments):
        """
        Show the rules for the specified game. (bool)

        Parameters:
        arguments: The game name. (str)
        """
        arguments = arguments.lower()
        if not arguments:
            print(self.rules)
        elif arguments in self.games:
            self.human.tell(self.games[arguments].rules)
            self.human.ask('Press Enter to continue: ')
        else:
            self.human.error("\nI do not know the rules to that game.")
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
        # Handle overall stats.
        if not arguments:
            self.show_stats(self.human.results, 'Overall Statistics', options)
            games = sorted(set([result[0] for result in self.human.results]))
            # Show the stats for the individual games.
            for game in games:
                relevant = [result for result in self.human.results if result[0] == game]
                self.show_stats(relevant, options = options)
        # Handle specific game stats.
        elif arguments.lower() in self.games:
            game_class = self.games[arguments.lower()]
            relevant = [result for result in self.human.results if result[0] == game_class.name]
            self.show_stats(relevant, options = options)
        # Handle category stats.
        elif arguments.lower() == 'cat':
            # Find the relevant games.
            names = [game.name for game in self.category_games()]
            relevant = [result for result in self.human.results if result[0] in names]
            # Show the over and individual game stats.
            self.show_stats(relevant, 'Category Statistics', options)
            games = sorted(set([result[0] for result in relevant]))
            for game in games:
                relevant = [result for result in self.human.results if result[0] == game]
                self.show_stats(relevant, options = options)
        else:
            self.human.tell('You have never played that game.')

    def figure_win_loss_draw(self, results):
        """
        Determine win/loss/draw numbers and streaks. (tuple)

        The return value is the game record, the per player record, the current 
        streak, the type of the current streak, and the longest streaks for each 
        type.

        Parameters:
        results: The game results to calculate from. (list of list)
        """
        # Prep for loop.
        wins = []
        game_wld = [0, 0, 0]
        player_wld = [0, 0, 0]
        # Loop through results storing totals and streak data.
        for name, win, loss, draw, score, turns, flags, settings in results:
            if flags & 256:
                # Handle match play.
                if win > loss:
                    game_wld[0] += 1
                    wins.append(1)
                elif loss > win:
                    game_wld[1] += 1
                    wins.append(-1)
                else:
                    game_wld[2] += 1
                    wins.append(0)
            else:
                # Handle single games.
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
        return game_wld, player_wld, current_streak, streak_type, longest_streaks

    def filter_results(self, results, options):
        """
        Filter game results based on user requests. (list of lists)

        Paramters:
        results: The game results to filter. (list of lists)
        options: The user provided options, including any filters. (str)
        """
        if 'cheat' not in options:
            results = [result for result in results if not result[6] & 2]
        if 'gipf' not in options:
            results = [result for result in results if not result[6] & 8]
        if 'xyzzy' not in options:
            results = [result for result in results if not result[6] & 128]
        return results

    def menu(self):
        """Run the game selection menu. (None)"""
        # Start at the top category.
        self.focus = self.categories
        self.previous = []
        self.titles = ['Home Menu']
        # Display the intro.
        self.human.tell("\nWelcome to Ichabod's Text Game Extravaganza!")
        unique_games = set([g for g in self.games.values() if g.categories[0] != 'Test Games'])
        num_options = sum(game.num_options for game in unique_games)
        count_text = 'Currently hosting {} different games with {} settable options.\n'
        self.human.tell(count_text.format(len(unique_games), num_options))
        self.human.tell("Copyright (C) 2018 by Craig O'Brien and the tgame contributors.")
        self.human.tell('For more details type help license.')
        # Loop through player choices.
        while True:
            # Show the menu and get the possible choices.
            menu_map = self.show_menu(self.focus)
            response = self.human.ask('What is your selection? ').strip()
            letter, slash, options = response.partition('/')
            letter = letter.strip().upper()
            self.human.tell()
            # Check for menu choices.
            if letter in menu_map:
                choice = menu_map[letter]
                # Check for sub-category choices.
                if choice[:-9] in self.focus['sub-categories']:
                    self.previous.append(self.focus)
                    self.focus = self.focus['sub-categories'][choice[:-9]]
                    self.titles.append(choice[:-9])
                # Check for special choices.
                elif choice == 'Previous Menu':
                    self.focus = self.previous.pop()
                    self.titles.pop()
                elif choice == 'Quit':
                    break
                # Assume anything else is a game to play.
                else:
                    self.play_game(self.games[choice.lower()], options.strip())
            # Check for non-menu choices.
            else:
                self.handle_cmd(response)

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
            stats_options = []
            if results[5] & 2:
                stats_options.append('cheat')
            if results[5] & 8:
                stats_options.append('gipf')
            if results[5] & 128:
                stats_options.append('xyzzy')
            stats_options = ' '.join(stats_options)
            self.do_stats('{} / {}'.format(self.game.name, stats_options))
            if stats_options:
                print('\nStatistics were calculated with the folloing options: {}.'.format(stats_options))
            again = self.human.ask('Would you like to play again? ').strip().lower()
            if again in ('!', '!!'):
                self.human.held_inputs = ['!']
                break
            elif again not in utility.YES:
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
        pairs = [[excel_column(n + 1), selection] for n, selection in enumerate(choices)]
        # Special characters for special choices
        pairs[-1][0] = '!'
        if pairs[-2][1] == 'Previous Menu':
            pairs[-2][0] = '<'
        # Display the menu.
        self.human.tell()
        self.human.tell(' > '.join(self.titles[-3:]))
        self.human.tell()
        for letter, choice in pairs:
            self.human.tell('{}: {}'.format(letter, choice))
        self.human.tell()
        # Return the meaning of the menu letters.
        menu_map = dict(pairs)
        if 'Q' not in menu_map:
            menu_map['Q'] = 'Quit'
        return dict(pairs)

    def show_scores(self, scores, score_type, options):
        """
        Show the base statistics for a set of scores or turns. (None)

        Parameters:
        scores: A list of scores or turns. (list of int)
        score_type: The type of scores or turns being shown. (str)
        options: User specified filtering and statistic options. (str)
        """
        if scores:
            score_stats = [min(scores), utility.mean(scores), utility.median(scores), max(scores)]
            self.human.tell('{}: {} - {:.1f} / {} - {}'.format(score_type, *score_stats))

    def show_stats(self, results, title = '', options = ''):
        """
        Show the statistics for a set of game results. (None)

        If the title is blank, it is taken from the game name in the first result.

        Parameters:
        results: The game results to generate stats for. (list of list)
        title: The title to print for the statistics. (str)
        options: User specified filtering and statistic options. (str)
        """
        # Check for empty results.
        if not results:
            self.human.tell('\nYou have never played that game.')
            return None
        # Process parameters.
        if not title:
            title = '\n{} Statistics'.format(results[0][0])
        # Process filters.
        results = self.filter_results(results, options)
        # Check for no valid results.
        if not results:
            self.human.tell('\nNo game results to show.')
            return None
        # Calculate total win-loss-draw and get data for streaks.
        stats = self.figure_win_loss_draw(results)
        game_wld, player_wld, current_streak, streak_type, longest_streaks = stats
        # Display the statistics to the user.
        # Display the title.
        self.human.tell(title)
        self.human.tell('-' * len(title))
        # Display win-loss-draw
        self.human.tell('Overall Win-Loss-Draw: {}-{}-{}'.format(*game_wld))
        self.human.tell('Player Win-Loss-Draw: {}-{}-{}'.format(*player_wld))
        # Display scores.
        self.show_scores([rez[4] for rez in results], 'Overall Scores', options)
        self.show_scores([rez[4] for rez in results if rez[1] and not rez[2]], 'Winning Scores', options)
        self.show_scores([rez[4] for rez in results if rez[2]], 'Losing Scores', options)
        # Display turns.
        self.show_scores([rez[5] for rez in results], 'Overall Turns', options)
        self.show_scores([rez[5] for rez in results if rez[1] and not rez[2]], 'Winning Turns', options)
        self.show_scores([rez[5] for rez in results if rez[2]], 'Losing Turns', options)
        # Display streaks.
        if longest_streaks[1]:
            self.human.tell('Longest winning streak: {}'.format(longest_streaks[1]))
        if longest_streaks[-1]:
            self.human.tell('Longest losing streak: {}'.format(longest_streaks[-1]))
        if longest_streaks[0]:
            self.human.tell('Longest drawing streak: {}'.format(longest_streaks[0]))
        streak_name = ('drawing', 'winning', 'losing')[streak_type]
        self.human.tell('You are currently on a {} game {} streak.'.format(current_streak, streak_name))


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


