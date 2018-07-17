"""
other_cmd.py

Basically, a cmd-style command processor without a cmdloop. This is just for
side handling of other commands during another text input handling loop.

Note that the return values for command handling methods are different in
OtherCmd compared to Cmd. To match game.Game processing, True means keep
processing without moving to the next turn.

Copyright (C) 2018 by Craig O'Brien and the t_game contributors.
See the top level __init__.py file for details on the t_games license.

Classes:
OtherCmd: An object for handing text commands. (object)
"""


import textwrap
import traceback


class OtherCmd(object):
    """
    An object for handing text commands. (object)

    Attributes:
    human: The user of the interface. (player.Player)

    Methods:
    handle_cmd: Check text input for a valid command. (bool)
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

    def default(self, text):
        """
        Handle unrecognized commands. (bool)

        The return value is a flag indicating a valid command. 

        Parameters:
        text: The raw text input by the user. (str)
        """
        player = self.players[self.player_index]
        player.error('I do not recognize the command {!r}.'.format(text))
        return True

    def do_debug(self, arguments):
        """
        I can't help you with that.
        """
        try:
            result = eval(arguments)
        except (Exception, AttributeError, ImportError, NameError, TypeError, ValueError):
            self.human.error('\nThere was an exception raised while processing that command:')
            self.human.error(traceback.format_exc(), end = '')
        else:
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
        # Method docstrings are given for recognized commands.
        elif hasattr(self, 'do_' + topic):
            help_text = getattr(self, 'do_' + topic).__doc__
            help_text = textwrap.dedent(help_text).rstrip()
            self.human.tell(help_text)
        # Display default text for unknown arguments.
        else:
            self.human.tell("I can't help you with that.")
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
        command, space, arguments = text.strip().partition(' ')
        command = command.lower()
        command = self.aliases.get(command, command)
        method = 'do_' + command
        if hasattr(self, method):
            return getattr(self, method)(arguments.strip())
        else:
            return self.default(text)


if __name__ == '__main__':
    import tgames.player
    other = OtherCmd(tgames.player.Player('Craig'))
    other.handle_cmd('debug self.aliases')
    other.handle_cmd('! self.human.name')
    print(other.handle_cmd('Python sucks.'))