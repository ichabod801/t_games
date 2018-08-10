"""
unitility.py

Utility classes and functions for unit testing.

Classes:
ProtoStdIn: A programatically controlled stdin. (object)
ProtoStdOut: A locally stored stdout. (object)
"""


import sys


class ProtoStdIn(object):
    """
    A programatically controlled stdin. (object)

    Attributes:
    lines: The lines of input to give. (list of str)

    Methods:
    readline: Return the next line of input. (list of str)

    Overridden Methods:
    __init__
    """

    def __init__(self, lines = []):
        """Set up the starting input. (None)"""
        self.lines = lines

    def readline(self):
        """Return the next line of input. (str)"""
        return self.lines.pop(0)


class ProtoStdOut(object):
    """
    A locally stored stdout. (object)

    Attributes:
    output: The pieces of output received. (list of str)

    Methods:
    write: Receive the next piece of output. (list of str)

    Overridden Methods:
    __init__
    """

    def __init__(self):
        """Set the instance up to receive output. (None)"""
        self.output = []

    def write(self, text):
        """
        Recieve the next piece of output. (list of str)

        Parameters:
        text: The output received. (str)
        """
        self.output.append(text)
