"""
wumpus_test.py

Unit testing of t_games/other_games/wumpus_game.py

Classes:
CaveTest: Tests of caves in the dungeon. (unittest.TestCase)
DodecahedronTest: Test of a dungeon of caves. (unittest.TestCase)
"""


import unittest

import t_games.other_games.wumpus_game as wumpus


class CaveTest(unittest.TestCase):
    """Tests of caves in the dungeon. (unittest.TestCase)"""

    def testReprPlain(self):
        """Test the debugging text of an empty cave."""
        cave = wumpus.Cave(18)
        self.assertEqual('<Cave 18>', repr(cave))

    def testReprWumpus(self):
        """Test the debugging text of a cave with a flag."""
        cave = wumpus.Cave(5)
        cave.wumpus = True
        self.assertEqual('<Cave 5 Wumpus>', repr(cave))


class DodecahedronTest(unittest.TestCase):
    """Test of a dungeon of caves. (unittest.TestCase)"""

    def correctRepr(self):
        """Get the correct repr for the current dungeon. (str)"""
        # Check the flags.
        bats, pits, wumpus = [], [], []
        for cave in self.dungeon.caves:
            if cave.bats:
                bats.append(str(cave.id))
            if cave.pit:
                pits.append(str(cave.id))
            if cave.wumpus:
                wumpus.append(cave.id)
        # Set up the correct repr.
        check = '<Dodecahedron Current: {}; Bats: {}; Pits: {}; Wumpus: {}>'
        return check.format(self.dungeon.current, ', '.join(bats), ', '.join(pits), wumpus[0])

    def setUp(self):
        self.dungeon = wumpus.Dodecahedron()

    def testRepr(self):
        """Test the debugging text of a system of caves."""
        self.assertEqual(self.correctRepr(), repr(self.dungeon))

    def testReprMove(self):
        """Test the debugging text of a system of caves after a wumpus move."""
        self.dungeon.move_wumpus()
        self.assertEqual(self.correctRepr(), repr(self.dungeon))


if __name__ == '__main__':
    unittest.main()
