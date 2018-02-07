"""
other_cmd.py

Basically, a cmd-style command processor without a cmdloop. This is just for
side handling of other commands during another text input handling loop.

Note that the return values for command handling methods are different in
OtherCmd compared to Cmd. To match game.Game processing, True means keep
processing without moving to the next turn.

Classes:
OtherCmd: An object for handing text commands. (object)
"""


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
        self.human.error('I do not recognize the command {!r}.'.format(text))
        return True

    def do_debug(self, arguments):
        """
        Handle debugging commands. (bool)

        Parameters:
        arguments: The debugging information needed. (str)
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

    def do_set(self, arguments):
        """
        Set a shortcut. (None)

        Parameters:
        arguments: The shortcut to set. (str)
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