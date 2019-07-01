"""
dollar_game.py

The Dollar Game, as specified in this Numberphile video:
https://www.youtube.com/watch?v=U33dsEcKgeQ&t=3s
"""


import random
import string

from .. import game


CREDITS = """
Game Design: Matt Baker
Game Programming: Craig O'Brien, David B. Wilson
"""

RULES = """
The game is made up of a bunch of nodes, each of which is a neighbor to one or
more of the other nodes. Each node has a dollar value to it, which may be
negative. Nodes with a negative dollar value are considered to be in debt.

Two moves are available in the game. You can have a node donate one dollar to
each of it's neighbors, or you can have a node take a dollar from each of its
neighbors. The aliases for the donate move are d and -, the aliases for the
take move are t and +.

The game is won when all nodes are out of debt (that is, all nodes have a
value of zero or more).

Options:
genus= (g=): The genus of the graph (#edges - #nodes + 1).
nodes= (n=): The number of nodes in the graph. Defaults to 5-10 at random.
ease= (e=): How easy the graph is to solve. (1-5, defaults to 2)
"""


class DollarGame(game.Game):
    """
    A game of the Dollar Game. (game.Game)

    Methods:
    do_donate: Donate one dollar from a node to each of it's neighbors. (bool)
    do_take: Take one dollar from each of a node's neighbors. (bool)

    Overridden Methods:
    handle_options
    player_action
    set_options
    set_up
    """

    aka = ['Dollar Game', 'Dollar', 'DoGa']
    aliases = {'-': 'donate', '+': 'take', 'd': 'donate', 't': 'take'}
    categories = ['Other Games', 'Theoretical Games']
    credits = CREDITS
    name = 'The Dollar Game'
    rules = RULES

    def do_donate(self, arguments):
        """
        Donate one dollar from a node to each of it's neighbors.

        Aliases: d, -
        """
        if self.auot_cap:
            arguments = arguments.upper()
        try:
            self.graph.donate(arguments)
            return True
        except KeyError:
            self.human.error('{} is not a node in the graph.'.format(arguments))

    def do_take(self, arguments):
        """
        Take one dollar from each of a node's neighbors.

        Aliases: t, +
        """
        if self.auot_cap:
            arguments = arguments.upper()
        try:
            self.graph.take(arguments)
            return True
        except KeyError:
            self.human.error('{} is not a node in the graph.'.format(arguments))

    def game_over(self):
        """Determine if the game has been won. (bool)"""
        if min(self.graph.values.values()) >= 0:
            self.human.tell('You won in {} turns!'.format(self.turns))
            self.win_loss_draw = [1, 0, 0]
            self.scores[self.human.name] = self.genus - self.ease
            return True
        else:
            return False

    def handle_options(self):
        """Handle the option settings for this game. (None)"""
        super(DollarGame, self).handle_options()
        if not self.nodes:
            self.nodes = random.randint(5, 10)
        self.edges = self.genus + self.nodes - 1
        self.total_value = self.genus + self.ease
        self.auto_cap = (self.nodes < 27)

    def player_action(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        print(self.graph)
        move = player.ask('\nWhat is your move? ')
        self.handle_cmd(move)

    def set_options(self):
        """Set up the game options. (None)"""
        self.option_set.add_option('nodes', ['n'], int, 0, valid = range(2, 53),
            question = 'How many nodes should be in the graph (return for 5-10 at random)? ')
        self.option_set.add_option('genus', ['g'], int, 3, check = lambda x: x > 0,
            question = 'What should the genus of the graph be (return for 3)? ')
        self.option_set.add_option('ease', ['e'], int, 2, valid = (1, 2, 3, 4, 5),
            question = 'How easy should the graph be (return for 3)? ')

    def set_up(self):
        """Set up the game. (None)"""
        self.graph = DollarGraph(self.nodes, self.edges, self.total_value)

class DollarGraph(object):
    """
    A graph with a dollar value for each node.

    Attributes:
    edges: The neighbors of the nodes. (dict of str: list of str)
    nodes: The letter names of the nodes. (str)
    values: The dollar values of the nodes. (dict of str: int)

    Methods:
    random_graph: Generate a random set of edges. (None)
    random_values: Populate the values of the graph. (None)

    Overridden Methods:
    __init__
    __str__
    """

    def __init__(self, nodes, edges, total_value):
        """
        Set up the graph. (None)

        Parameters:
        nodes: The number of nodes in the graph. (int)
        edges: The number of edges in the graph. (int)
        total_value: The total of the values in the graph. (int)
        """
        # Set the base attributes.
        self.nodes = (string.ascii_uppercase + string.ascii_lowercase)[:nodes]
        self.values = {char: 0 for char in self.nodes}
        self.edges = {char: [] for char in self.nodes}
        # Fill in the attributes.
        self.random_graph(nodes, edges)
        self.random_values(total_value)

    def __str__(self):
        """Human readable text representation. (str)"""
        text = ''
        for node in self.nodes:
            neighbors = []
            for neighbor in self.edges[node]:
                neighbors.append('{}: {}'.format(neighbor, self.values[neighbor]))
            text = '{}\n{}: {} ({})'.format(text, node, self.values[node], ', '.join(neighbors))
        return text

    def donate(self, node):
        """
        Donate money from a node to its neighbors. (None)

        Parameters:
        node: The node to donate from. (str)
        """
        self.values[node] -= len(self.edges[node])
        for neighbor in self.edges[node]:
            self.values[neighbor] += 1

    def random_graph(self, nodes, edges):
        """
        Generate a random set of edges. (None)

        Algorithm from David Bruce Wilson. Should generate every possible tree with
        equal probability.

        Parameters:
        nodes: The number of nodes in the graph. (int)
        edges: The number of edges in the graph. (int)
        """
        # Set up the edge detection loop.
        current = random.choice(self.nodes)
        found = set(current)
        found_edges = set()
        # Randomly walk the (fully connected) graph.
        # This generates a random spanning graph.
        while len(found) < len(self.nodes):
            new = random.choice(self.nodes)
            if new not in found:
                # When a node is visited the first time, add that edge.
                found.add(new)
                found_edges.add((current, new))
                found_edges.add((new, current))
            current = new
        # Add edges to the spanning graph until it has the required number of edges.
        while len(found_edges) < edges * 2:
            start, end = random.sample(self.nodes, 2)
            found_edges.add((start, end))
            found_edges.add((end, start))
        # Add the randomly calculated edges to the stored graph data.
        for start, end in found_edges:
            self.edges[start].append(end)
        # Sort the edges for clearer output.
        for node in self.nodes:
            self.edges[node].sort()

    def random_values(self, total_value):
        """
        Populate the values of the graph. (None)

        I assume there is bias to this method. I should look into a non-biassed
        method for generating the values, given the constraints of at least one
        negative value and no absolute values greater than the total value.

        Parameters:
        total_value: The defined total of the values in the graph. (int)
        """
        while True:
            # Generate random values in the range.
            values = [random.randint(-total_value, total_value) for value in range(len(self.nodes))]
            # Adjust random values until the correct total value is reached.
            mod = 1 if sum(values) < total_value else -1
            while sum(values) != total_value:
                value_index = random.randrange(len(self.nodes))
                if abs(values[value_index]) < total_value:
                    values[value_index] += mod
            # Exit if you have an unsolved position.
            if min(values) < 0:
                break
        # Set the values.
        self.values = {char: value for char, value in zip(self.nodes, values)}

    def take(self, node):
        """
        Take money from a node's neighbors. (None)

        Parameters:
        node: The node that take the money. (str)
        """
        self.values[node] += len(self.edges[node])
        for neighbor in self.edges[node]:
            self.values[neighbor] -= 1

