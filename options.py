"""
options.py

Option handling for tgames.

Classes:
AllRange: A range that contains everything. (object)
OptionSet: A set of options for a particular game. (object)

Functions:
lower: Convert a string to lower case. (str)
upper: Convert a string to upper case. (str)
"""


import collections
import tgames.utility as utility


class AllRange(object):
    """
    A range that contains everything. (object)

    Overridden Methods:
    __contains__
    """

    def __contains__(self, item):
        """
        Check for the item being in the range. (bool)

        Parameters:
        item: The item to check for existence in the range. (object)
        """
        return True


class OptionSet(object):
    """
    A set of options for a particular game. (object)

    Attributes:
    aliases: The aliases for the options. (list of str)
    definitions: The option definitions for the game. (list of dict)
    errors: Any errors that come up in processing. (list of str)
    game: The game the options are for. (game.Game)
    groups: The option groups. (dict of str: str)
    settings: The option settings provided. (collections.defaultdict)
    settings_text: The standardized settings text. (str)

    Methods: 
    add_group: Add a new option group. (None)
    add_option: Add a new option definition. (None)
    apply_definitions: Apply the option definitions to the text settings. (None)
    handle_settings: Handle text representing some option settings. (None)
    parse_settings: Parse the text settings. (dict of str: str)

    Overridden Methods:
    __init__
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
        self.settings = {}
        self.settings_text = ''

    def add_group(self, name, expansion):
        """
        Add a new option group. (None)

        An option group is an aliase for multiple option settings.

        Parameters:
        name: The option setting to convert. (str)
        expansion: What to conver the setting to. (str)
        """
        self.groups[name] = expansion

    def add_option(self, name, aliases = [], converter = str, default = False, value = None, target = '', 
        action = 'assign', question = '', valid = AllRange(), check = lambda x: True, error_text = ''):
        """
        Add a new option definition. (None)

        Parameters:
        name: The name of the option. (str)
        aliases: Alternate names for the option. (list of str)
        converter: The type to convert the option to. (callable)
        default: The default value of the option. (object)
        value: The value to assign if the option is chose. (object)
        target: Where to store the value in, if different from name. (str)
        action: How to store the value. (str)
        question: How to ask for a setting from the user. (str)
        valid: The range of allowed settings. (range or container)
        check: A function that validates a setting. (callable)
        error_text: Text to display when there is an invalid setting. (str)
        """
        # Add option aliases to overall aliases
        for alias in aliases:
            self.aliases[alias] = name
        # Convert empty parapmeters.
        if target == '':   # instead of 'not target' b/c target could be empty dictionary.
            target = name
        if value is None:
            value = True
        # Create and add the dictionary for the definition.
        definition = {'name': name, 'converter': converter, 'default': default, 'value': value, 
            'target': target, 'action': action, 'question': question, 'valid': valid, 'check': check, 
            'error_text': error_text}
        self.definitions.append(definition)

    def apply_definitions(self, prelim_settings):
        """
        Apply the option definitions to the text settings. (None)

        Parameters:
        prelim_settings: Unconverted option settings. (dict of str: str)
        """
        for definition in self.definitions:
            new_settings = {}
            if not prelim_settings[definition['name']]:
                if definition['default'] is None:
                    continue
                else:
                    self.take_action(definition, definition['default'])
            else:
                error = 'Invalid {} parameter: {!r}.'
                valid = definition['valid']
                check = definition['check']
                for setting in prelim_settings[definition['name']]:
                    if setting is None:
                        self.take_action(definition, definition['value'])
                    elif '/' in setting or isinstance(definition['default'], (list, tuple)):
                        try:
                            setting = [definition['converter'](item) for item in setting.split('/')]
                        except ValueError:
                            self.errors.append(error.format(definition['name'], setting))
                        else:
                            if not all(item in valid and check(item) for item in setting):
                                self.errors.append(error.format(definition['name'], setting))
                            else:
                                self.take_action(definition, setting)
                    else:
                        try:
                            setting = definition['converter'](setting)
                        except ValueError:
                            self.errors.append(error.format(definition['name'], setting))
                        else:
                            if not (setting in valid and check(setting)):
                                self.errors.append(error.format(definition['name'], setting))
                            else:
                                self.take_action(definition, setting)

    def ask_settings(self):
        """Get the setttings by asking the user. (None)"""
        if self.game.human.ask('Would you like to change the options? ') in utility.YES:
            self.game.flags |= 1
            pairs = []
            for definition in self.definitions:
                while True:
                    raw_setting = self.game.human.ask(definition['question']).strip()
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
                    self.game.human.tell('That input is not valid.')
                self.take_action(definition, setting)
                if raw_setting:
                    pairs.append((definition['name'], raw_setting))
            # Create standardized text.
            pairs.sort()
            text_pairs = [('='.join(pair) if pair[1] is not None else pair[0]) for pair in pairs]
            self.settings_text = ' '.join(text_pairs)

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
            for definition in self.definitions:
                if definition['default'] is not None:
                    self.take_action(definition, definition['default'])
        elif settings_text:
            self.game.flags |= 1
            prelim_settings = self.parse_settings(settings_text)
            self.apply_definitions(prelim_settings)
        else:
            self.ask_settings()
        # Transfer the settings to the game.
        for option, setting in self.settings.items():
            if option == 'bot':
                self.game.players = [self.game.human] + setting
            else:
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
        for name, expansion in self.groups.items():
            settings_text = settings_text.replace(name, expansion)
        # Remove unwanted spaces.
        for gap, no_gap in ((' =', '='), ('= ', '='), (' /', '/'), ('/ ', '/'), (' *', '*'), ('* ', '*')):
            while gap in settings_text:
                settings_text = settings_text.replace(gap, no_gap)
        # Repeat any stared options.
        words = []
        for word in settings_text.split():
            if '*' in word:
                try:
                    setting, repeat = word.split('*')
                    repeat = int(repeat)
                    words.expand([word] * repeat)
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
                    pairs.append((self.aliases.get(name.lower(), name.lower()), setting))
                except ValueError:
                    self.errors.append('Syntax error with equals: {!r}.'.format(word))
            else:
                pairs.append((word.lower(), None))
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
        action = definition['action']
        target = definition['target']
        if action == 'assign':
            self.settings[target] = setting
        elif action == 'append':
            if target not in self.settings:
                self.settings[target] = []
            self.settings[target].append(setting)
        elif action.startswith('key='):
            word, key = action.split('=')
            target[key] = setting
        elif action == 'map':
            self.settings[target] = definition['value'][setting]
        elif action == 'bot':
            bot_class = self.game.bot_classes[definition['target']]
            if setting is True: # That is, there were no parameters given
                self.settings['bots'].append((bot_class, []))
            elif isinstance(setting, (list, tuple)):
                self.settings['bots'].append((bot_class, setting))
            else:
                self.settings['bots'].append((bot_class, [setting]))


def lower(text):
    """Convert a string to lower case. (str)"""
    return text.lower()

def upper(text):
    """Convert a string to upper case. (str)"""
    return text.upper()

if __name__ == '__main__':
    import tgames.player as player
    class Dummy(object):
        pass
    game = Dummy()
    options = OptionSet(game)
    options.add_option(name = 'yes', default = None)
    options.add_option(name = 'no', value = False, default = True)
    options.add_option(name = 'five', value = 5)
    options.handle_settings('no five')
    print(options.settings_text)
    print(options.errors)
    print(game.__dict__)
    game2 = Dummy()
    options2 = OptionSet(game2)
    options2.add_option(name = 'lower', converter = lower)
    game2.numbers = {}
    options2.add_option(name = 'number', default = 0, action = 'key=five', target = game2.numbers)
    options2.add_option(name = 'yes')
    options2.add_option(name = 'no', value = False, default = True)
    options2.add_group('maybe', 'yes no')
    options2.handle_settings('lower = IMHO five maybe number = 108')
    print()
    print(options2.settings_text)
    print(options2.errors)
    print(game2.__dict__)
    game3 = Dummy()
    options3 = OptionSet(game3)
    options3.add_option(name = 'yes', aliases = ['y', 'da'])
    options3.add_option(name = 'rank', converter = upper, valid = 'XA23456789TJQK')
    options3.add_option(name = 'multi', converter = upper, valid = 'XA23456789TJQK')
    options3.add_option(name = 'many', value = [1, 2, 3], default = [4, 5, 6])
    options3.handle_settings('da rank = 5 multi=j/a/ k many')
    print()
    print(options3.settings_text)
    print(options3.errors)
    print(game3.__dict__)
    numbers = {'one': 1, 'two': 2, 'five': 5}
    game4 = Dummy()
    options4 = OptionSet(game4)
    options4.add_option(name = 'number', action = 'map', value = numbers, default = 'one')
    options4.add_option(name = 'source', value = numbers, default = {})
    options4.add_option(name = 'text', valid = ['one', 'two', 'five'])
    options4.add_option(name = 'key', valid = numbers.keys())
    options4.handle_settings('number = five source text = two key = three')
    print()
    print(options4.settings_text)
    print(options4.errors)
    print(game4.__dict__)
    game5 = Dummy()
    options5 = OptionSet(game5)
    options5.add_option(name = 'low', converter = int, valid = range(1, 19))
    options5.add_option(name = 'high', converter = int, check = lambda x: x > 18)
    options5.add_option(name = 'coordinate', converter = int, default = [0, 1])
    options5.handle_settings('low=8 high=8 coordinate =8')
    print()
    print(options5.settings_text)
    print(options5.errors)
    print(game5.__dict__)
    game6 = Dummy()
    game6.human = player.Tester()
    options6 = OptionSet(game6)
    options6.add_option(name = 'number', default = 0, question = 'Please enter an odd integer < 100: ',
        converter = int, valid = range(0, 100), check = lambda x: x % 2)
    options6.handle_settings('')