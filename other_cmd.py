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


class OtherCmd(object):
    """
    An object for handing text commands. (object)

    Attributes:
    human: The user of the interface. (player.Player)

    Methods:
    handle_cmd: Check text input for a valid command. (bool)
    """

    aliases = {}

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
        self.human.tell('I do not recognize the command {!r}.'.format(text))
        return True

    def do_debug(self, arguments):
        """
        Handle debugging commands. (bool)

        Parameters:
        arguments: The debugging information needed. (str)
        """
        self.human.tell(eval(arguments))
        return True

    def handle_cmd(self, text):
        """
        Check text input for a valid command. (bool)

        The return value is a flag indicating a valid command. 

        Parameters:
        text: The raw text input by the user. (str)
        """
        command, space, arguments = text.partition(' ')
        command = command.lower()
        command = self.aliases.get(command, command)
        method = 'do_' + command
        if hasattr(self, method):
            return getattr(self, method)(arguments)
        else:
            return self.default(text)


if __name__ == '__main__':
    import tgames.player
    other = OtherCmd(tgames.player.Player('Craig'))
    other.handle_cmd('debug self.aliases')
    other.handle_cmd('! self.human.name')
    print(other.handle_cmd('Python sucks.'))