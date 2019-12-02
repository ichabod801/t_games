"""
interface.py

The interface for the t_games game suite.

Copyright (C) 2018-2020 by Craig O'Brien and the t_games contributors.
See the top level __init__.py file for details on the t_games license.

Contants:
HELP_TEXT: General help for the interface. (str)
LICENSE: Info on the GPLv3 license that t_games uses. (str)
RULES: Some basic guidelines for life. (str)

Classes:
Interface: A menu interface for playing games. (OtherCmd)
RandomValve: A random variable that gets more likely to be true. (object)
Statistics: Statistics on a sequence of t_games results. (object)

Functions:
excel_column: Convert a number into a Excel style column header. (str)
"""


import os
import random
import re
from string import ascii_uppercase

from . import full_credits
from . import game
from . import other_cmd
from . import player
from . import utility


# General help for the interface.
HELP_TEXT = """
General interface help (?).

The games are organized into categories. You can use the menu to browse
through the categories to find the game you want. Just type in the letter or
letters to the left of the colon to make a selection. You can type home at any
point to get back to the top of the menu.

When the game is over you will be shown your overall statistics for that game.
From the interface you can see your statistics for any game by using the stats
command.

You may also type in other commands as listed below. This can allow playing
games without going through the menu system or getting information about the
games that can be played or the system in general.

You can get this help text by typing help or ?
"""


# Info on the GPLv3 license that t_games uses.
LICENSE = """
Copyright (C) 2018-2020 by Craig O'Brien and the t_games contributors.

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
    rules: The rules. (str)
    word_list: The relative location of a word list for word games. (str)

    Methods:
    category_games: Get the games in the current category. (list of game.Game)
    do_credits: Show the programming credits for the interface. (bool)
    do_games: List the available games. (bool)
    do_home: Go to the top of the menu tree. (bool)
    do_play: Play a game with the specified options, if any. (bool)
    do_random: Play a random game. (bool)
    do_rules: Show the rules for the specified game. (bool)
    do_stats: Show game statistics. (bool)
    load_games: Load all of the games defined locally. (None)
    menu: Run the game selection menu. (None)
    play_game: Play a selected game. (None)
    show_menu: Display the menu options to the user. (dict)

    Overridden Methods:
    __init__
    default
    """

    help_text = {'help': HELP_TEXT, 'license': LICENSE}
    rules = RULES
    word_list = 'other_games/3of6game.txt'

    def __init__(self, human):
        """
        Set up the interface. (None)

        Parameters:
        human: The user making menu choices/entering commands. (str)
        """
        # Set the attributes.
        self.human = human
        self.games, self.categories = game.load_games()
        self.valve = RandomValve()
        # Inherit aliases from parent classes.
        self.aliases = {}
        for cls in reversed(self.__class__.__mro__):
            if hasattr(cls, 'aliases'):
                self.aliases.update(cls.aliases)

    def __repr__(self):
        """Generate a debugging text representation. (str)"""
        return '<Interface {!r}>'.format(self.human)

    def category_games(self):
        """Get the games in the current category. (list of game.Game)"""
        # Depth first search of the game category tree.
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
            self.human.error('\nThat is an invalid selection.')

    def do_credits(self, arguments):
        """
        Show the full t_games credits.
        """
        self.human.tell(full_credits.FULL_CREDITS)
        self.human.ask('Press Enter to continue: ')
        return True

    def do_games(self, arguments):
        """
        List the available games.

        The games listed are aware of your location in the menu, so only games in the
        current category are listed.
        """
        # Get the games, sorted alphabetically.
        games = self.category_games()
        games.sort(key = lambda game: game.name)
        # Print the game list with aliases.
        self.human.tell()
        for game in games:
            if game.aka:
                self.human.tell('{} ({})'.format(game.name, ', '.join(game.aka)))
            else:
                self.human.tell(game.name)
        self.human.ask('\nPress Enter to continue: ')

    def do_home(self, arguments):
        """
        Go to the top of the menu tree.
        """
        self.focus = self.categories
        self.previous = []
        self.titles = ['Home Menu']

    def do_play(self, arguments):
        """
        Play a game with the specified options.

        Anything after the play command but before the first forward slash (/) is
        taken as the name of the game or an alias for a game. Anything after the first
        forward slash is given as option settings to the game.

        Note that if the game has options and you don't specify any, it will
        immediately ask you if you want to change the options. To avoid this you can
        either specify the 'none' option (play game-name / none) or follow the game
        name with a semi-colon.

        Also note that the play command is the default. If you just type in a game
        name, the system will start that game.
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
        else:
            # Warn about unknown games.
            self.human.error("\nI don't know how to play that game.")
        return True

    def do_random(self, arguments):
        """
        Play a random game.

        The random command is aware of your location in the menu tree, so it will only
        choose from games in the current category. To play a random choice from all
        games, regardless of the current menu category, provide the 'all' argument to
        the random command.
        """
        if arguments.strip().lower() == 'all':
            game_class = random.choice(list(self.games.values()))
        else:
            game_class = random.choice(self.category_games())
        self.play_game(game_class, '')
        self.human.tell()

    def do_rules(self, arguments):
        """
        Show the rules for the game specified as an argument.

        Without a game specified, this just shows the rules for the current game.
        """
        arguments = arguments.lower()
        if not arguments:
            # Show the general rules.
            print(self.rules)
        elif arguments in self.games:
            # Show rules for a specific game.
            self.human.tell(self.games[arguments].rules)
            self.human.ask('Press Enter to continue: ')
        else:
            # Show an error.
            self.human.error("\nI do not know the rules to that game.")
        return True

    def do_stats(self, arguments):
        """
        Show game statistics.

        If no arguments are given to the stats command, it will display the stats for
        all of the games in the current menu category. If the argument given to the
        stats command is a game name or an alias for a game, stats will be given for
        that game. If 'all' is given as the argument to the stats command, stats will
        be shown for all games.

        Options to the stats command (given after a slash) can be used to filter the
        results. The format for filtering options is type:value. The filter types are:
            * flags: Include only games with the given flags set (flags:3).
            * flags!: Exclude any games with the given flags set (flags!:3).
            * opt: Include only games using the given option setting (opt:bar=2).
            * opt!: Exclude any games using the given option setting (opt!:bar=2).
            * opt-name: Include only games using the given option (opt-name:bar).
            * opt-name!: Exclude any games using the given option (opt-name!:bar).

        Game options using in statistics filtering options must be the full name. You
        may not use option aliases.

        You may also use the 'clean' filter, which only includes games using the
        default option settings.
        """
        # Process the arguments.
        arguments, slash, options = arguments.partition('/')
        arguments = arguments.strip()
        options = options.strip().lower()
        # Handle category stats.
        if not arguments:
            # Find the relevant games.
            names = [game.name for game in self.category_games()]
            relevant = [result for result in self.human.results if result[0] in names]
            # Show the category and individual game stats.
            stats = Statistics(relevant, options, 'Category Statistics')
            self.human.tell(stats)
            games = sorted(set([result[0] for result in relevant]))
            for game in games:
                relevant = [result for result in self.human.results if result[0] == game]
                stats = Statistics(relevant, options = options)
                self.human.tell(stats)
        # Handle specific game stats.
        elif arguments.lower() in self.games:
            # Find the relevant results.
            game_class = self.games[arguments.lower()]
            relevant = [result for result in self.human.results if result[0] == game_class.name]
            if relevant:
                # Show any relevant statistics
                stats = Statistics(relevant, options = options)
                self.human.tell(stats)
            else:
                # Give a warning if there are no matching resutls.
                self.human.error('You have never played {!r}.'.format(arguments))
        # Handle overall stats.
        elif arguments.lower() == 'all':
            # Show the overall statistics.
            stats = Statistics(self.human.results, options, 'Overall Statistics')
            self.human.tell(stats)
            games = sorted(set([result[0] for result in self.human.results]))
            # Show the stats for the individual games.
            for game in games:
                relevant = [result for result in self.human.results if result[0] == game]
                stats = Statistics(relevant, options = options)
                self.human.tell(stats)
        # Handle the session statistics.
        elif arguments.lower() == 'session':
            session_results = self.human.results[self.human.session_index:]
            session_stats = Statistics(session_results, 'all', 'Session Statistics')
            self.human.tell(session_stats)
        # Show an error for invalid game names.
        else:
            self.human.error("I don't know that game.")

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
        self.human.tell("Copyright (C) 2018-2020 by Craig O'Brien and the t_games contributors.")
        self.human.tell("For more details type 'help' or 'help license'.")
        # Loop through player choices.
        while True:
            # Show the menu and get the possible choices.
            menu_map = self.show_menu(self.focus)
            response = self.human.ask('\nWhat is your selection? ').strip()
            letter, slash, options = response.partition('/')
            letter = letter.strip().upper()
            # Check for menu choices.
            if letter in menu_map:
                choice = menu_map[letter]
                # Check for sub-category choices.
                if choice[:-9] in self.focus['sub-categories']:
                    self.previous.append(self.focus)
                    self.focus = self.focus['sub-categories'][choice[:-9]]
                    self.titles.append(choice[:-9])
                # Check for backing up.
                elif choice == 'Previous Menu':
                    self.focus = self.previous.pop()
                    self.titles.pop()
                # Check for quiting.
                elif choice == 'Quit':
                    if self.human.session_index < len(self.human.results):
                        self.do_stats('session / cheat xyzzy gipf')
                        self.human.tell('\nThanks for playing! Come back soon!\n')
                    else:
                        self.human.tell('\nYou no play. Me feel sad. :(\n')
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
        # Don't play if there are option related errors.
        if self.game.option_set.errors:
            return False
        # Play the game until the player wants to stop.
        while True:
            # Play the game.
            results = self.game.play()
            self.human.store_results(self.game.name, results)
            # Show the statics, including the game just played.
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
                message = '\nStatistics were calculated with the following options: {}.'
                self.human.tell(message.format(stats_options))
            # See if they want to play again.
            again = self.human.ask('\nWould you like to play again? ').strip().lower()
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
        # Return the meaning of the menu letters.
        menu_map = dict(pairs)
        return dict(pairs)


class RandomValve(object):
    """
    A binary random variable that gets more likely to be true. (object)

    The valve starts out with a set probabiliy (its parameter). Each time it is
    checked and the response is false, the chance of a true value increases. The
    increase is random, but proportional to the current probability of a true
    value. When the response is true, the valve is reset to it's original set
    probability.

    This is a special random valve, that automatically returns false with no changes
    to the probability of a true value if it is triggered by the same game as it's
    last check.

    Attributes:
    last: The last game to call the valve. (game.Game)
    p: The base probability. (float)
    q: The current probability. (float)

    Methods:
    blow: Check the valve for a blow (true value). (bool)

    Overridden Methods:
    __init__
    __repr__
    """

    def __init__(self, p = 0.1):
        """
        Set up the attributes. (None)

        Parameters:
        p: The initial probability of true. (float)
        """
        self.p = p
        self.q = p
        self.last = None

    def __repr__(self):
        """Return a debugging text representation. (str)"""
        return '<RandomValve {:.4f}/{:.4f}>'.format(self.p, self.q)

    def blow(self, trigger):
        """
        Check for a true value.

        Parameters:
        trigger: The game triggering the check. (game.Game)
        """
        # Check for repeated triggers.
        if trigger is self.last:
            return False
        self.last = trigger
        # Check for true response.
        check = random.random()
        if check < self.q:
            # Reset probability.
            self.q = self.p
            return True
        else:
            # Increase probability.
            self.q += self.q * check
            return False


class Statistics(object):
    """
    Statistics on a sequence of t_games results. (object)

    Attributes:
    game_wld: The per game win/loss/draw counts. (list of int)
    options: The options for filtering the results. (str)
    results: The categoriezed results. (dict of str: list)
    player_wld: The per player win/loss/draw counts. (list of int)
    stats: The categorized statistics. (dict of str: dict)
    title: The title for the statistics. (str)

    Methods:
    bin_results: Categorize results based on win, loss, or draw. (None)
    filter_results: Filter game results based on user requests. (list of lists)
    sequence_stats: Calculate and store statistics for some numbers. (None)

    Overridden Methods:
    __init__
    __bool__
    __repr__
    __str__
    """

    def __init__(self, results = [], options = '', title = ''):
        """
        Set up the statistics attributes. (None)

        Parameters:
        results: The raw game results. (list of list)
        options: The options for filtering the results. (str)
        title: The title for the statistics to show. (str)
        """
        # Set provided attributes.
        self.options = options.lower().split()
        if title or not results:
            self.title = title
        else:
            self.title = '{} Statistics'.format(results[0][0])
        # Set the default attributes.
        self.results, self.stats = {}, {}
        for result_type in ('win', 'loss', 'draw', 'overall'):
            self.results[result_type] = []
            self.stats[result_type] = {}
        self.results['overall'] = self.filter_results(results, self.options)
        self.game_wld, self.player_wld = [0, 0, 0], [0, 0, 0]
        # Calculate statistics.
        self.bin_results()
        for result_type in ('win', 'loss', 'draw', 'overall'):
            self.sequence_stats(result_type, 'scores', [result[4] for result in self.results[result_type]])
            self.sequence_stats(result_type, 'turns', [result[5] for result in self.results[result_type]])

    def __bool__(self):
        """Boolean value of the stats, or are there results? (bool)"""
        return bool(self.results['overall'])

    def __nonzero__(self):
        """Boolean value for version 2.7."""
        return self.__bool__()

    def __repr__(self):
        """Debugging text representation. (str)"""
        result_count = len(self.results['overall'])
        result_plural = utility.plural(result_count, 'result')
        return '<Statistics object with {} for {} {}>'.format(self.title, result_count, result_plural)

    def __str__(self):
        """Human readable text representation. (str)"""
        # Check for empty results.
        if not self.results['overall']:
            return '\nNo statistics are available for those settings.'
        # Set up the output
        lines = ['', self.title, '-' * len(self.title)]
        # Add the win-loss-draw numbers.
        lines.append('Overall Win-Loss-Draw: {}-{}-{}'.format(*self.game_wld))
        lines.append('Player Win-Loss-Draw: {}-{}-{}'.format(*self.player_wld))
        # Add the scores and turns.
        stat_format = '{} {}: {} : {:.2f} / {:.1f} : {}'
        for prefix in ('scores', 'turns'):
            for result_type, word in (('overall', 'Overall'), ('win', 'Winning'), ('loss', 'Losing')):
                if self.results[result_type]:
                    stats = [word, prefix.capitalize()]
                    for stat in ('min', 'mean', 'median', 'max'):
                        stats.append(self.stats[result_type]['{}-{}'.format(prefix, stat)])
                    lines.append(stat_format.format(*stats))
        # Add the streaks.
        if self.stats['win']['longest-streak']:
            lines.append('Longest winning streak: {}'.format(self.stats['win']['longest-streak']))
        if self.stats['loss']['longest-streak']:
            lines.append('Longest losing streak: {}'.format(self.stats['loss']['longest-streak']))
        if self.stats['draw']['longest-streak']:
            lines.append('Longest drawing streak: {}'.format(self.stats['draw']['longest-streak']))
        streak_name = ('drawing', 'winning', 'losing')[self.stats['overall']['streak-type']]
        current_streak = self.stats['overall']['current-streak']
        lines.append('You are currently on a {} game {} streak.'.format(current_streak, streak_name))
        return '\n'.join(lines)

    def bin_results(self):
        """Categorize results based on win, loss, or draw. (None)"""
        # Loop through results storing totals and streak data.
        wins = []
        for result in self.results['overall']:
            win, loss, draw = result[1:4]
            if result[-2] & 256:
                # Handle match play.
                if win > loss:
                    self.results['win'].append(result)
                    wins.append(1)
                elif loss > win:
                    self.results['loss'].append(result)
                    wins.append(-1)
                else:
                    self.results['draw'].append(result)
                    wins.append(0)
            else:
                # Handle single games.
                if not loss and not win:
                    self.results['draw'].append(result)
                    wins.append(0)
                elif not loss:
                    self.results['win'].append(result)
                    wins.append(1)
                else:
                    self.results['loss'].append(result)
                    wins.append(-1)
            # Update the per-player stats.
            self.player_wld[0] += win
            self.player_wld[1] += loss
            self.player_wld[2] += draw
        # Update the per-game stats.
        self.game_wld = [len(self.results[result_type]) for result_type in ('win', 'loss', 'draw')]
        # Get streaks.
        current_streak, streak_type, longest_streaks = utility.streaks(wins)
        self.stats['overall']['current-streak'] = current_streak
        self.stats['overall']['streak-type'] = streak_type
        self.stats['win']['longest-streak'] = longest_streaks[1]
        self.stats['loss']['longest-streak'] = longest_streaks[-1]
        self.stats['draw']['longest-streak'] = longest_streaks[0]

    def filter_results(self, results, options):
        """
        Filter game results based on user requests. (list of lists)

        Paramters:
        results: The game results to filter. (list of lists)
        options: The user provided options, including any filters. (str)
        """
        # parse filters
        new_options = []
        for option in options:
            if new_options and (option == ':' or option.startswith(':') or new_options[-1].endswith(':')):
                new_options[-1] += option
            elif new_options and (option == '=' or option.startswith('=') or new_options[-1].endswith('=')):
                new_options[-1] += option
            else:
                new_options.append(option)
        options = new_options
        # Do the predefined filters.
        if 'cheat' not in options:
            results = [result for result in results if not result[6] & 2]
        if 'gipf' not in options:
            results = [result for result in results if not result[6] & 8]
        if 'xyzzy' not in options:
            results = [result for result in results if not result[6] & 128]
        # Do the option filters.
        if 'clean' in options:
            results = [result for result in results if not result[-1]]
        else:
            # Filter for specific option settings.
            opt_filters = [option for option in options if option[:4] in ('opt:', 'opt!')]
            for opt_filter in opt_filters:
                filter_type, option = opt_filter.split(':')
                if filter_type == 'opt':
                    results = [result for result in results if option in result[-1].split()]
                else:
                    results = [result for result in results if option not in result[-1].split()]
            # Filter for options by name.
            name_filters = [option for option in options if option[:9] in ('opt-name:', 'opt-name!')]
            for name_filter in name_filters:
                filter_type, name = name_filter.split(':')
                regex = re.compile('\\b{}\\b'.format(name))
                if filter_type == 'opt-name':
                    results = [result for result in results if regex.search(result[-1])]
                else:
                    results = [result for result in results if not regex.search(result[-1])]
        # Do the flag filters.
        flag_filters = [option for option in options if option[:5] in ('flag:', 'flag!')]
        for flag_filter in flag_filters:
            filter_type, flags = flag_filter.split(':')
            try:
                flags = int(flags)
            except ValueError:
                continue
            if filter_type == 'flag':
                results = [result for result in results if result[-2] & flags]
            else:
                results = [result for result in results if not (result[-2] & flags)]
        # Return the filtered data.
        return results

    def sequence_stats(self, result_type, prefix, data):
        """
        Calculate and store statistics for some numbers. (None)

        Paramters:
        result_type: Win, loss, or draw. (str)
        prefix: What the data represents. (str)
        data: The numbers to get statistics for. (list of number)
        """
        if self.results[result_type]:
            self.stats[result_type]['{}-mean'.format(prefix)] = utility.mean(data)
            self.stats[result_type]['{}-median'.format(prefix)] = utility.median(data)
            self.stats[result_type]['{}-min'.format(prefix)] = min(data)
            self.stats[result_type]['{}-max'.format(prefix)] = max(data)


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
    # Run the unit testing.
    from t_tests.interface_test import *
    unittest.main()
