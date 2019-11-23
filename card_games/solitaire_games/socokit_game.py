"""
socokit_game.py

The Solitaire Construction Kit, for dynamic solitaire game creation.

Constants:'
ATTRIBUTE_HELP: Help text for changing game attributes. (str)
CREDITS: The credits for the Solitaire Construction Kit. (str)
RULE_HELP: Help text for changing rule functions. (str)
RULES: Basic instructions for the Solitaire Construction Kit. (str)

Classes:
SoCoKit: A way to design a solitiare game on the fly. (game.Game)
"""


from ... import game
from . import solitaire_game as solitaire
from ... import utility


ATTRIBUTE_HELP = """
The following are attributes of solitaire games that can be changed in the
main design menu. In parentheses after each one is the name of the SoCK option
for that attribute.

The number of cards dealt by the turn command. This is the number of cards
    turned over from the stock into the waste. (turn-count=)
The number of foundation piles. This should generally not be messed with. In
    matching games it should be one, in one-deck games it should be four, and
    in two-deck games it should be eight. The only real exception to this is
    Quadrille with the sort_up_down rule function. (num-foundations=)
The number of free cells. You can use this to add free cells to just about any
    game. (num-cells=)
The number of reserve piles. These are non-building piles for holding cards.
    (num-reserve=)
The number of tableau piles. Generally more tableau piles makes games easier
    while fewer tableau piles makes games harder. Especially with tableau
    piles, you may want to change the dealers if you change this attribute.
    (num-tableau)
The maximum number of passes through the stock. Some games put a limit on the
    number of times you can go through the stock by turning over cards into the
    waste. If you don't want a limit on this, set this attribute to -1.
    (max-passes)
Wrapping ranks for building/sorting. This should only be true if the foundation
    piles don't start with an ace. If they don't, this needs to be true or the
    game will be unwinnable. (wrap-ranks)
"""

CREDITS = """
Construction Kit Design: Craig "Ichabod" O'Brien
Construction Kit Programming: Craig "Ichabod" O'Brien
Inspired by the Pinball Construction Kit made by Bill Budge
"""

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
and the card it is being moved onto matter, but what cards are in the stack
don't matter. However, FreeCell's only build rule is about moves being doable
one card at a time. The pair rules enforce the alternate color/desceding rank
to make sure only valid stacks are moved.

While rules typically only apply to the moving card and the card being moved
onto (and sometimes the stack on top of the moving card), they can access other
information about the location of the cards. For example, Canfield uses this to
make sure that stacks of cards that have been built up cannot be split apart.

The option names for the rules options are:
build-checkers=: Rules for building on the tableau.
dealers=: Rules for dealing the initial layout of cards.
free-checkers=: Rules for moving cards to free cells.
lane-checkers=: Rules for moving cards to empty lanes.
match-checkers=: Rules for matching cards together.
pair-checkers=: Rules for stacking cards on the tableau, both when laning and
    building.
sort-checkers=: Rules for sorting cards to the foundations.

The values for the above options are slash-delimited lists of rule function
names or calls to functions that create rule functions. The names of the rule
checking functions are hidden by default in the design menu interface, but
there is an option to show them. When using calls to functions in option values
be sure to remove all spaces. Any spaces will mess up the option parsing.

Note that not all game rules are represented by rule checking functions. Some
of them are hard-coded as methods of specific game classes. This is especially
true of modified rules for the turn command, as in Monte Carlo, Pyramid, and
Spider. Access to those rules can only be obtained by basing your game on those
games.
"""

RULES = """
You make the rules for this one.

The Solitaire Construction Kit (SoCK) is for designing your own solitaire game.
You choose the game to base your game off of, modify the rules of that game,
and then you can play the game you just created. If you don't choose a game to
base your game off of, it will be based off a generalized solitaire game with
almost no rules.

You will be presented with a menu of different rules you can change. The first
options are the numeric attributes of the game, like how many of each type of
pile there are. Selecting that option will allow you to enter a new value for
that attribute. To get detailed information on the attributes, type 'help
attributes'.

After the attributes are the different types of rules, including the rules for
dealing the cards (the 'dealers'). In the main design menu only the number of
each type of rule is shown. Choosing the option for a particular type of rule
gives you a list of those rules, and a sub-menu allowing you to add or remove
rules from that list. For an explanation of the different types of rules, type
'help rules'.

Some of the rules are generalized types of rules, like deal a certain number of
cards. These will be listed in the menu as 'Create a rule that ...'. If you
choose to add such a rule, you will be prompted for the specific parameters of
the rule you want. Rules in the game that have been created that way will have
a '[created]' tag to identify them.

Order doesn't matter for most of the rules, but it does matter for the rules
about how to deal the cards. In the menu for the dealers, you will have the
option to reorder the rules. You just give the numbers of the rules as listed
above the menu, in the order you want them. Only the rules you list will be
kept, so you can use this to delete rules as well.

After you play the game, you will have the option to create a shortcut for the
game. If you choose this option, a shortcut will be created in your personal
shortcuts that will take you into SoCK, redesign the game, and take you
straight to playing it again. Note that this will override any previous
shortcut using the name of the game you just made (with spaces replaced by
hypens).

In addition to the options for attributes and rules, there are the following
options for the system in general:

name: The name of the game you are designing.
no-build: Skip the main design menu and go straight to playing the game.

Note that you can provide options for the base game, to start with that game
and those options. Options for SoCK come after the base game options, and are
separated from them with a pipe character (|). Consider these four commands
for using SoCK:

1. sock / klondike
2. sock / klondike / switch-one
3. sock / klondike / switch-one | num-cells = 2 no-build
4. sock / klondike | num-cells = 2 name = Horns

The first one starts SoCK with Klondike as the base game. The second starts
with Klondike using the switch-one option as the base game. The third one has
Klondike with the switch-one option as the base game, adds two free cells, and
goes straight to playing the game (although you will be asked for a name). The
last one uses Klondike with no options as the base game, but adds two free
cells and gives the game the name 'Horns'.

There is no double checking done on the rules or attributes you choose for your
game. So it is entirely possible to create a game that is not winnable. Watch
out for that.
"""


class SoCoKit(game.Game):
    """
    A way to design a solitiare game on the fly. (game.Game)

    Attributes:
    base_class: The class of the base game to build off of. (type)
    base_game: An instance of the base game to build off of. (solitaire.Solitaire)
    base_options: The user provided options for the base game. (text)
    build_options: The user provided options for SoCoKit. (text)
    game: An instance of the created game to actually play. (solitaire.Solitaire)
    game_info: The attributes and rule checkers for the designed game. (dict)
    show_names: A flag for showing function names in rule sub-menus. (bool)

    Class Attributes:
    menu: The main menu items and their keys in the game definition. (list)

    Methods:
    add_checker: Get a new rule checker to add to the game. (function)
    build_game: Get the user's definition of the solitaire game. (dict)
    checker_text: Generate the option text for a rule checker function. (str)
    function_choice: Return menu item text for a function. (str)
    get_game_info: Get the inforamation defining the base game. (dict)
    make_game: Make a game object based on the design. (solitaire.Solitaire)
    modify_checkers: Modify a list of rules checkers. (list of function)
    option_text: Create the option text for the game. (None)
    parse_build_options: Get the actual settings of the build options. (dict)
    paser_options: Parse the raw options for later handling. (dict)
    show_game_menu: Show the current status of the game as a menu. (None)

    Static Methods:
    function_choice: Return menu item text for a function. (str)

    Overridden Methods:
    handle_options
    play
    """

    aka = ['SoCoKit', 'SoCK']
    categories = ['Card Games', 'Solitaire Games']
    help_text = {'attributes': ATTRIBUTE_HELP, 'rules': RULE_HELP}
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
                    valid = self.base_game.deck.ranks
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
            raw_choice = self.human.ask('\nWhat would you like to change? ')
            choice = raw_choice.upper()
            if choice not in valid:
                # Allow for non-menu commands.
                self.handle_cmd(raw_choice)
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

    def checker_text(self, rule_checker):
        """
        Generate the option text for a rule checker function. (str)

        Parameters:
        rule_checker: A function for checking rules. (callable)
        """
        if 'option-code' in rule_checker.__doc__:
            # Handle created rule checkers.
            start = rule_checker.__doc__.index('option-code') + 13
            end = rule_checker.__doc__.index('\n', start)
            return rule_checker.__doc__[start:end]
        else:
            # Handle standard rule checkers.
            return rule_checker.__name__

    def function_choice(self, char, func):
        """Return menu item text for a function. (str)"""
        # Get the description.
        description = func.__doc__.split('\n')[1].split('(')[0].strip()
        # Add the name if necessary.
        if self.show_names:
            return '{}: {}\n    {}'.format(char, func.__name__, description)
        else:
            return '{}: {}'.format(char, description)

    def get_game_info(self):
        """
        Get the inforamation defining the base game. (dict)
        """
        # Make a viable instance of the game (to pull in hard coded solitaire options).
        self.base_game = self.base_class(self.human, self.base_options, silent = True)
        self.base_game.scores = {}
        self.base_game.set_up()
        # Get information from the attributes.
        game_info = {'num-cells': self.base_game.num_cells, 'wrap-ranks': self.base_game.wrap_ranks,
            'turn-count': self.base_game.turn_count, 'max-passes': self.base_game.max_passes}
        # Get information from the options, with defaults.
        game_info['deck-specs'] = self.base_game.options.get('deck-specs', [])
        game_info['num-tableau'] = self.base_game.options.get('num-tableau', 7)
        game_info['num-foundations'] = self.base_game.options.get('num-foundations', 4)
        game_info['num-reserve'] = self.base_game.options.get('num-reserve', 0)
        # Get the rule checker lists.
        for check_type in 'build free lane match pair sort'.split():
            key = '{}-checkers'.format(check_type)
            attribute = '{}_checkers'.format(check_type)
            game_info[key] = getattr(self.base_game, attribute)
        game_info['dealers'] = self.base_game.dealers
        # Get the option set for attributes derived from options.
        game_info['option-set'] = self.base_game.option_set
        return game_info

    def handle_options(self):
        """Design the solitaire game. (None)"""
        # Set up this game.
        self.players = [self.human]
        self.player_index = 0
        # Set up this interface.
        option_info = self.parse_options()
        if option_info is None:
            self.option_set.errors.append('Game aborted by the user.')
            return None
        self.show_names = False
        self.base_class = self.interface.games[self.base_name]
        # Extract the game design from the base game.
        game_info = self.get_game_info()
        # Apply the options or quit due to errors.
        game_info.update(option_info)
        # Get a (unique) name for the game.
        if 'name' not in game_info:
            game_info['name'] = self.human.ask('\nWhat is the name of the game you are making? ').strip()
        while game_info['name'].lower() in self.interface.games:
            warning = 'The name {!r} is already in use by another game.'.format(game_info['name'])
            self.human.tell(warning)
            game_info['name'] = self.human.ask('Please choose another name for your game: ').strip()
        # Build the game.
        if 'no-build' not in option_info:
            self.game_info = self.build_game(game_info)
        else:
            self.game_info = game_info
        # Check for exit without playing.
        if self.game_info:
            self.game = self.make_game(self.game_info)
            self.option_text()
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
            categories = ['Card Games', 'Solitaire Games']
            name = game_info['name']
            def handle_options(self):
                # Use the game definition for the options.
                self.options = game_info
                self.option_set = game_info['option-set']
                for option, setting in self.option_set.settings.items():
                    if option != 'bots':
                        setattr(self, option, setting)
            def set_checkers(self):
                # Extract the rule checkers and the dealers.
                for checker_type in 'build free lane match pair sort'.split():
                    attr = '{}_checkers'.format(checker_type)
                    key = '{}-checkers'.format(checker_type)
                    setattr(self, attr, game_info[key])
                self.dealers = game_info['dealers']
        # Return the initialized game.
        return ConstructedGame(self.human, '', self.interface)

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
            if self.show_names:
                self.human.tell('H: Hide Function Names')
            if text == 'Dealers':
                self.human.tell('R: Reorder Rules')
            if not self.show_names:
                self.human.tell('S: Show Function Names')
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
            # Handle hiding or showing function names.
            elif choice == 'H':
                self.show_names = False
            elif choice == 'S':
                self.show_names = True
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

    def option_text(self):
        """Create the option text for the game. (None)"""
        # Get the base game and it's options, if any.
        if self.base_options == 'none':
            option_text = self.base_name
        else:
            option_text = '{} / {}'.format(self.base_name, self.base_game.option_set.settings_text)
        # Get a list of build options by comparing game info dictionaries.
        build_options = []
        base_info = self.get_game_info()
        for key, value in self.game_info.items():
            # Save any differences.
            if key not in base_info or base_info[key] != value:
                # Handle rule checkers.
                if isinstance(value, list):
                    text = '/'.join(self.checker_text(func) for func in value)
                    build_options.append('{}={}'.format(key, text))
                # Handle flag options.
                elif key in ('wrap-ranks', 'no-build'):
                    build_options.append(key)
                # Handle attribute options.
                else:
                    build_options.append('{}={}'.format(key, value))
        # Sort and add any build options found.
        if build_options:
            build_options.sort()
            option_text = '{} | {}'.format(option_text, ' '.join(build_options))
        # Store the options in the created game.
        self.game.option_set.settings_text = option_text

    def parse_build_options(self):
        """Get the actual settings of the build options. (dict)"""
        # Remove unwanted spaces.
        for gap, no_gap in ((' =', '='), ('= ', '='), (' /', '/'), ('/ ', '/')):
            while gap in self.build_options:
                self.build_options = self.build_options.replace(gap, no_gap)
        # Build a dictionary of options.
        option_info = {}
        errors = []
        for option in self.build_options.split():
            # Check for assigned values.
            if '=' in option:
                # Split out the value (but not any parameter assignments for rule checkers)
                key, value = option.split('=', 1)
                # Handle rule checker options.
                if '/' in value and ('checkers' in key or key == 'dealers'):
                    try:
                        value = [eval('solitaire.' + func_name) for func_name in value.split('/')]
                    except AttributeError as err:
                        errors.append(err.args[0])
                # Handle integer values.
                elif value.isdigit() or value == '-1':
                    value = int(value)
                # Handle assigned flags.
                elif value.lower() in ('true', 't', 'false', 'f') and key in ('no-build', 'wrap-ranks'):
                    value = (value[0].lower() == 't')
                # Skip the name options
                elif key in ('name'):
                    pass
                # Handle bad options (!! doesn't check for invalid option names).
                else:
                    errors.append('Invalid value for {!r} key: {!r}.'.format(key, value))
                # Assign the value.
                option_info[key] = value
            # Handle flag options.
            elif option in ('wrap-ranks', 'no-build'):
                option_info[option] = True
            else:
                errors.append('Invalid stand alone option: {!r}.'.format(option))
        # Check for continuation if there are any errors.
        if errors:
            for error in errors:
                self.human.error(error)
            if self.human.ask('\nDo you wish to continue? ') not in utility.YES:
                return None
        return option_info

    def parse_options(self):
        """Parse the raw options for later handling. (dict)"""
        # Split out the base game, options to the base game, and build options.
        slash_index = self.raw_options.find('/')
        pipe_index = self.raw_options.find('|')
        # Only count slashes before the build options.
        slash_index = slash_index if slash_index < pipe_index else -1
        # Game and build options
        if slash_index != -1 and pipe_index != -1:
            self.base_name = self.raw_options[:slash_index].strip()
            self.base_options = self.raw_options[(slash_index + 1):pipe_index].strip()
            self.build_options = self.raw_options[(pipe_index + 1):].strip()
        # Game options only.
        elif slash_index != -1:
            self.base_name = self.raw_options[:slash_index].strip()
            self.base_options = self.raw_options[(slash_index + 1):].strip()
            self.build_options = ''
        # Build options only.
        elif pipe_index != -1:
            self.base_name = self.raw_options[:pipe_index].strip()
            self.base_options = 'none'
            self.build_options = self.raw_options[(pipe_index + 1):].strip()
        # no options
        else:
            if self.raw_options.strip():
                self.base_name = self.raw_options.strip()
            else:
                self.base_name = 'solitaire base'
            self.base_options = 'none'
            self.build_options = ''
        # Confirm the base game.
        while self.base_name.lower() not in self.interface.games:
            self.human.tell('I do not recognize the game {!r}.'.format(self.base_name))
            self.base_name = self.human.ask('\nPlease enter the game to use as a base (return for none): ')
        self.base_name = self.base_name.lower()
        return self.parse_build_options()

    def play(self):
        """Play the game. (list of int)"""
        results = self.game.play()
        # Check for existing short cut.
        shortcut_name = self.game.name.lower().replace(' ', '-')
        if shortcut_name not in self.human.shortcuts:
            # Ask about creating a short cut.
            make_it = self.human.ask('\nWould you like to make a shortcut for {}? '.format(self.game.name))
            if make_it in utility.YES:
                # Create the shortcut if user approves.
                shortcut_value = 'socokit / {} no-build'.format(self.game.option_set.settings_text)
                self.human.store_shortcut(shortcut_name, shortcut_value)
                self.human.tell('The shortcut for this game is {!r}.'.format(shortcut_name))
        return results

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
