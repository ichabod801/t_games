"""
socokit_game.py

The Solitaire Construction Kit, for dynamic solitaire game creation.

to do:
test multideck
    !! fails to carry over deck_specs
full option handling/automatic shortcuts
allow options for the base game.
allow mutli-deck to single-deck changes

Classes:
SoCoKit: A way to design a solitiare game on the fly. (game.Game)
"""


from ... import game
from . import solitaire_game as solitaire
from ... import utility


RULE_HELP = """
In general, the different types of rules apply to the different types of moves
you can make in a typical solitaire game: free rules apply to moving cards to
free cells, match rules apply to pairing cards for movement to the foundations,
and sorting rules apply to sending individual cards to the foundation.

Rules for moving cards on the tableau are a little more complicated. Build
rules apply to building one card onto another, and can apply to all of the
cards in the stack of cards being moved (depending on the rule). Lane rules
are the same, but for moving cards into empty lanes on the tableau. Pair rules
can apply to both building and laning. The base card of a stack being moved on
the tableau and the card it is moving onto must follow the pair rules. In
addition, every sequential pair of cards in a stack being moved on the tableau
(eithet building or laning) must follow the pair rules.

For example, in Yukon there are build rules but no pair rules. The base card
and the card it is being moved to matter, but what cards are in the stack don't
matter. However, FreeCell's only build rule is about moves being doable one
card at a time. The pair rules enforce the alternate color/desceding rank to
make sure only valid stacks are moved.

While rules typically only apply to the moving card and the card being moved
onto (and sometimes the stack on top of the moving card), they can access other
information about the location of the cards. For example, Canfield uses this to
make sure that stacks of cards that have been built up cannot be split apart.
"""


class SoCoKit(game.Game):
    """
    A way to design a solitiare game on the fly. (game.Game)

    Class Attributes:
    menu: The main menu items and their keys in the game definition. (list)

    Methods:
    add_checker: Get a new rule checker to add to the game. (function)
    build_game: Get the user's definition of the solitaire game. (dict)
    get_game_info: Get the inforamation defining the base game. (dict)
    make_game: Make a game object based on the design. (solitaire.Solitaire)
    modify_checkers: Modify a list of rules checkers. (list of function)
    show_game_menu: Show the current status of the game as a menu. (None)

    Static Methods:
    function_choice: Return menu item text for a function. (str)

    Overridden Methods:
    handle_options
    play
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
        ('I', 'Building Rules', 'build-checkers'),
        ('J', 'Empty Lane Rules', 'lane-checkers'),
        ('K', 'Free Cell Rules', 'free-checkers'),
        ('L', 'Matching Rules', 'match-checkers'),
        ('M', 'Pairing Rules', 'pair-checkers'),
        ('N', 'Sorting Rules', 'sort-checkers'),
        ('O', 'Dealers', 'dealers')]
    name = 'Solitaire Construction Kit'

    def add_checker(self, key, checkers):
        """
        Get a new rule checker to add to the game. (function)

        Parameters:
        key: The game_key for the checker type to add. (str)
        checkers: The current checkers. (list of function)
        """
        # Get all of the matching rule checker functions.
        prefix, dash, checker = key.partition('-')
        if prefix == 'dealers':
            prefix = 'deal'
        choices = []
        for name in dir(solitaire):
            if name.startswith(prefix):
                function = getattr(solitaire, name)
                choices.append(function)
        # Present a menu of the matching rule checker functions.
        self.human.tell('\n0: Cancel (do not add a rule).')
        for function_index, function in enumerate(choices, start = 1):
            self.human.tell(self.function_choice(function_index, function))
        # Get the user's choice.
        query = '\nWhich rule do you want to add (#)? '
        checker_index = self.human.ask_int(query, low = 0, high = len(choices), cmd = False)
        if not checker_index:
            return None
        checker = choices[checker_index - 1]
        # Check for higher order function.
        if 'Create' in checker.__doc__:
            # Find the parameters.
            params = checker.__code__.co_varnames[:checker.__code__.co_argcount]
            param_values = []
            # Get the parameter values based on the parameter names.
            for param in params:
                # Get basic integer values.
                if param == 'n':
                    query = 'How many cards should the rule apply to? '
                    value = self.human.ask_int(query, low = 1, cmd = False)
                # Get boolean values for up/down deals.
                elif param == 'up':
                    yes_no = self.human.ask('Should all the cards be dealt face up? ')
                    value = yes_no in utility.YES
                # Card ranks, based on the base game's deck.
                elif param == 'rank':
                    valid = self.base.deck.ranks
                    while True:
                        value = self.human.ask('What rank should the rule apply to? ').upper()
                        if value in valid:
                            break
                        self.human.error('That rank is not valid. Please choose one of {!r}.'.format(valid))
                param_values.append(value)
            # Get the derived rule checker using the user's parameter values.
            checker = checker(*param_values)
        return checker

    def build_game(self, game_info):
        """
        Get the user's definition of the solitaire game. (dict)

        Parameters:
        game_info: The definition of the base game. (dict)
        """
        # Set up the menu helpers.
        valid = list('ABCDEFGHIJKLMNO+!')
        checkers = dict(zip('IJKLMN', 'build free lane match pair sort'.split()))
        # Loop through main menu selections.
        while True:
            self.show_game_menu(game_info)
            choice = self.human.ask('\nWhat would you like to change? ').upper()
            if choice not in valid:
                # Allow for non-menu commands.
                self.handle_cmd(choice)
                continue
            elif choice == '+':
                # Handle being finished.
                break
            elif choice == '!':
                # Handle cancelling out (empty game_nnfo signifies quitting).
                game_info = {}
                break
            else:
                # Get the menu definition for the user choice
                choice, text, key = self.menu[ord(choice) - 65]
                if choice > 'H':
                    # Do a sub menu for changing rules checkers.
                    game_info[key] = self.modify_checkers(game_info, text, key)
                else:
                    # Get the new value from the user.
                    value = self.human.ask('\nWhat should the new value be? ')
                    # Convert based on the particular choice.
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
        """Return menu item text for a function. (str)"""
        description = func.__doc__.split('\n')[1].split('(')[0].strip()
        return '{}: {}'.format(char, description)

    def get_game_info(self, base_game):
        """
        Get the inforamation defining the base game. (dict)

        Parameters:
        base_game: A solitaire game. (solitiare.Solitaire)
        """
        # Make a viable instance of the game (to pull in hard coded solitaire options).
        self.base = base_game(self.human, 'none', silent = True)
        self.base.scores = {}
        self.base.set_up()
        # Get information from the attributes.
        game_info = {'num-cells': self.base.num_cells, 'wrap-ranks': self.base.wrap_ranks,
            'turn-count': self.base.turn_count, 'max-passes': self.base.max_passes}
        # Get information from the options, with defaults.
        game_info['deck-specs'] = self.base.options.get('deck-specs', [])
        game_info['num-tableau'] = self.base.options.get('num-tableau', 7)
        game_info['num-foundations'] = self.base.options.get('num-foundations', 4)
        game_info['num-reserve'] = self.base.options.get('num-reserve', 0)
        # Get the rule checker lists.
        for check_type in 'build free lane match pair sort'.split():
            key = '{}-checkers'.format(check_type)
            attribute = '{}_checkers'.format(check_type)
            game_info[key] = getattr(self.base, attribute)
        game_info['dealers'] = self.base.dealers
        return game_info

    def handle_options(self):
        """Design the solitaire game. (None)"""
        self.players = [self.human]
        self.player_index = 0
        # !! This will need to be redone to handle full option specification.
        # Get the base game.
        while self.raw_options and self.raw_options not in self.interface.games:
            self.human.tell('I do not recognize the game {!r}.'.format(self.raw_options))
            base_name = self.human.ask('\nPlease enter the game to use as a base (return for none): ')
            self.raw_options = base_name.strip().lower()
        # Use Solitaire Base as the default base game.
        if not self.raw_options:
            self.raw_options = 'solitaire base'
        base_game = self.interface.games[self.raw_options]
        # Get the base class the game will inherit from.
        if issubclass(base_game, solitaire.MultiSolitaire):
            self.base_class = solitaire.MultiSolitaire
        else:
            self.base_class = solitaire.Solitaire
        # Extract the game design from the base game.
        game_info = self.get_game_info(base_game)
        # Get a (unique) name for the game.
        while True:
            game_name = self.human.ask('\nWhat is the name of the game you are making? ').strip()
            if game_name.lower() in self.interface.games:
                self.human.tell('That name is already taken, please choose another.')
            else:
                break
        game_info['name'] = game_name
        # Build the game.
        game_info = self.build_game(game_info)
        # Check for exit without playing.
        if game_info:
            self.game = self.make_game(game_info)
        else:
            self.option_set.errors.append('Game aborted by the user.')

    def make_game(self, game_info):
        """
        Make a game object based on the design. (solitaire.Solitaire)

        Parameters:
        game_info: The definition of the game.
        """
        # Use the base game to determine solitaire vs. multisolitaire.
        class ConstructedGame(self.base_class):
            name = game_info['name']
            def handle_options(self):
                # Use the game definition for the options.
                self.options = game_info
            def set_checkers(self):
                # Extract the rule checkers and the dealers.
                for checker_type in 'build free lane match pair sort'.split():
                    attr = '{}_checkers'.format(checker_type)
                    key = '{}-checkers'.format(checker_type)
                    setattr(self, attr, game_info[key])
                self.dealers = game_info['dealers']
        # Return the initialized game.
        return ConstructedGame(self.human, '')

    def modify_checkers(self, game_info, text, key):
        """
        Modify one of the lists of rules checkers. (list of function)

        Parameter:
        game_info: The definition of the game. (dict)
        text: The description of the list of rules checkers. (str)
        key: The key in game_info for the list of rules checkers. (str)
        """
        # Get an independent copy of the list.
        checkers = game_info[key][:]
        # Loop through menu choices.
        while True:
            # Show the rule checkers.
            self.human.tell('\n{}:'.format(text))
            for checker_index, checker in enumerate(checkers, start = 1):
                self.human.tell(self.function_choice(checker_index, checker))
            # Show the menu options.
            self.human.tell('\nOptions:')
            self.human.tell('A: Add Rule')
            self.human.tell('D: Delete Rule')
            if text == 'Dealers':
                self.human.tell('R: Reorder Rules')
            self.human.tell('<: Return to Main Design Menu')
            choice = self.human.ask('\nWhat is your choice? ').upper()
            # Handle new checkers.
            if choice == 'A':
                new_checker = self.add_checker(key, checkers)
                if new_checker is not None:
                    checkers.append(new_checker)
            # Handle getting rid of checkers.
            elif choice == 'D':
                query = '\nWhich rule do you want to delete (#)? '
                checker_index = self.human.ask_int(query, low = 1, high = len(checkers), cmd = False) - 1
                del checkers[checker_index]
            # Handle reordering rules (dealers).
            elif choice == 'R' and text == 'Dealers':
                query = '\nEnter the rule numbers in the order you want them to be: '
                order = self.human.ask_int_list(query, valid = range(1, len(checkers) + 1), cmd = False)
                checkers = [checkers[index - 1] for index in order]
            # Handle going back to the main menu.
            elif choice == '<':
                break
            # Handle invalid choices.
            else:
                self.human.error('\nThat is not a valid choice.')
        # Return the modified list of checkers.
        return checkers

    def play(self):
        """Play the game. (list of int)"""
        return self.game.play()

    def show_game_menu(self, game_info):
        """
        Show the current status of the game as a menu. (None)

        Parameters:
        game_info: The definition of the game. (dict)
        """
        # Make a text menu from the menu specification.
        lines = ['']
        for char, text, key in self.menu:
            # Show value or number of rule checkers.
            if char < 'I':
                value = game_info[key]
            else:
                value = len(game_info[key])
            lines.append('{}) {}: {}'.format(char, text, value))
        # Add a quit option
        lines.append('+) Finish Construction and Play')
        lines.append('!) Quit Without Playing')
        # Show it to the human.
        self.human.tell('\n'.join(lines))
