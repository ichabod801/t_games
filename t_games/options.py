"""
options.py

Option handling for tgames.

Copyright (C) 2018 by Craig O'Brien and the t_game contributors.
See the top level __init__.py file for details on the t_games license.

Classes:
AllRange: A range that contains everything. (object)
OptionSet: A set of options for a particular game. (object)

Functions:
lower: Convert a string to lower case. (str)
upper: Convert a string to upper case. (str)
"""


import collections
import t_games.utility as utility


class AllRange(object):
    """
    A range that contains everything. (object)

    Overridden Methods:
    __contains__
    __repr__
    """

    def __contains__(self, item):
        """
        Always say the item is in the range. (bool)

        Parameters:
        item: The item to check for existence in the range. (object)
        """
        return True

    def __repr__(self):
        """Generate a computer readable text representation. (str)"""
        return 'AllRange()'


class OptionSet(object):
    """
    A set of options for a particular game. (object)

    Attributes:
    aliases: The aliases for the options. (list of str)
    default_bots: The default bot players. (list of player.Bot)
    definitions: The option definitions for the game. (list of dict)
    errors: Any errors that come up in processing. (list of str)
    game: The game the options are for. (game.Game)
    groups: The option groups. (dict of str: str)
    settings: The option settings provided. (dict of str: object)
    settings_text: The standardized settings text. (str)

    Methods:
    add_group: Add a new option group. (None)
    add_option: Add a new option definition. (None)
    apply_defaults: Apply the default settings. (None)
    apply_definitions: Apply the option definitions to the text settings. (None)
    ask_bool: Ask a boolean question. (list)
    ask_bot_count: Ask a bot question, with count. (list)
    ask_bot_param: Ask a bot question, with parameters. (list)
    ask_parameter: Ask for an option parameter. (list)
    ask_settings: Get the setttings by asking the user. (None)
    handle_settings: Handle text representing some option settings. (None)
    parse_settings: Parse the text settings. (dict of str: str)
    take_action: Take the final action to apply the option setting. (None)

    Overridden Methods:
    __init__
    __repr__
    """

    def __init__(self, game):
        """
        Set up an empty option set. (None)

        Parameters:
        game: The game the option set is for. (game.Game)
        """
        # Set the specified attribute.
        self.game = game
        # Set the default attributes.
        self.aliases = {}
        self.definitions = []
        self.errors = []
        self.groups = {}
        self.settings = {'bots': []}
        self.settings_text = ''
        self.default_bots = []

    def __repr__(self):
        """Generate a debugging text representation. (str)"""
        option_count = len(self.definitions)
        plural = utility.plural(option_count, 'option')
        return '<OptionSet for {} with {} {}>'.format(self.game.name, option_count, plural)

    def add_group(self, name, expansion):
        """
        Add a new option group. (None)

        An option group is an alias for multiple option settings.

        Parameters:
        name: The option setting to convert. (str)
        expansion: What to conver the setting to. (str)
        """
        self.groups[name] = expansion

    def add_option(self, name, aliases = [], converter = str, default = False, value = True, target = '',
        action = 'assign', question = '', valid = AllRange(), check = lambda x: True, error_text = ''):
        """
        Add a new option definition. (None)

        Generally only valid or check is given, althout the option must pass both.
        They are both checkeed after converter is applied. For more details, see
        Programming Games in the wiki.

        Parameters:
        name: The name of the option. (str)
        aliases: Alternate names for the option. (list of str)
        converter: The function to convert the option from a string. (callable)
        default: The default value of the option. (object)
        value: The value to assign if the option is chosen. (object)
        target: Where to store the value in, if different from name. (str)
        action: How to store the value. (str)
        question: How to ask for a setting from the user. (str)
        valid: The allowed settings. (range or container)
        check: A function that validates a setting. (callable)
        error_text: Text to display when there is an invalid setting. (str)
        """
        # Add option aliases to overall aliases
        for alias in aliases:
            self.aliases[alias] = name
        self.aliases[name] = name
        # Check for question types.
        if question.endswith('bool'):
            question_type = 'bool'
            question = question[:-4]
        elif action == 'bot' and value is None:
            question_type = 'bot-param'
        elif action == 'bot':
            question_type = 'bot-count'
        elif not question:
            question_type = 'none'
        else:
            question_type = ''
        # Convert empty parapmeters.
        if target == '':   # instead of 'not target' b/c target could be empty dictionary.
            target = name.replace('-', '_')
        # Create and add the dictionary for the definition.
        definition = {'name': name, 'converter': converter, 'default': default, 'value': value,
            'target': target, 'action': action, 'question': question, 'valid': valid, 'check': check,
            'error_text': error_text, 'question_type': question_type}
        self.definitions.append(definition)

    def apply_defaults(self):
        """Apply the default settings. (None)"""
        for definition in self.definitions:
            if definition['default'] is not None:
                self.take_action(definition, definition['default'])

    def apply_definitions(self, prelim_settings):
        """
        Apply the option definitions to the text settings. (None)

        Parameters:
        prelim_settings: Unconverted option settings. (dict of str: str)
        """
        for definition in self.definitions:
            new_settings = {}
            # If the option was not specified, use the default (if any).
            if not prelim_settings[definition['name']]:
                if definition['default'] is None:
                    continue
                else:
                    self.take_action(definition, definition['default'])
            else:
                # Loop through the settings for the option.
                error = 'Invalid {} parameter: {!r}.'
                valid = definition['valid']
                check = definition['check']
                for setting in prelim_settings[definition['name']]:
                    # Add the value for simple options.
                    if setting is None:
                        self.take_action(definition, definition['value'])
                    # Check for a list of settings.
                    elif '/' in setting or isinstance(definition['default'], (list, tuple)):
                        try:
                            setting = [definition['converter'](item) for item in setting.split('/')]
                        except ValueError:
                            # Give an error message for invalid items in the list.
                            self.errors.append(error.format(definition['name'], setting))
                        else:
                            # Check the list for validity.
                            if not (setting in valid and check(setting)):
                                self.errors.append(error.format(definition['name'], setting))
                            else:
                                self.take_action(definition, setting)
                    # Check for a single item setting.
                    else:
                        try:
                            setting = definition['converter'](setting)
                        except ValueError:
                            # Give an error message for invalid type of setting.
                            self.errors.append(error.format(definition['name'], setting))
                        else:
                            # Check the setting for validity.
                            if not (setting in valid and check(setting)):
                                self.errors.append(error.format(definition['name'], setting))
                            else:
                                self.take_action(definition, setting)
                    # Apply default on error
                    if self.errors and self.errors[-1][8:].startswith(definition['name']):
                        if definition['default'] is not None:
                            self.take_action(definition, definition['default'])

    def ask_bool(self, definition):
        """
        Ask a boolean question. (list)

        The return value is for generating the settings text.

        Parameters:
        definition: The definition of the option to ask about. (dict)
        """
        # Ask the question.
        yes_no = self.game.human.ask(definition['question']) in utility.YES
        # Process the response.
        if yes_no:
            setting = self.take_action(definition, definition['value'])
            return [(definition['name'], None)]
        else:
            setting = self.take_action(definition, definition['default'])
            return []

    def ask_bot_count(self, definition):
        """
        Ask a bot question, with count. (list)

        Parameters:
        definition: The definition of the option to ask about. (dict)
        """
        # Get the count.
        query = 'How many {} bots would you like? '.format(definition['name'])
        bot_num = self.game.human.ask_int(query, valid = range(11), default = 0, cmd = 0)
        # Apply the count.
        setting = definition['value']
        for bot in range(bot_num):
            self.take_action(definition, setting)
        # Return data for settings text.
        return [(definition['name'], None)] * bot_num

    def ask_bot_param(self, definition):
        """
        Ask a bot question, with parameters. (list)

        Parameters:
        definition: The definition of the option to ask about. (dict)
        """
        # Set up the loop.
        pairs = []
        bot_query = 'Would you like to add a {} bot? '.format(definition['name'])
        param_query = 'What parameters should the {} bot have? '.format(definition['name'])
        # Ask if they want to add one until they don't.
        while self.game.human.ask(bot_query) in utility.YES:
            # Ask for parameters until they enter a valid set.
            while True:
                raw_params = self.game.human.ask(param_query)
                if not raw_params:
                    setting = ()
                    break
                try:
                    converter = definition['converter']
                    setting = [converter(param) for param in raw_params.split('/')]
                except ValueError:
                    pass
                else:
                    if setting in definition['valid'] and definition['check'](setting):
                        break
                self.game.human.error('That input is not valid.')
                if definition['error_text']:
                    self.game.human.error(definition['error_text'])
            # Apply the bot and the parameters.
            pairs.append((definition['name'], ''.join(raw_params.split())))
            self.take_action(definition, setting)
        # Return data for settings text.
        return pairs

    def ask_parameter(self, definition):
        """
        Ask for an option parameter. (list)

        Parameters:
        definition: The definition of the option to ask about. (dict)
        """
        pairs = []
        # Get a valid parameter.
        while True:
            raw_setting = self.game.human.ask(definition['question'])
            if not raw_setting:
                setting = definition['default']
                break
            try:
                setting = definition['converter'](raw_setting)
            except ValueError:
                pass
            else:
                if setting in definition['valid'] and definition['check'](setting):
                    break
            self.game.human.error('That input is not valid.')
            if definition['error_text']:
                self.game.human.error(definition['error_text'])
        # Apply the parameter.
        if raw_setting:
            pairs.append((definition['name'], raw_setting))
        self.take_action(definition, setting)
        # Return data for settings text.
        return pairs

    def ask_settings(self):
        """Get the setttings by asking the user. (None)"""
        # Ask if the user if they want to change the options.
        query = '\nWould you like to change the options? '
        if self.definitions and self.game.human.ask(query) in utility.YES:
            # Mark that options have been changed.
            self.game.flags |= 1
            # Ask questions, retaining settings text information.
            pairs = []
            self.game.human.tell()
            for definition in self.definitions:
                # Ask the question based on the question type setting.
                if definition['question_type'] == 'bool':
                    pairs.extend(self.ask_bool(definition))
                elif definition['question_type'] == 'bot-param':
                    pairs.extend(self.ask_bot_param(definition))
                elif definition['question_type'] == 'bot-count':
                    pairs.extend(self.ask_bot_count(definition))
                elif definition['question_type'] == 'none':
                    continue
                else:
                    pairs.extend(self.ask_parameter(definition))
            # Create standardized text.
            pairs.sort()
            text_pairs = [('='.join(pair) if pair[1] is not None else pair[0]) for pair in pairs]
            self.settings_text = ' '.join(text_pairs)
        else:
            # Apply defaults if no options changed.
            self.apply_defaults()

    def handle_settings(self, raw_settings):
        """
        Handle text representing option settings. (None)

        Parameters:
        raw_settings: The option settings provided by the user or interface. (str)
        """
        # Convert the raw text to parsable text.
        settings_text = raw_settings.strip()
        # Apply the settings.
        if settings_text == 'none':
            self.apply_defaults()
        elif settings_text:
            self.game.flags |= 1
            prelim_settings = self.parse_settings(settings_text)
            self.apply_definitions(prelim_settings)
        else:
            self.ask_settings()
        # Check for unspecified bots.
        if not self.settings['bots']:
            self.settings['bots'] = self.default_bots
        # Transfer the settings to the game.
        for option, setting in self.settings.items():
            if option == 'bots':
                # Use bots option to set up the players.
                taken_names = [self.game.human.name]
                bots = []
                for bot_class, params in setting:
                    bots.append(bot_class(*params, taken_names = taken_names))
                    taken_names.append(bots[-1].name)
                self.game.players = [self.game.human] + bots
            else:
                # Set other options normally.
                setattr(self.game, option, setting)
        # Warn of any errors.
        if self.errors:
            self.game.human.tell('\n'.join(self.errors))

    def parse_settings(self, settings_text):
        """
        Parse the text settings. (dict of str: str)

        This sets the standardized setting text and the dictionary of option settings.

        Parameters:
        settings_text: The settings text from the user. (str)
        """
        # Apply the groups.
        settings_text = ' '.join([self.groups.get(word, word) for word in settings_text.split()])
        # Remove unwanted spaces.
        for gap, no_gap in ((' =', '='), ('= ', '='), (' /', '/'), ('/ ', '/'), (' *', '*'), ('* ', '*')):
            while gap in settings_text:
                settings_text = settings_text.replace(gap, no_gap)
        # Repeat any starred options.
        words = []
        for word in settings_text.split():
            if '*' in word:
                try:
                    setting, repeat = word.split('*')
                    repeat = int(repeat)
                    words.extend([setting] * repeat)
                except ValueError:
                    self.errors.append('Invalid repeat value: {!r}.'.format(word))
            else:
                words.append(word)
        # Create option/setting tuples.
        pairs = []
        for word in words:
            if '=' in word:
                try:
                    name, setting = word.split('=')
                    # Apply any known aliases.
                    if name.lower() in self.aliases:
                        pairs.append((self.aliases[name.lower()], setting))
                    else:
                        self.errors.append('Unrecognized option: {}.'.format(name))
                except ValueError:
                    self.errors.append('Syntax error with equals: {!r}.'.format(word))
            elif word.lower() in self.aliases:
                pairs.append((self.aliases[word.lower()], None))
            else:
                self.errors.append('Unrecognized option: {}.'.format(word))
        # Create standardized text.
        pairs.sort()
        text_pairs = [('='.join(pair) if pair[1] is not None else pair[0]) for pair in pairs]
        self.settings_text = ' '.join(text_pairs)
        # Create preliminary settings data.
        prelim_settings = collections.defaultdict(list)
        for option, setting in pairs:
            prelim_settings[option].append(setting)
        return prelim_settings

    def take_action(self, definition, setting):
        """
        Take the final action to apply the option setting. (None)

        Parameters:
        definition: An option definition. (dict of str: object)
        setting: The option setting. (object)
        """
        # Get the action settings for the option.
        action = definition['action']
        target = definition['target']
        if action == 'assign':
            # Assign to the target.
            self.settings[target] = setting
        elif action == 'append':
            # Append to the target.
            if target not in self.settings:
                self.settings[target] = []
            self.settings[target].append(setting)
        elif action.startswith('key='):
            # Assign to the target using a key.
            word, key = action.split('=')
            target[key] = setting
        elif action == 'map':
            # Assing to the target from a dictionary of values.
            self.settings[target] = definition['value'][setting]
        elif action == 'bot':
            # Assing a new bot.
            bot_class = self.game.bot_classes[definition['target']]
            if setting is True:  # That is, there were no parameters given
                self.settings['bots'].append((bot_class, []))
            elif isinstance(setting, (list, tuple)):
                self.settings['bots'].append((bot_class, setting))
            else:
                self.settings['bots'].append((bot_class, [setting]))


def lower(text):
    """
    Convert a string to lower case. (str)

    Parameters:
    text: The string to convert. (str)
    """
    return text.lower()


def upper(text):
    """
    Convert a string to upper case. (str)

    Parameters:
    text: The string to convert. (str)
    """
    return text.upper()


if __name__ == '__main__':
    # Run the unit testing.
    from t_tests.options_test import *
    unittest.main()
