"""
player.py

Base player classes for tgames.

Copyright (C) 2018-2020 by Craig O'Brien and the t_games contributors.
See the top level __init__.py file for details on the t_games license.

Constants:
BOT_NAMES: Names for computer opponents. (dict of str: str)
NO: Recognized responses equivalent to 'no'. (set of str)
YES: Recognized responses equivalent to 'yes'. (set of str)

Classes:
BotError: An invalid play by a bot. (ValueError)
Player: The base player class. (object)
Humanoid: A player that communicates using input and print. (Player)
Human: A human being, with stored data. (Humanoid)
Tester: A preset test account. (Human)
Nameless: A player with a random name. (Player)
Bot: A full computer player. (Nameless)
AlphaBetaBot: A robot player using alpha-beta pruning. (Bot)
Cyborg: A computer player that is run by a person. (Nameless, Humanoid)
"""


from __future__ import print_function

import os
import random
import re
import string

from . import utility
from . import cards


# Convert 2.7 input to raw_input
try:
    input = raw_input
except NameError:
    pass


BOT_NAMES = {'a': 'Ash/Abby/Adam/Alan/Alice/Ada/Adele/Alonzo/Angus/Astro',
    'b': 'Bender/Barbara/Blue/Bella/Buckaroo/Beth/Bob/Bishop/Betty/Brooke',
    'c': 'Caitlyn/Calvin/Candice/Carl/Carol/Carsen/Cassandra/Cecilia/Chance/Craig',
    'd': 'Data/Deckard/Dahlia/Dana/Daphne/Damon/Debby/David/Darryl/Denise',
    'e': 'Edith/Eve/Ed/Elliot/Elizabeth/Edgar/Enzo/Emelia/Erin/Ernest',
    'f': 'Felicity/Futura/Fatima/Felix/Felipe/Finn/Fiona/Frances/Frank/Fletcher',
    'g': 'Gort/Guido/Geneva/Gia/Gerty/Gilberto/Grace/Gloria/Garry/Grover',
    'h': 'Hymie/Hobbes/Hiro/Homer/Hugo/Haladay/Harriet/Heidi/Hope/Haven',
    'i': 'Ida/Indira/Ines/Inga/Ivy/Ian/Igor/Isaac/Ichabod/Ivan',
    'j': 'Judith/Jade/Jane/Jodie/Julia/John/Jaque/Joshua/Johan/Jerome',
    'k': 'Kitt/Karen/Kay/Kelly/Kyoko/Kareem/Kurt/Kronos/Klaus/Kirk',
    'l': 'Lore/Lee/Lars/Leon/Laszlo/Limor/Laverne/Leelu/Lola/Lois',
    'm': 'Marvin/Mr. Roboto/MechaCraig/Maximillian/Mordecai/Maria/Mary Lou/Marlyn/Monique/Mika',
    'n': 'Nellodee/Nancy/Naomi/Norma/Natalie/Nathan/Ned/Nero/Nick/Nigel',
    'o': 'Otis/Ogden/Omar/Oscar/Otto/Olga/Olivia/Oksana/Octavia/Oriana',
    'p': 'Pris/Patience/Patty/Phoebe/Pru/Patrick/Phillip/Parker/Paul/Pavel',
    'q': 'Queenie/Quenby/Quiana/Quinn/Qadir/Qasim/Quincy/Quang/Quest',
    'r': 'Robby/Roy/Rachel/Risana/Rita/Rosie/River/Reiner/Rick/Rusty',
    's': 'Sam/Shroud/Santiago/Steve/Sonny/Sarina/Susan/Sylvia/Shirley/Sheba',
    't': 'Tabitha/Theresa/Tracy/Trinity/Tamala/Tanner/Tariq/Ted/Tyler/Tyrone',
    'u': 'Ulla/Uma/Ursula/Ursuline/Uta/Ulric/Umberto/Uriah/Usher/Urban',
    'v': 'Vincent/Valerie/Venus/Vivian/Vera/Veronica/Victor/Viggo/Vikram/Vladimir',
    'w': 'Wally/Wednesday/Wana/Wendy/Willow/Winnie/Waylon/Wayne/William/Wolfgang',
    'x': 'Xander/Xavier/Xena/Xhosa/Ximena/Xiang/Xaria/Xanthus/Xenon/Xerxes',
    'y': 'Yamina/Yasmin/Yoland/Yvette/Yadira/Yaakov/Yitzhak/Yves/Yannick/Yaron',
    'z': 'Zahara/Zelda/Zoe/Zuma/Zenaida/Zachary/Zafar/Zane/Zebulon/Zen'}

NO = set(['no', 'n', '0', 'nope', 'negative', 'nah', 'no way', 'i think not', 'nay', 'hell no', 'negatory'])
NO.update(['nyet', 'wu', 'nahin', 'na', 'nao', 'bango', 'nahim', 'nahi', 'la', "a'a", ''])

YES = set(['yes', 'y', '1', 'yup', 'sure', 'affirmative', 'yeah', 'indubitably', 'yep', 'aye', 'ok', 'nem'])
YES.update(['okay', 'eh', 'roger', 'da', 'si', 'shi', 'haan', 'hyam', 'sim', 'hai', 'ham', 'hoya'])


class BotError(ValueError):
    """An invalid play by a bot. (ValueError)"""
    pass


class Player(object):
    """
    The base player class. (object)

    Attributes:
    game: The game the player is playing. (game.Game)
    held_inputs: Inputs awaiting a question. (list of str)
    name: The name of the player. (str)
    shortcuts: Short versions of commands. (dict of str: str)

    Methods:
    ask: Get information from the player. (str)
    ask_card: Get a card from the player. (cards.Card)
    ask_card_list: Get a multiple card response from the player. (int)
    ask_int: Get an integer response from the player. (int)
    ask_int_list: Get a multiple integer response from the player. (int)
    ask_valid: Get and validate responses from the user. (str)
    ask_yes_no: Get a yes or no answer from the user. (str)
    clean_up: Do any necessary post-game processing. (None)
    error: Warn the player about an invalid play. (None)
    set_up: Do any necessary pre-game processing. (None)
    store_results: Store a game result. (None)
    tell: Give information to the player. (None)

    Overridden Methods:
    __init__
    __repr__
    __str__
    """

    def __init__(self, name):
        """
        Save the player's name. (None)

        Parameters:
        name: The name of the player. (str)
        """
        # Save the name.
        self.name = name
        # Set the default attributes.
        self.game = None
        self.held_inputs = []
        self.shortcuts = {}

    def __eq__(self, other):
        """
        Equality testing by name. (bool)

        Parameters:
        other: The object to check equality with. (object)
        """
        if isinstance(other, Player):
            return self.name == other.name
        elif isinstance(other, str):
            return self.name == other
        else:
            return NotImplemented

    def __hash__(self):
        """Return a hash of the player's name. (int)"""
        return hash(self.name)

    def __lt__(self, other):
        """
        Less-than testing by name. (bool)

        Parameters:
        other: The object to check equality with. (object)
        """
        if isinstance(other, Player):
            return self.name < other.name
        elif isinstance(other, str):
            return self.name < other
        else:
            return NotImplemented

    def __repr__(self):
        """Generate a debugging text representation. (str)"""
        return '<{} {}>'.format(self.__class__.__name__, self.name)

    def __str__(self):
        """Generate a human readable representation. (str)"""
        return self.name

    def ask(self, prompt):
        """
        Get information from the player. (str)

        Parameters:
        prompt: The question being asked of the player. (str)
        """
        raise BotError('Unexpected question asked of {}: {!r}'.format(self.__class__.__name__, prompt))

    def ask_card(self, prompt, valid = [], default = None, cmd = True):
        """
        Get a card from the player. (cards.Card)

        Parameters:
        prompt: The question asking for the card. (str)
        valid: The valid values for the card. (container of int)
        default: The default choice. (cards.Card or None)
        cmd: A flag for returning commands for processing. (bool)
        """
        raise BotError('Unexpected question asked of {}: {!r}'.format(self.__class__.__name__, prompt))

    def ask_card_list(self, prompt, valid = [], valid_lens = [], default = None, cmd = True):
        """
        Get a multiple card response from the player. (int)

        Parameters:
        prompt: The question asking for the card. (str)
        valid: The valid values for the cards. (list of int)
        valid_lens: The valid numbers of values. (list of int)
        default: The default choice. (list or None)
        cmd: A flag for returning commands for processing. (bool)
        """
        raise BotError('Unexpected question asked of {}: {!r}'.format(self.__class__.__name__, prompt))

    def ask_int(self, prompt, low = None, high = None, valid = [], default = None, cmd = True):
        """
        Get an integer response from the player. (int)

        Parameters:
        prompt: The question asking for the integer. (str)
        low: The lowest acceptable value for the integer. (int or None)
        high: The highest acceptable value for the integer. (int or None)
        valid: The valid values for the integer. (container of int)
        default: The default choice. (int or None)
        cmd: A flag for returning commands for processing. (bool)
        """
        raise BotError('Unexpected question asked of {}: {!r}'.format(self.__class__.__name__, prompt))

    def ask_int_list(self, prompt, low = None, high = None, valid = [], valid_lens = [], default = None,
        cmd = True):
        """
        Get a multiple integer response from the human. (int)

        Parameters:
        prompt: The question asking for the interger. (str)
        low: The lowest acceptable value for the integer. (list or None)
        high: The highest acceptable value for the integer. (laist or None)
        valid: The valid values for the integer. (list of int)
        valid_lens: The valid numbers of values. (list of int)
        default: The default choice. (list or None)
        cmd: A flag for returning commands for processing. (bool)
        """
        raise BotError('Unexpected question asked of {}: {!r}'.format(self.__class__.__name__, prompt))

    def ask_valid(self, prompt, valid, default = '', lower = True):
        """
        Get and validate responses from the user. (str)

        Note that default must be in valid.

        Parameters:
        prompt: The question to ask the user. (str)
        valid: The valid responses from the user. (container of str)
        default: The default value for the response. (str)
        lower: A flag for case insensitive matching. (bool)
        """
        raise BotError('Unexpected question asked of {}: {!r}'.format(self.__class__.__name__, prompt))

    def ask_yes_no(self, prompt, yes = (), no = (), other = (), cmd = False):
        """
        Get a yes or no answer from the user. (str)

        Parameters:
        prompt: The question to ask the user. (str)
        yes: Extra answers accepted as yes. (tuple of str)
        no: Extra answers accepted as no. (tuple of str)
        other: Other answers to be returned as strings. (tuple of str)
        cmd: A flag for returning commands for processing. (bool)
        """
        raise BotError('Unexpected question asked of {}: {!r}'.format(self.__class__.__name__, prompt))

    def clean_up(self):
        """Do any necessary post-game processing. (None)"""
        pass

    def error(self, *args, **kwargs):
        """
        Warn the player about an invalid play. (None)

        Parameters:
        The parameters are as the built-in print function.
        """
        print(*args, **kwargs)

    def set_up(self):
        """Do any necessary pre-game processing. (None)"""
        pass

    def store_results(self, game_name, result):
        """
        Store game results. (None)

        Parameters:
        game_name: The name of the game the result is from. (str)
        results: The results of playing the game. (list of int)
        """
        pass

    def tell(self, *args, **kwargs):
        """
        Give information to the player. (None)

        Parameters:
        The parameters are as per the built-in print function.
        """
        print(*args, **kwargs)


class Humanoid(Player):
    """
    A player that communicates using input and print. (Player)

    Class Attributes:
    list_re: A regex for splitting lists in user input. (re. SRE_Expression)

    Overridden Methods:
    ask
    ask_card
    ask_card_list
    ask_int
    ask_int_list
    ask_valid
    ask_yes_no
    """

    list_re = re.compile('[,\-/\s]+')

    def ask(self, prompt):
        """
        Get information from the player. (str)

        Parameters:
        prompt: The question being asked of the player. (str)
        """
        # Check for held inputs.
        if not self.held_inputs:
            # Get new inputs.
            answer = input(prompt).strip()
            # Check for new held inputs.
            if ';' in answer:
                self.held_inputs = [part.strip() for part in answer.split(';')]
        if self.held_inputs:
            # Pull from the held inputs.
            answer = self.held_inputs.pop(0)
        # Process shortcuts.
        first, space, rest = answer.partition(' ')
        first = self.shortcuts.get(first.lower(), first)
        # Return the processed inputs.
        return '{} {}'.format(first, rest).strip()

    def ask_card(self, prompt, valid = [], default = None, cmd = True):
        """
        Get a card from the player. (cards.Card)

        Parameters:
        prompt: The question asking for the card. (str)
        valid: The valid values for the card. (container of cards.Card)
        default: The default choice. (cards.Card or None)
        cmd: A flag for returning commands for processing. (bool)
        """
        # Give a dummy answer if the game is over.
        if cmd and self.game.force_end:
            return valid[0] if valid else cards.Card('X', 'S')
        # Get the deck to base the search on.
        if isinstance(valid, cards.Hand):
            deck = valid.deck
        elif hasattr(self.game, 'deck'):
            deck = self.game.deck
        else:
            deck = None
        # Ask until you get a valid answer.
        while True:
            card_text = self.ask(prompt).strip()
            # Check for default.
            if not card_text and default is not None:
                return default
            # Convert to a cards.
            card = cards.parse_text(card_text, deck)
            if isinstance(card, cards.Card):
                if valid and card not in valid:
                    self.error('Please enter one of {}.'.format(utility.oxford(valid, 'or', '{:u}')))
                else:
                    return card
            elif card:
                self.error('One card only please.')
            elif cmd:
                return card_text
            else:
                self.error('Please enter a valid card.')

    def ask_card_list(self, prompt, valid = [], valid_lens = [], default = None, cmd = True):
        """
        Get a multiple card response from the human. (int)

        Parameters:
        prompt: The question asking for the card. (str)
        valid: The valid values for the cards. (list of int)
        valid_lens: The valid numbers of values. (list of int)
        default: The default choice. (list or None)
        cmd: A flag for returning commands for processing. (bool)
        """
        # Give a dummy answer if the game is over.
        if cmd and self.game.force_end:
            return valid[0] if valid else cards.Card('X', 'S')
        # Get the deck to base the search on.
        if isinstance(valid, cards.Hand):
            deck = valid.deck
        elif hasattr(self.game, 'deck'):
            deck = self.game.deck
        else:
            deck = None
        # Ask until you get a valid answer.
        while True:
            card_text = self.ask(prompt).strip()
            # Check for default.
            if not card_text and default is not None:
                return default
            # Convert to a cards.
            cards_in = cards.parse_text(card_text, deck)
            if isinstance(cards_in, cards.Card):
                cards_in = [cards_in]
            if isinstance(cards_in, list):
                if valid_lens and len(cards_in) not in valid_lens:
                    self.error('Please enter {} cards.'.format(utility.oxford(valid_lens)))
                elif [card for card in cards_in if card not in valid]:
                    self.error('Not all of those cards are available.')
                else:
                    return cards_in
            elif isinstance(cards_in, str) and cmd:
                return card_text

    def ask_int(self, prompt, low = None, high = None, valid = [], default = None, cmd = True):
        """
        Get an integer response from the human. (int)

        Parameters:
        prompt: The question asking for the interger. (str)
        low: The lowest acceptable value for the integer. (int or None)
        high: The highest acceptable value for the integer. (int or None)
        valid: The valid values for the integer. (container of int)
        default: The default choice. (int or None)
        cmd: A flag for returning commands for processing. (bool)
        """
        # Give a dummy answer if the game is over.
        if cmd and self.game.force_end:
            return [x for x in valid + [low, high, default, 0] if x is not None][0]
        # Ask until you get a valid answer.
        while True:
            response = self.ask(prompt).strip()
            # Check for default.
            if not response and default is not None:
                return default
            # Convert to integer
            try:
                response = int(response)
            except ValueError:
                # Handle non-integers based on cmd parameter.
                if cmd:
                    break
                else:
                    self.error('Integers only please.')
            else:
                # Check for valid input
                if low is not None and response < low:
                    self.error('That number is too low. The lowest valid response is {}.'.format(low))
                elif high is not None and response > high:
                    self.error('That number is too high. The highest valid response is {}.'.format(high))
                elif valid and response not in valid:
                    self.error('{} is not a valid choice.'.format(response))
                    self.error('You must choose one of {}.'.format(utility.oxford(valid, 'or')))
                else:
                    break
        return response

    def ask_int_list(self, prompt, low = None, high = None, valid = [], valid_lens = [], default = None,
        cmd = True):
        """
        Get a multiple integer response from the human. (int)

        Parameters:
        prompt: The question asking for the interger. (str)
        low: The lowest acceptable value for the integer. (list or None)
        high: The highest acceptable value for the integer. (laist or None)
        valid: The valid values for the integer. (list of int)
        valid_lens: The valid numbers of values. (list of int)
        default: The default choice. (list or None)
        cmd: A flag for returning commands for processing. (bool)
        """
        # Give a dummy answer if the game is over.
        if cmd and self.game.force_end:
            return [x for x in valid + [[low], [high], [0]] if x != [None]][0]
        # Ask until you get a valid answer.
        while True:
            response = self.ask(prompt).strip()
            # Check for default
            if not response and default is not None:
                return default
            # Check for empty list as valid response.
            elif not response and not cmd and (0 in valid_lens or not valid_lens):
                return []
            # Check for valid response.
            try:
                # Extract integers.
                response = [int(num) for num in self.list_re.split(response)]
            except ValueError:
                # Handle non-integer input based on cmd parameter.
                if cmd:
                    return response
                else:
                    self.error('Please enter the requested integers.')
                    continue
            # Check low.
            if low is not None and min(response) < low:
                self.error('{} is too low. The lowest valid response is {}.'.format(min(response), low))
            # Check high.
            elif high is not None and max(response) > high:
                highest = max(response)
                self.error('{} is too high. The highest valid response is {}.'.format(highest, high))
            # Check valid values.
            elif valid:
                for number in set(response):
                    if response.count(number) > valid.count(number):
                        self.error("You have more {}'s than allowed.".format(number))
                        self.error("You must choose from: {}.".format(utility.oxford(valid)))
                        break
                else:
                    break
            # Check valid lengths.
            elif valid_lens and len(response) not in valid_lens:
                self.error('That is an invalid number of integers.')
                if len(valid_lens) == 1:
                    plural = utility.number_plural(valid_lens[0], 'integer')
                    self.error('Please enter {}.'.format(plural))
                else:
                    self.error('Please enter {} integers.'.format(utility.oxford(valid_lens, 'or')))
            # Exit on valid input.
            else:
                break
        return response

    def ask_yes_no(self, prompt, yes = (), no = (), other = (), cmd = False):
        """
        Get a yes or no answer from the user. (str)

        Note that the yes, no, and other parameters are compared to the lower
        case version of the input.

        Parameters:
        prompt: The question to ask the user. (str)
        yes: Extra answers accepted as yes. (tuple of str)
        no: Extra answers accepted as no. (tuple of str)
        other: Other answers to be returned as strings. (tuple of str)
        cmd: A flag for returning commands for processing. (bool)
        """
        if cmd and self.game.force_end:
            return False
        while True:
            raw = input(prompt).strip()
            yes_no = raw.lower()
            if yes_no in YES or yes_no in yes:
                return True
            elif yes_no in NO or yes_no in no:
                return False
            elif cmd or yes_no in other:
                return raw
            else:
                valid = ['yes', 'no']
                valid.extend(other)
                self.error("Please enter {}.".format(utility.oxford(valid, 'or', "'{}'")))


class Human(Humanoid):
    """
    A human being, with stored data. (Player)

    Attributes:
    color: The player's favorite color. (str)
    folder_name: The local file with the player's data. (str)
    quest: The player's quest. (str)
    results: The results of games played. (list of list)
    session_index: The number of games played before this session. (int)

    Methods:
    load_results: Load the player's history of play. (None)
    load_shortcuts: Load the player's interface shortcuts. (None)
    store_results: Store game results. (None)
    store_shortcut: Store new shortcuts. (None)

    Overridden Methods:
    __init__
    """

    def __init__(self):
        """Get a login from a human. (None)"""
        while True:
            # Get the user's name.
            self.name = input('What is your name? ')
            # Allow for single or multiple entry of quest and color.
            if ';' in self.name:
                self.name, self.quest, self.color = [word.strip() for word in self.name.split(';')]
            else:
                self.quest = input('What is your quest? ')
                self.color = input('What is your favorite color? ')
            # Check for previous log in.
            base_name = '{}-{}-{}'.format(self.name, self.quest, self.color).lower()
            self.folder_name = os.path.join(utility.LOC, base_name)
            if not os.path.exists(self.folder_name):
                # Check for adding new players.
                new_player = input('I have not heard of you. Are you a new player? ')
                if new_player.lower() in utility.YES:
                    os.mkdir(self.folder_name)
                    with open(os.path.join(self.folder_name, 'results.txt'), 'w') as player_data:
                        player_data.write('')
                    with open(os.path.join(self.folder_name, 'shortcuts.txt'), 'w') as player_data:
                        player_data.write('')
                    break
                print()
            else:
                break
        # Load player information.
        self.load_results()
        self.load_shortcuts()
        # Set default attributes.
        self.held_inputs = []

    def load_results(self):
        """Load the player's history of play. (None)"""
        self.results = []
        with open(os.path.join(self.folder_name, 'results.txt')) as player_data:
            for line in player_data:
                results = line.strip().split(',', 7)
                self.results.append(results[:1] + [int(x) for x in results[1:-1]] + results[-1:])
        self.session_index = len(self.results)
        self.fire_index = self.session_index

    def load_shortcuts(self):
        """Load the player's interface shortcuts. (None)"""
        # Load the shortcuts.
        self.shortcuts = {}
        with open(os.path.join(self.folder_name, 'shortcuts.txt')) as player_data:
            for line in player_data:
                shortcut, text = line.strip().split('\t')
                self.shortcuts[shortcut] = text
                # Make sure the file is ready for appending new shortcuts.
                if not line.endswith('\n'):
                    with open(os.path.join(self.folder_name, 'shortcuts.txt'), 'a') as player_data:
                        player_data.write('\n')

    def store_results(self, game_name, results):
        """
        Store game results. (None)

        Parameters:
        game_name: The name of the game the result is from. (str)
        results: The results of playing the game. (list of int)
        """
        # Store locally.
        self.results.append([game_name] + results)
        # Store in the player's file.
        results_text = ','.join([str(x) for x in results])
        with open(os.path.join(self.folder_name, 'results.txt'), 'a') as player_data:
            player_data.write('{},{}\n'.format(game_name, results_text))

    def store_shortcut(self, shortcut, text):
        """
        Store new shortcuts. (None)

        Parameters:
        shortcut: The word that is the short cut. (str)
        text: The text the shortcut expands into. (str)
        """
        # Store locally
        shortcut = shortcut.lower()
        self.shortcuts[shortcut] = text
        # Store in the player's file.
        with open(os.path.join(self.folder_name, 'shortcuts.txt'), 'a') as player_data:
            player_data.write('{}\t{}\n'.format(shortcut, text))


class Tester(Human):
    """
    A preset test account. (Human)

    Overridden Methods:
    __init__
    """

    def __init__(self, name = 'Buckaroo', quest = 'testing', color = 'black'):
        """Auto setup a Human. (None)"""
        # Store the answers to the three questions.
        self.name = name
        self.quest = quest
        self.color = color
        # Set up the folder for the tester.
        base_name = '{}-{}-{}'.format(self.name, self.quest, self.color).lower()
        self.folder_name = os.path.join(utility.LOC, base_name)
        if not os.path.exists(self.folder_name):
            os.mkdir(self.folder_name)
            with open(os.path.join(self.folder_name, 'results.txt'), 'w') as player_data:
                player_data.write('')
            with open(os.path.join(self.folder_name, 'shortcuts.txt'), 'w') as player_data:
                player_data.write('')
        # Load any previous testing data.
        self.load_results()
        self.load_shortcuts()
        # Set default attributes.
        self.held_inputs = []


class Nameless(Player):
    """
    A player with a random name. (Player)

    Overridden Methods:
    __init__
    """

    def __init__(self, taken_names = [], initial = ''):
        """
        Set the bot's name. (None)

        If initial is empty, the bot's name can start with any letter.

        Parameters:
        taken_names: Names already used by a player. (list of str)
        initial: The first letter of the bot's name. (str)
        """
        # Get a random name that hasn't been used yet.
        while True:
            if initial:
                self.name = random.choice(BOT_NAMES[initial.lower()].split('/'))
            else:
                self.name = random.choice(BOT_NAMES[random.choice(string.ascii_lowercase)].split('/'))
            if self.name not in taken_names:
                break
        # Set default attributes.
        self.held_inputs = []
        self.shortcuts = {}


class Bot(Nameless):
    """
    A full computer player. (Player)

    Overridden Methods:
    error
    tell
    """

    def error(self, *args, **kwargs):
        """
        Stop play due to a bot malfunction. (None)

        Parameters:
        The parameters are the same as the built-in bot function.
        """
        # Get the base text.
        kwargs['sep'] = kwargs.get('sep', ' ')
        kwargs['end'] = kwargs.get('end', '\n')
        text = kwargs['sep'].join([str(arg) for arg in args]) + kwargs['end']
        # Raise an error.
        raise BotError(text.strip())

    def tell(self, *args, **kwargs):
        """
        Give information to the player. (None)

        Parameters:
        The parameters are as per the built-in print function.
        """
        # Get the base text.
        kwargs['sep'] = kwargs.get('sep', ' ')
        kwargs['end'] = kwargs.get('end', '\n')
        text = kwargs['sep'].join([str(arg) for arg in args])
        # Reframe as third person.
        possessive = self.name + "'s"
        pairs = (('Your', possessive), ('your', possessive), ('You', self.name), ('you', self.name),
            ('have', 'has'))
        for pronoun, name in pairs:
            text = text.replace(pronoun, name)
        # Print the modified text.
        print(text, end = kwargs['end'])


class AlphaBetaBot(Bot):
    """
    A robot player using alpha-beta pruning. (Bot)

    The AlphaBetaBot assumes you have a board game, and the board has a get_moves
    method which returns all legal moves, a copy method which returns an
    indepent copy of the board, and a check_win method that returns 'game on'
    until the game is over.

    Attributes:
    depth: The depth of the search. (int)
    fudge: A fudge factor to avoid early capitulation. (int or float)

    Methods:
    alpha_beta: Tree search with alpha-beta pruning. (tuple)
    eval_board: Evaluate the board. (int)

    Overridden Methods:
    __init__
    """

    def __init__(self, depth, fudge, taken_names = [], initial = ''):
        """
        Set up the bot. (None)

        Parameters:
        depth: The depth of the search. (int)
        fudge: A fudge factor to avoid early capitulation. (int or float)
        taken_names: Names already used by a player. (list of str)
        initial: The first letter of the bot's name. (str)
        """
        # Do the standard initialization.
        super(AlphaBetaBot, self).__init__(taken_names, initial)
        # Initialize the alpha-beta attributes.
        self.depth = depth
        self.fudge = fudge

    def alpha_beta(self, board, depth, alpha, beta, max_player):
        """
        Tree search with alpha-beta pruning. (tuple)

        The return value is a tuple of the best move found and the estimated board
        value for that move.

        Parameters:
        board: The board position at this point in the tree. (ConnectFourBoard)
        depth: How many more iterations of the search there should be. (int)
        alpha: The best score for the maximizing player. (int)
        beta: The best score for the minimizing player. (int)
        max_player: Flag for evaluating the maximizing player. (int)
        """
        # Initialize loops
        best_move = None
        # check for terminal node
        if depth == 0 or board.check_win() != 'game on':
            value = self.eval_board(board)
            fudge = self.fudge * (self.depth - depth)
            # ?? this is meant to prevent giving up in a forced win situation. Not sure it works.
            value -= fudge
            return None, value
        elif max_player:
            # maximize loop
            board_value = -utility.MAX_INT
            for move in board.get_moves():
                # evaluate the move
                clone = board.copy()
                clone.make_move(move)
                sub_move, move_value = self.alpha_beta(clone, depth - 1, alpha, beta, False)
                # check for better move
                if move_value > board_value:
                    board_value = move_value
                    best_move = move
                # adjust and check alpha
                alpha = max(alpha, board_value)
                if beta <= alpha:
                    break
        else:
            # minimize loop
            board_value = utility.MAX_INT
            for move in board.get_moves():
                # evaluate the move
                clone = board.copy()
                clone.make_move(move)
                sub_move, move_value = self.alpha_beta(clone, depth - 1, alpha, beta, True)
                # check for worse move
                if move_value < board_value:
                    board_value = move_value
                    best_move = move
                # adjust and check beta
                beta = min(beta, board_value)
                if beta <= alpha:
                    break
        # return best move found with board value
        return best_move, board_value

    def eval_board(self, board):
        """
        Evaluate the board. (int)

        Parameters:
        board: The board to evaluate. (board.Board)
        """
        return NotImplemented


class Cyborg(Nameless, Humanoid):
    """A computer player that is run by a person. (Nameless, Humanoid)"""
    pass


if __name__ == '__main__':
    # Run the unit testing.
    from t_tests.player_test import *
    unittest.main()
