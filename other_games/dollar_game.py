"""
dollar_game.py

The Dollar Game, as specified in this Numberphile video:
https://www.youtube.com/watch?v=U33dsEcKgeQ&t=3s
"""


import random
import string

from .. import game


class DollarGame(game.Game):
    pass


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
        self.nodes = string.ascii_uppercase[:nodes]
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
            text = '{}\n{}: {} {}'.format(text, node, self.values[node], ', '.join(neighbors))
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

