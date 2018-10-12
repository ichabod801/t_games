"""
dice_test.py

Unit testing of dice.py.

Classes:
DieTest: Tests of a single die. (unittest.TestCase)
DominoPoolTest: Test of a sampling pool of dice. (unittest.TestCase)
PoolTest: Test of a pool of dice. (unittest.TestCase)
ShuffleDieTest: Tests of a sampling die. (unittest.TestCase)
"""


import unittest

import t_games.dice as dice


class DieTest(unittest.TestCase):
    """Tests of a single die. (unittest.TestCase)"""

    def setUp(self):
        self.die = dice.Die()

    def testAddDie(self):
        """Test adding two dice together."""
        d8 = dice.Die(8)
        self.assertEqual(self.die.value + d8.value, self.die + d8)

    def testAddFloat(self):
        """Test adding a die to a floating point number."""
        self.assertEqual(self.die.value + 1.8, self.die + 1.8)

    def testAddInt(self):
        """Test adding a die to an integer."""
        self.assertEqual(self.die.value + 18, self.die + 18)

    def testEqualDie(self):
        """Test equality across dice."""
        other = dice.Die()
        while other.value != self.die.value:
            other.roll()
        self.assertEqual(other, self.die)

    def testEqualFloat(self):
        """Test equality between a Die and a floating point number."""
        while self.die < 6:
            self.die.roll()
        self.assertEqual(6.0, self.die)

    def testEqualInt(self):
        """Test equality between a Die and an integer."""
        while self.die > 1:
            self.die.roll()
        self.assertEqual(1, self.die)

    def testInequalityGreater(self):
        """Test greater than for a die."""
        self.assertTrue(-1 < self.die)

    def testInequalityLess(self):
        """Test less than for a die."""
        self.assertTrue(self.die < 18)

    def testInqualityNot(self):
        """Test not equals for a die."""
        self.assertNotEqual(801, self.die)

    def testRAddFloat(self):
        """Test right adding a die to a floating point number."""
        self.assertEqual(self.die.value + 1.8, 1.8 + self.die)

    def testRAddInt(self):
        """Test right adding a die to an integer."""
        self.assertEqual(self.die.value + 18, 18 + self.die)

    def testRepr(self):
        """Test a computer readable text representation of a die."""
        self.assertEqual('<Die {}>'.format(self.die.value), repr(self.die))

    def testSort(self):
        """Test sorting a bunch of dice."""
        pool = [dice.Die() for die in range(18)]
        pool.sort()
        self.assertTrue(all([lower <= higher for lower, higher in zip(pool, pool[1:])]))

    def testStr(self):
        """Test a human readable text representation of a die."""
        self.assertEqual(str(self.die.value), str(self.die))


class DominoPoolTest(unittest.TestCase):
    """Test of a sampling pool of dice. (unittest.TestCase)"""

    def setUp(self):
        self.pool = dice.DominoPool()

    def testRepr(self):
        """Test a computer readable text representation of a pool of dice."""
        self.assertEqual('<DominoPool {}, {}>'.format(*self.pool.values), repr(self.pool))


class PoolTest(unittest.TestCase):
    """Test of a pool of dice. (unittest.TestCase)"""

    def setUp(self):
        self.pool = dice.Pool([6] * 5)

    def testCount(self):
        """Test of counting values among the dice."""
        values = [die.value for die in self.pool.dice]
        self.assertEqual(values.count(5), self.pool.count(5))

    def testCountHeld(self):
        """Test of counting values among the dice with held dice."""
        self.pool.hold(*self.pool.values[-2:])
        values = [die.value for die in self.pool.dice + self.pool.held]
        self.assertEqual(values.count(5), self.pool.count(5))

    def testIter(self):
        """Test of iterating over the dice in the pool."""
        self.assertEqual(list(self.pool), self.pool.dice)

    def testIterHold(self):
        """Test of iterating over the dice in the pool."""
        self.pool.hold(*self.pool.values[-2:])
        self.assertEqual(list(self.pool), self.pool.held + self.pool.dice)

    def testRepr(self):
        """Test a computer readable text representation of a pool of dice."""
        values = self.pool.values
        base_text = ', '.join([str(value) for value in values[:4]])
        self.assertEqual('<Pool {}, and {}>'.format(base_text, values[4]), repr(self.pool))

    def testReprHold(self):
        """Test a computer readable text representation of a pool of dice with holds."""
        # Hold two dice.
        self.pool.hold(self.pool.dice[1].value)
        self.pool.hold(self.pool.dice[2].value)
        # Get the text for the values.
        text_bits = [str(die) + '*' for die in self.pool.held] + [str(die) for die in self.pool.dice]
        base_text = ', '.join(text_bits[:4])
        # Check for a match.
        self.assertEqual('<Pool {}, and {}>'.format(base_text, text_bits[4]), repr(self.pool))

    def testReprSmall(self):
        """Test a computer readable text representation of a pool of dice."""
        pool = dice.Pool()
        self.assertEqual('<Pool {} and {}>'.format(*pool.values), repr(pool))

    def testStr(self):
        """Test a human readable text representation of a pool of two dice."""
        values = self.pool.values
        base_text = ', '.join([str(value) for value in values[:4]])
        self.assertEqual('{}, and {}'.format(base_text, values[4]), str(self.pool))

    def testStrHold(self):
        """Test a humn readable text representation of a pool of dice with holds."""
        # Hold two dice.
        self.pool.hold(self.pool.dice[1].value)
        self.pool.hold(self.pool.dice[2].value)
        # Get the text for the values.
        text_bits = [str(die) + '*' for die in self.pool.held] + [str(die) for die in self.pool.dice]
        base_text = ', '.join(text_bits[:4])
        # Check for a match.
        self.assertEqual('{}, and {}'.format(base_text, text_bits[4]), str(self.pool))

    def testStrSmall(self):
        """Test a human readable text representation of a pool of two dice."""
        pool = dice.Pool()
        self.assertEqual('{} and {}'.format(*pool.values), str(pool))


class ShuffleDieTest(unittest.TestCase):
    """Tests of a sampling die. (unittest.TestCase)"""

    def setUp(self):
        self.die = dice.ShuffleDie()

    def testReset(self):
        """Test reeetting a shuffle die."""
        self.die.reset()
        self.assertEqual([1, 2, 3, 4, 5, 6], sorted(self.die.population))

    def testRoll(self):
        """Test rolling a shuffle die."""
        values = [self.die.value]
        for roll in range(5):
            self.die.roll()
            values.append(self.die.value)
        values.sort()
        self.assertEqual([1, 2, 3, 4, 5, 6], values)

    def testRollPop(self):
        """Test that roll removes a possible value."""
        old_len = len(self.die.population)
        self.die.roll()
        self.assertEqual(old_len - 1, len(self.die.population))

    def testRollRepeat(self):
        """Test rolling a shuffle die with a repeat."""
        self.die.repeats = 2
        self.die.reset()
        values = []
        for roll in range(12):
            self.die.roll()
            values.append(self.die.value)
        values.sort()
        self.assertEqual([1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6], values)

    def testRollTwice(self):
        """Test rolling a shuffle die through a reset."""
        values = [self.die.value]
        for roll in range(11):
            self.die.roll()
            values.append(self.die.value)
        values.sort()
        self.assertEqual([1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6], values)

    def testRepr(self):
        """Test a computer readable text representation of a shuffle die."""
        self.assertEqual('<ShuffleDie {}>'.format(self.die.value), repr(self.die))


if __name__ == '__main__':
    unittest.main()
