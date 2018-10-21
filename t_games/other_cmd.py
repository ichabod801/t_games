"""
other_cmd.py

Basically, a cmd-style command processor without a cmdloop. This is just for
side handling of other commands during another text input handling loop.

Note that the return values for command handling methods are different in
OtherCmd compared to Cmd. To match game.Game processing, True means keep
processing without moving to the next turn.

Copyright (C) 2018 by Craig O'Brien and the t_games contributors.
See the top level __init__.py file for details on the t_games license.

Classes:
OtherCmd: An object for handing text commands. (object)
"""


import textwrap
import traceback


class OtherCmd(object):
    """
    An object for handing text commands. (object)

    Class Attributes:
    aliases: Other names for commands. (dict of str: str)
    help_text: Text for other help topics. (dict of str: str)

    Attributes:
    human: The user of the interface. (player.Player)

    Methods:
    default: Handle unrecognized commands. (bool)
    do_debug: Evaluate Python code. (bool)
    do_help: Process help requests. (bool)
    do_set: Set shortcuts. (bool)
    handle_cmd: Check text input for a valid command. (bool)

    Overridden Methods:
    __init__
    __repr__
    """

    aliases = {'&': 'debug'}
    help_text = {'help': '\nResistance is futile.'}

    def __init__(self, human):
        """
        Set up the user. (None)

        Parameters:
        human: The (ostensibly) human user of the interface. (player.Player)
        """
        self.human = human

    def __repr__(self):
        """Generate a debugging text representation. (str)"""
        return '<{} for {!r}>'.format(self.__class__.__name__, self.human)

    def default(self, text):
        """
        Handle unrecognized commands. (bool)

        Parameters:
        text: The raw text input by the user. (str)
        """
        self.human.error('\nI do not recognize the command {!r}.'.format(text))

    def do_debug(self, arguments):
        """
        I can't help you with that.
        """
        try:
            # Run the code.
            result = eval(arguments)
        except (Exception, AttributeError, ImportError, NameError, TypeError, ValueError):
            # Catch most exceptions and inform the user.
            self.human.error('\nThere was an exception raised while processing that command:')
            self.human.error(traceback.format_exc(), end = '')
        else:
            # Show the results of valid code.
            self.human.tell(repr(result))
            self.human.tell()
        return True

    def do_help(self, arguments):
        """
        Handle help requests. (bool)

        Parameters:
        arguments: What to provide help for. (str)
        """
        topic = arguments.lower()
        # check for aliases
        topic = self.aliases.get(topic, topic)
        # The help_text dictionary takes priority.
        if topic in self.help_text:
            self.human.tell(self.help_text[topic].rstrip())
        # General help is given with no arguments.
        elif not topic:
            # Show the base help text.
            self.human.tell(self.help_text['help'].rstrip())
            # Get the names of other help topics.
            names = [name[3:] for name in dir(self.__class__) if name.startswith('do_')]
            names.extend([name[5:] for name in dir(self.__class__) if name.startswith('help_')])
            names.extend(self.help_text.keys())
            # Clean up the names.
            names = list(set(names) - set(('debug', 'gipf', 'help', 'text', 'xyzzy')))
            names.sort()
            # Convert the names to cleanly wrapped text and output.
            name_lines = textwrap.wrap(', '.join(names), width = 79)
            if name_lines:
                self.human.tell()
                self.human.tell("Additional help topics available with 'help <topic>':")
                self.human.tell('\n'.join(name_lines))
        # help_foo methods take priority over do_foo docstrings.
        elif hasattr(self, 'help_' + topic):
            help_method = getattr(self, 'help_' + topic)
            # Exit without pausing if requested by the help_foo method.
            if help_method():
                return True
        # Method docstrings are given for recognized commands.
        elif hasattr(self, 'do_' + topic):
            help_text = getattr(self, 'do_' + topic).__doc__
            help_text = textwrap.dedent(help_text).rstrip()
            self.human.tell(help_text)
        # Display default text for unknown arguments.
        else:
            self.human.tell("\nI can't help you with that.")
        # Don't let the next menu interfere with reading the help text.
        self.human.ask('\nPress Enter to continue: ')
        return True

    def do_set(self, arguments):
        """
        Set a shortcut.

        The first word provided as an argument to the set command will be the
        shortcut. The rest of text of the argument will be what the shortcut is
        expanded into. Any time that shortcut is used as a command, it is replaced
        with the expanded text.

        For example, if you prefer playing freecell with three cells, you could type
        'set fc play freecell / cells = 3'. Then any time you typed 'fc', it would
        play the game freecell with the option 'cells = 3'. You could even type 'fc
        challenge' to play with three cells and the challenge option.
        """
        shortcut, space, text = arguments.strip().partition(' ')
        self.human.store_shortcut(shortcut, text)

    def handle_cmd(self, text):
        """
        Check text input for a valid command. (bool)

        The return value is a flag indicating a valid command.

        Parameters:
        text: The raw text input by the user. (str)
        """
        # Parse the input into a command and arguments.
        command, space, arguments = text.strip().partition(' ')
        command = command.lower()
        command = self.aliases.get(command, command)
        # Check for a method to handle the command.
        method = 'do_' + command
        if hasattr(self, method):
            return getattr(self, method)(arguments.strip())
        else:
            # Use default if there is no available method.
            return self.default(text)


if __name__ == '__main__':
    # Run the unit testing.
    from t_tests.other_cmd_test import *
    unittest.main()
