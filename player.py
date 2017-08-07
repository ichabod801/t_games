"""
player.py
"""

class Player(object):

    def __init__(self, name):
        self.name = name

    def ask(self, prompt):
        return input(prompt)

    def tell(self, *args, **kwargs):
        print(*args, **kwargs)