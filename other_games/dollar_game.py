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

    def __init__(self, nodes, edges, total_value):
        self.nodes = string.ascii_uppercase[:nodes]
        self.values = {char: 0 for char in self.nodes}
        self.edges = {char: [] for char in self.nodes}
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

    def random_graph(self, nodes, edges, total_value):
        current = random.choice(self.nodes)
        found = set(current)
        found_edges = set()
        while len(found) < len(self.nodes):
            new = random.choice(self.nodes)
            if new not in found:
                found.add(new)
                found_edges.add((current, new))
                found_edges.add((new, current))
            current = new
        while len(found_edges) < edges * 2:
            start, end = random.sample(self.nodes, 2)
            found_edges.add((start, end))
            found_edges.add((end, start))
        for start, end in found_edges:
            self.edges[start].append(end)
        for node in self.nodes:
            self.edges[node].sort()

    def random_values(self, total_value):
        while sum(self.values.values()) < total_value:
            node = random.choice(self.nodes)
            if random.random() < 0.69:
                self.values[node] += 1
            else:
                self.values[node] -= 1
