"""
socokit_game.py

The Solitaire Construction Kit, for dynamic solitaire game creation.

Classes:
SoCoKit: A way to design a solitiare game on the fly. (game.Game)
"""


from ... import game
from . import solitaire_game as solitaire


class SoCoKit(game.Game):
    """
    A way to design a solitiare game on the fly. (game.Game)

    Overridden Methods:
    handle_options
    """

    aka = ['SoCoKit', 'SoCK']
    categories = ['Card Games', 'Solitaire Games']
    menu = [('A', 'Name', 'name'),
        ('B', '# of Cards Dealt by Turn Command', 'turn-count'),
        ('C', '# of Foundation Piles', 'num-foundations'),
        ('D', '# of Free Cells', 'num-cells'),
        ('E', '# of Reserve Piles', 'num-reserve'),
        ('F', '# of Tableau Piles', 'num-tableau'),
        ('G', 'Maximum Passes Through Stock', 'max-passes'),
        ('H', 'Wrap Ranks for Building/Sorting', 'wrap-ranks'),
        ('I', 'Build Checkers', 'build-checkers'),
        ('J', 'Free Checkers', 'free-checkers'),
        ('K', 'Lane Checkers', 'lane-checkers'),
        ('L', 'Match Checkers', 'match-checkers'),
        ('M', 'Pair Checkers', 'pair-checkers'),
        ('N', 'Sort Checkers', 'sort-checkers'),
        ('O', 'Dealers', 'dealers')]
    name = 'Solitaire Construction Kit'

    def add_checker(self, key, checkers):
        """
        Get a new checker to add to the game. (function)

        Parameters:
        key: The game_key for the checker type to add. (str)
        checkers: The current checkers. (list of function)
        """
        prefix, dash, checker = key.partition('-')
        choices = []
        for name in dir(solitaire):
            if name.startswith(prefix):
                function = getattr(solitaire, name)
                if function not in checkers:
                    choices.append(function)
        self.human.tell()
        for function_index, function in enumerate(choices, start = 1):
            self.human.tell(self.function_choice(function_index, function))
        query = '\nWhich function do you want to add (#)? '
        checker_index = self.human.ask_int(query, low = 1, high = len(choices), cmd = False) - 1
        return choices[checker_index]

    def build_game(self, game_info):
        """
        Construct the solitaire game. (dict)

        Parameters:
        game_info: The definition of the base game. (dict)
        """
        valid = list('ABCDEFGHIJKLMNO!')
        checkers = dict(zip('IJKLMN', 'build free lane match pair sort'.split()))
        while True:
            self.show_game(game_info)
            choice = self.human.ask('\nWhat would you like to change? ').upper()
            if choice not in valid:
                self.handle_cmd(choice)
                continue
            elif choice == '!':
                break
            else:
                choice, text, key = self.menu[ord(choice) - 65]
                if choice > 'H':
                    game_info[key] = self.modify_checkers(game_info, text, key)
                else:
                    value = self.human.ask('\nWhat should the new value be? ')
                    if choice in 'BDEFG':
                        try:
                            value = int(value)
                        except ValueError:
                            self.human.error('That is not a valid setting (integers only).')
                            continue
                    elif choice == 'H':
                        value = value.lower() in ('true', 't', '1')
                    game_info[key] = value
        return game_info

    @staticmethod
    def function_choice(char, func):
        """Return sensible choice text for a function."""
        name = func.__name__
        description = func.__doc__.split('\n')[1].split('(')[0].strip()
        return '{}: {}\n   {}'.format(char, name, description)

    def get_game_info(self, base_game):
        """
        Get the inforamation defining the game. (dict)

        Parameters:
        base_game: A solitaire game. (solitiare.Solitaire)
        """
        base = base_game(self.human, 'none', silent = True)
        base.scores = {}
        base.set_up()
        game_info = {'num-cells': base.num_cells, 'wrap-ranks': base.wrap_ranks,
            'turn-count': base.turn_count, 'max-passes': base.max_passes}
        game_info['deck-specs'] = base.options.get('deck-specs', [])
        game_info['num-tableau'] = base.options.get('num-tableau', 7)
        game_info['num-foundations'] = base.options.get('num-foundations', 4)
        game_info['num-reserve'] = base.options.get('num-reserve', 0)
        for check_type in 'build free lane match pair sort'.split():
            game_info['{}-checkers'.format(check_type)] = getattr(base, '{}_checkers'.format(check_type))
        game_info['dealers'] = base.dealers
        return game_info

    def handle_options(self):
        """Design the solitaire game. (None)"""
        while self.raw_options and self.raw_options not in self.interface.games:
            self.human.tell('I do not recognize the game {!r}.'.format(self.raw_options))
            base_name = self.human.ask('\nPlease enter the game to use as a base: ')
            self.raw_options = base_name.strip().lower()
        if not self.raw_options:
            self.raw_options = 'solitaire base'
        base_game = self.interface.games[self.raw_options]
        game_info = self.get_game_info(base_game)
        while True:
            game_name = self.human.ask('\nWhat is the name of the game you are making? ').strip()
            if game_name.lower() in self.interface.games:
                self.human.tell('That name is already taken, please choose another.')
            else:
                break
        game_info['name'] = game_name
        game_info = self.build_game(game_info)
        self.game = self.make_game(game_info)

    def make_game(self, game_info):
        """
        Make a game object based on the design. (solitaire.Solitaire)

        Parameters:
        game_info: The definition of the game.
        """
        class ConstructedGame(solitaire.Solitaire):
            name = game_info['name']
            def handle_options(self):
                self.options = game_info
            def set_checkers(self):
                for checker_type in 'build free lane match pair sort'.split():
                    attr = '{}_checkers'.format(checker_type)
                    key = '{}-checkers'.format(checker_type)
                    setattr(self, attr, game_info[key])
                self.dealers = game_info['dealers']
        return ConstructedGame(self.human, '')

    def modify_checkers(self, game_info, text, key):
        """
        Modify one of the lists of rules checkers. (list of function)

        Parameter:
        game_info: The definition of the game. (dict)
        text: The description of the list of rules checkers. (str)
        key: The key in game_info for the list of rules checkers. (str)
        """
        checkers = game_info[key][:]
        while True:
            self.human.tell('\n{}:'.format(text))
            for checker_index, checker in enumerate(checkers, start = 1):
                self.human.tell(self.function_choice(checker_index, checker))
            self.human.tell('\nOptions:')
            self.human.tell('A: Add Function')
            self.human.tell('D: Delete Function')
            self.human.tell('<: Return to Main Design Menu')
            choice = self.human.ask('\nWhat is your choice? ').upper()
            if choice == 'A':
                checkers.append(self.add_checker(key, checkers))
            elif choice == 'D':
                query = 'Which checker do you want to delete (#)? '
                checker_index = self.human.ask_int(query, low = 1, high = len(checkers), cmd = False) - 1
                del checkers[checker_index]
            elif choice == '<':
                break
        return checkers

    def play(self):
        return self.game.play()

    def show_game(self, game_info):
        """
        Show the current status of the game. (None)

        Parameters:
        game_info: The definition of the game. (dict)
        """
        lines = ['']
        for char, text, key in self.menu:
            if char < 'I':
                value = game_info[key]
            else:
                value = len(game_info[key])
            lines.append('{}) {}: {}'.format(char, text, value))
        lines.append('!) Finished Construction')
        self.human.tell('\n'.join(lines))

