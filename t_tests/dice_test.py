"""
dice_test.py

Unit testing of dice.py.

Classes:
DieTest: Tests of a single die. (unittest.TestCase)
DominoPoolRollTest: Test rolling a sampling pool of dice. (unittest.TestCase)
DominoPoolTest: Test of a sampling pool of dice. (unittest.TestCase)
PoolTest: Test of a pool of dice. (unittest.TestCase)
ShuffleDieTest: Tests of a sampling die. (unittest.TestCase)
"""


from __future__ import division

import operator
import unittest

from t_games import dice


class DieTest(unittest.TestCase):
    """Tests of a single die. (unittest.TestCase)"""

    def setUp(self):
        self.die = dice.Die()

    def testAbsNegative(self):
        """Test the absolute value of a negative die."""
        self.die.value = -3
        self.assertEqual(3, abs(self.die))

    def testAbsPositive(self):
        """Test the absolute value of a postive die."""
        self.assertEqual(self.die.value, abs(self.die))

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

    def testComplexEqual(self):
        """Test a complex version of a die being equal to the die."""
        self.assertEqual(complex(self.die), self.die)

    def testComplexParts(self):
        """Test the parts of a comple version of a die."""
        c = complex(self.die)
        self.assertEqual((self.die.value, 0.0), (c.real, c.imag))

    def testCopyIndependent(self):
        """Test that changing a copy of a die does not change the original die."""
        other = self.die.copy()
        self.die.value = 7
        other.roll()
        self.assertNotEqual(self.die.value, other.value)

    def testCopyValue(self):
        """Test that the copy of a die has the same value."""
        self.assertEqual(self.die.value, self.die.copy().value)

    def testDivMod(self):
        """Test divmoding a die."""
        self.assertEqual((self.die.value // 3, self.die.value % 3), divmod(self.die, 3))

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

    def testFloatEqual(self):
        """Test a float version of a Die being a float."""
        self.assertEqual(float(self.die), self.die)

    def testFloatType(self):
        """The the type of a float version of a Die."""
        self.assertEqual(float, type(float(self.die)))

    def testFloorDivDie(self):
        """Test floor division with another die."""
        other = dice.Die()
        other.value = 2
        self.assertEqual(self.die.value // 2, self.die // other)

    def testFloorDivInt(self):
        """Test floor division of a die by an integer."""
        self.assertEqual(self.die.value // 2, self.die // 2)

    def testFloorDivZero(self):
        """Test floor division of a die guaranteed to be zero."""
        self.assertEqual(0, self.die // 7)

    def testIndexType(self):
        """Test the type when converting a die to an index."""
        die = dice.Die([1.5, 2.5, 3.5])
        self.assertIsInstance(operator.index(die), int)

    def testIndexValue(self):
        """Test value when converting a die to an index."""
        die = dice.Die([1.5, 2.5, 3.5])
        check = [0, 1, 1, 1, 0, 0]
        self.assertEqual(1, check[die])

    def testInequalityGreater(self):
        """Test greater than for a die."""
        self.assertTrue(-1 < self.die)

    def testInequalityLess(self):
        """Test less than for a die."""
        self.assertTrue(self.die < 18)

    def testInequalityNot(self):
        """Test not equals for a die."""
        self.assertNotEqual(801, self.die)

    def testIntType(self):
        """Test the type when converting a die to an int."""
        die = dice.Die([1.5, 2.5, 3.5])
        self.assertIsInstance(int(die), int)

    def testIntValue(self):
        """Test value when converting a die to an int."""
        die = dice.Die([1.5, 2.5, 3.5])
        self.assertIn(int(die), (1, 2, 3))

    def testModDie(self):
        """Test the modulus of a die by a die."""
        other = dice.Die()
        other.value = 2
        self.assertEqual(self.die.value % 2, self.die % other)

    def testModInt(self):
        """Test the modulus of a die by an integer."""
        self.assertEqual(self.die.value % 2, self.die % 2)

    def testMultiplyDie(self):
        """Test multiplication by a die."""
        other = dice.Die()
        other.value = 5
        self.assertEqual(self.die.value * 5, self.die * other)

    def testMultiplyInt(self):
        """Test multiplication by an integer."""
        self.assertEqual(self.die.value * 4, self.die * 4)

    def testMultiplyOne(self):
        """Test multiplication by the identity."""
        self.assertEqual(self.die.value, self.die * 1)

    def testMultiplyZero(self):
        """Test multiplication by the absorber."""
        self.assertEqual(0, self.die * 0)

    def testNegation(self):
        """Test the negation of a die."""
        self.assertEqual(self.die.value * -1, -self.die)

    def testPositiveNegative(self):
        """Test the positive of a negative die."""
        die = dice.Die([-1, -2, -3])
        self.assertEqual(die.value, +die)

    def testPositivePositive(self):
        """Test the positive of a positive die."""
        self.assertEqual(self.die.value, +self.die)

    def testPowDie(self):
        """Test exponetiation by a die."""
        other = dice.Die()
        other.value = 5
        self.assertEqual(self.die.value ** 5, self.die ** other)

    def testPowInt(self):
        """Test exponetiation by an integer."""
        self.assertEqual(self.die.value ** 4, self.die ** 4)

    def testPowMod(self):
        """Test exponentiation of a die with a modules."""
        self.assertEqual(pow(self.die.value, 3, 4), pow(self.die, 3, 4))

    def testPowOne(self):
        """Test exponetiation by the identity."""
        self.assertEqual(self.die.value, self.die ** 1)

    def testPowZero(self):
        """Test exponetiation by zero."""
        self.assertEqual(1, self.die ** 0)

    def testRAddFloat(self):
        """Test right adding a die to a floating point number."""
        self.assertEqual(self.die.value + 1.8, 1.8 + self.die)

    def testRAddInt(self):
        """Test right adding a die to an integer."""
        self.assertEqual(self.die.value + 18, 18 + self.die)

    def testRepr(self):
        """Test a computer readable text representation of a die."""
        self.assertEqual('<Die {}>'.format(self.die.value), repr(self.die))

    def testRightDivMod(self):
        """Test divmoding a die on the right."""
        self.assertEqual((3 // self.die.value, 3 % self.die.value), divmod(3, self.die))

    def testRightFloorDivDie(self):
        """Test right-handed floor division with another die."""
        other = dice.Die()
        other.value = 2
        self.assertEqual(2 // self.die.value, other // self.die)

    def testRightFloorDivInt(self):
        """Test right-handed floor division of a die by an integer."""
        self.assertEqual(2 // self.die.value, 2 // self.die)

    def testRightModDie(self):
        """Test right-handed modulus of a die by a die."""
        other = dice.Die()
        other.value = 2
        self.assertEqual(2 % self.die.value, other % self.die)

    def testRightModInt(self):
        """Test right-handed modulus of a die by an integer."""
        self.assertEqual(2 % self.die.value, 2 % self.die)

    def testRightMultiplyDie(self):
        """Test right-handed multiplication by a die."""
        other = dice.Die()
        other.value = 5
        self.assertEqual(5 * self.die.value, other * self.die)

    def testRightMultiplyInt(self):
        """Test right-handed multiplication by an integer."""
        self.assertEqual(self.die.value * 4, 4 * self.die)

    def testRightMultiplyOne(self):
        """Test right-handed multiplication by the identity."""
        self.die.value = 1
        self.assertEqual(18, self.die * 18)

    def testRightMultiplyZero(self):
        """Test right-handed multiplication by the absorber."""
        self.die.value = 0
        self.assertEqual(0, self.die * 81)

    def testRightPowInt(self):
        """Test right-handed exponetiation of an integer."""
        self.assertEqual(4 ** self.die.value, 4 ** self.die)

    def testRightPowOne(self):
        """Test right-handed exponetiation by the identity."""
        self.die.value = 1
        self.assertEqual(108, 108 ** self.die)

    def testRightPowZero(self):
        """Test right-handed exponetiation by zero."""
        self.die.value = 0
        self.assertEqual(1, 801 ** self.die)

    def testRightSubtractInt(self):
        """Test right-hand subtraction with an integer."""
        self.assertEqual(4 - self.die.value, 4 - self.die)

    def testRightSubtractZero(self):
        """Test right-hand subtraction of nothing."""
        self.die.value = 0
        self.assertEqual(83, 83 - self.die)

    def testRightTrueDivInt(self):
        """Test right-hand division of a die with an integer."""
        self.assertEqual(4 / self.die.value, 4 / self.die)

    def testRightTrueDivOne(self):
        """Test right-hand division of a die with the identity."""
        self.die.value = 1
        self.assertEqual(424, 424 / self.die)

    def testRollHeld(self):
        """Test trying to roll a held die."""
        self.die.held = True
        self.assertRaises(ValueError, self.die.roll)

    def testRound(self):
        """Test rounding a die."""
        die = dice.Die([1.1, 1.2, 1.3])
        self.assertEqual(1, round(die))

    def testRoundPlaces(self):
        """Test rounding a die to a particular precision."""
        die = dice.Die([1.11, 1.12, 1.13])
        self.assertEqual(1.1, round(die, 1))

    def testSort(self):
        """Test sorting a bunch of dice."""
        pool = [dice.Die() for die in range(18)]
        pool.sort()
        self.assertTrue(all([lower <= higher for lower, higher in zip(pool, pool[1:])]))

    def testStr(self):
        """Test a human readable text representation of a die."""
        self.assertEqual(str(self.die.value), str(self.die))

    def testSubtractDie(self):
        """Test subtraction of a die with a die."""
        other = dice.Die()
        other.value = 4
        self.assertEqual(self.die.value - 4, self.die - other)

    def testSubtractInt(self):
        """Test subtraction of a die with an integer."""
        self.assertEqual(self.die.value - 4, self.die - 4)

    def testSubtractZero(self):
        """Test subtraction of a die with nothing."""
        self.assertEqual(self.die.value, self.die - 0)

    def testTrueDivDie(self):
        """Test division of a die with a die."""
        other = dice.Die()
        other.value = 3
        self.assertEqual(self.die.value / 3, self.die / other)

    def testTrueDivInt(self):
        """Test division of a die with an integer."""
        self.assertEqual(self.die.value / 2, self.die / 2)

    def testTrueDivOne(self):
        """Test division of a die with the identity."""
        self.assertEqual(self.die.value, self.die / 1)


class DominoPoolRollTest(unittest.TestCase):
    """Test rolling a sampling pool of dice. (unittest.TestCase)"""

    def setUp(self):
        self.pool = dice.DominoPool()
        self.rolls = self.pool.values[:]
        for roll in range(len(self.pool.possible) - 1):
            self.rolls.extend(self.pool.roll())

    def test1s(self):
        """Test that an appropriate number of ones are rolled by a domino pool."""
        self.assertTrue(self.rolls.count(1) >= 7)

    def test2s(self):
        """Test that an appropriate number of twos are rolled by a domino pool."""
        self.assertTrue(self.rolls.count(2) >= 7)

    def test3s(self):
        """Test that an appropriate number of threes are rolled by a domino pool."""
        self.assertTrue(self.rolls.count(3) >= 7)

    def test4s(self):
        """Test that an appropriate number of fours are rolled by a domino pool."""
        self.assertTrue(self.rolls.count(4) >= 7)

    def test5s(self):
        """Test that an appropriate number of fives are rolled by a domino pool."""
        self.assertTrue(self.rolls.count(5) >= 7)

    def test6s(self):
        """Test that an appropriate number of sixes are rolled by a domino pool."""
        self.assertTrue(self.rolls.count(6) >= 7)

    def testPopulation(self):
        """Test resetting a domino pool."""
        self.assertEqual(len(self.pool.possible), len(self.pool.population))


class DominoPoolTest(unittest.TestCase):
    """Test of a sampling pool of dice. (unittest.TestCase)"""

    def setUp(self):
        self.pool = dice.DominoPool()

    def testReplaceNo(self):
        """Test replacing with a valid value."""
        self.assertEqual(5, self.pool.replace(5))

    def testReplaceYes(self):
        """Test replacing with an invalid value."""
        self.assertNotEqual(0, self.pool.replace(0))

    def testRepr(self):
        """Test a computer readable text representation of a pool of dominoes."""
        self.assertEqual('<DominoPool {} and {}>'.format(*self.pool.values), repr(self.pool))

    def testStr(self):
        """Test a human readable text representation of a domino pool."""
        self.assertEqual('{} and {}'.format(*self.pool.values), str(self.pool))

    def testStrLong(self):
        """Test a human readable text representation of a triomino pool."""
        pool = dice.DominoPool([4, 4, 4], dice.Die(4))
        check = '{0}, {1}, and {2}'.format(*pool.values)
        self.assertEqual(check, str(pool))


class PoolTest(unittest.TestCase):
    """Test of a pool of dice. (unittest.TestCase)"""

    def setUp(self):
        self.pool = dice.Pool([6] * 5)

    def testAppendDie(self):
        """Test appending a die to the pool."""
        other = dice.Die()
        other.value = 7
        self.pool.append(other)
        self.assertIs(other, self.pool.dice[-1])

    def testAppendValue(self):
        """Test appending a value to the pool."""
        other = dice.Die()
        other.value = 7
        self.pool.append(other)
        self.assertEqual(7, self.pool.values[-1])

    def testContains(self):
        """Test an item being in the list."""
        check = self.pool[1].value
        self.assertIn(check, self.pool)

    def testContainsNot(self):
        """Test an item not being in the list."""
        check = [value for value in range(1, 7) if value not in self.pool.values][0]
        self.assertNotIn(check, self.pool)

    def testCount(self):
        """Test of counting values among the dice."""
        values = [die.value for die in self.pool.dice]
        self.assertEqual(values.count(5), self.pool.count(5))

    def testCountHeld(self):
        """Test of counting values among the dice with held dice."""
        self.pool.hold(self.pool.values[-2:])
        values = [die.value for die in self.pool.dice]
        self.assertEqual(values.count(5), self.pool.count(5))

    def testDeleteDie(self):
        """Test deleting a die from the pool."""
        del self.pool[3]
        self.assertEqual(4, len(self.pool.dice))

    def testDeleteValue(self):
        """Test deleting a value from the pool."""
        del self.pool[0]
        self.assertEqual(4, len(self.pool.values))

    def testExtendDice(self):
        """Test extending a pool by dice."""
        others = [dice.Die(), dice.Die()]
        self.pool.extend(others)
        self.assertIs(others[0], self.pool.dice[-2])
        self.assertIs(others[1], self.pool.dice[-1])

    def testExtendValues(self):
        """Test extending a pool by values."""
        others = [dice.Die(), dice.Die()]
        values = [die.value for die in others]
        self.pool.extend(others)
        self.assertEqual(values, self.pool.values[-2:])

    def testGetItemIndex(self):
        """Test getting a die by index."""
        self.assertIs(self.pool.dice[2], self.pool[2])

    def testGetItemNegative(self):
        """Test getting a die by negative index."""
        self.assertIs(self.pool.dice[-1], self.pool[-1])

    def testGetItemSkip(self):
        """Test getting a die by slice with skip."""
        self.assertEqual(self.pool.dice[::2], self.pool[::2])

    def testGetItemSlice(self):
        """Test getting a die by slice."""
        self.assertEqual(self.pool.dice[1:-1], self.pool[1:-1])

    def testHoldDice(self):
        """Test holding dice holds the dice."""
        last_two = self.pool.dice[-2:]
        values = [die.value for die in last_two]
        self.pool.hold(values)
        self.assertEqual(sorted(last_two), sorted([die for die in self.pool if die.held]))

    def testIndex(self):
        """Test indexing a value."""
        for check in range(1, 7):
            if check in self.pool:
                break
        self.assertEqual(self.pool.dice.index(check), self.pool.index(check))

    def testIter(self):
        """Test of iterating over the dice in the pool."""
        self.assertEqual(list(self.pool), self.pool.dice)

    def testIterHold(self):
        """Test of iterating over the dice in the pool."""
        self.pool.hold(self.pool[2].value)
        self.assertEqual(self.pool.dice, list(self.pool))

    def testInsertDie(self):
        """Test inserting a die in the pool."""
        other = dice.Die()
        other.value = 7
        self.pool.insert(3, other)
        self.assertIs(other, self.pool.dice[3])

    def testInsertValue(self):
        """Test setting a value in the pool with an index."""
        other = dice.Die()
        other.value = 7
        self.pool.insert(1, other)
        self.assertEqual(7, self.pool.values[1])

    def testLen(self):
        """Test the length of a pool."""
        self.assertEqual(5, len(self.pool))

    def testPopIndexValue(self):
        """Test the return value of popping a pool with an index."""
        check = self.pool[2]
        self.assertIs(check, self.pool.pop(2))

    def testPopLenDice(self):
        """Test that pop removes a die."""
        self.pool.pop()
        self.assertEqual(4, len(self.pool.dice))

    def testPopLenValues(self):
        """Test that pop removes a die."""
        self.pool.pop()
        self.assertEqual(4, len(self.pool.values))

    def testPopValue(self):
        """Test the return value of popping a pool."""
        check = self.pool[-1]
        self.assertIs(check, self.pool.pop())

    def testReleaseAll(self):
        """Test releasing all of the dice."""
        self.pool.hold(self.pool.values)
        self.pool.release()
        self.assertEqual(5, len(self.pool.dice))

    def testReleaseNone(self):
        """Test releasing when no dice are held."""
        self.pool.release()
        self.assertEqual(5, len(self.pool.dice))

    def testReleaseSome(self):
        """Test releasing some of the dice."""
        self.pool.hold(self.pool.values[:2])
        self.pool.release()
        self.assertEqual(5, len(self.pool.dice))

    def testRemoveDie(self):
        """Test removing a die from the pool."""
        for check in range(1, 7):
            if check in self.pool:
                break
        self.pool.remove(check)
        self.assertEqual(4, len(self.pool.dice))

    def testRemoveValue(self):
        """Test removing a value from the pool."""
        for check in range(1, 7):
            if check in self.pool:
                break
        self.pool.remove(check)
        self.assertEqual(4, len(self.pool.values))

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
        base_text = ', '.join([str(die) for die in self.pool])
        last_comma = base_text.rfind(',') + 1
        check = '<Pool {} and{}>'.format(base_text[:last_comma], base_text[last_comma:])
        # Check for a match.
        self.assertEqual(check, repr(self.pool))

    def testReprSmall(self):
        """Test a computer readable text representation of a pool of dice."""
        pool = dice.Pool()
        self.assertEqual('<Pool {} and {}>'.format(*pool.values), repr(pool))

    def testReverseDice(self):
        """Test reversing a pool in place by dice."""
        check = self.pool.dice[::-1]
        self.pool.reverse()
        self.assertEqual(check, self.pool)

    def testReverseValues(self):
        """Test reversing a pool in place by values."""
        check = self.pool.values[::-1]
        self.pool.reverse()
        self.assertEqual(check, self.pool.values)

    def testReversed(self):
        """Test a reversed pool."""
        self.assertEqual(list(reversed(self.pool.values)), [die.value for die in reversed(self.pool)])

    def testRollHeld(self):
        """Test that rolling does not affect held dice."""
        held_values = sorted(self.pool.values[:2])
        self.pool.hold(held_values)
        self.pool.roll()
        self.assertEqual(held_values, sorted([die for die in self.pool if die.held]))

    def testRollIndex(self):
        """Test that rolling by index does not affect the other values."""
        held_values = self.pool.values[:]
        self.pool.roll(4)
        self.assertEqual(held_values[:4], self.pool.values[:4])

    def testSetItemIndexDie(self):
        """Test setting a die in the pool with an index."""
        other = dice.Die()
        other.value = 7
        self.pool[2] = other
        self.assertIs(other, self.pool.dice[2])

    def testSetItemIndexValue(self):
        """Test setting a value in the pool with an index."""
        other = dice.Die()
        other.value = 7
        self.pool[2] = other
        self.assertEqual(7, self.pool.values[2])

    def testSetItemNegativeDie(self):
        """Test setting a die in the pool with a negative index."""
        other = dice.Die()
        other.value = -1
        self.pool[-1] = other
        self.assertIs(other, self.pool.dice[-1])

    def testSetItemNegativeValue(self):
        """Test setting a value in the pool with a negative index."""
        other = dice.Die()
        other.value = -1
        self.pool[-1] = other
        self.assertEqual(-1, self.pool.values[-1])

    def testSortHoldKey(self):
        """Test sorting the values with a key function and held dice."""
        self.pool.hold(self.pool.values[:2])
        check = [die.value for die in sorted(self.pool, key = id)]
        self.pool.sort(key = id)
        self.assertEqual(check, self.pool.values)

    def testSortHoldPlain(self):
        """Test sorting the values with held dice."""
        self.pool.hold(self.pool.values[:2])
        check = [die.value for die in sorted(self.pool)]
        self.pool.sort()
        self.assertEqual(check, self.pool.values)

    def testSortHoldReverse(self):
        """Test sorting the values with reversal and held dice."""
        self.pool.hold(self.pool.values[:2])
        check = [die.value for die in sorted(self.pool, reverse = True)]
        self.pool.sort(reverse = True)
        self.assertEqual(check, self.pool.values)

    def testSortKey(self):
        """Test sorting the values with a key function."""
        check = [die.value for die in sorted(self.pool, key = id)]
        self.pool.sort(key = id)
        self.assertEqual(check, self.pool.values)

    def testSortPlain(self):
        """Test sorting the values without parameters."""
        check = [die.value for die in sorted(self.pool)]
        self.pool.sort()
        self.assertEqual(check, self.pool.values)

    def testSortReverse(self):
        """Test sorting the values with reversal."""
        check = [die.value for die in sorted(self.pool, reverse = True)]
        self.pool.sort(reverse = True)
        self.assertEqual(check, self.pool.values)

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
        base_text = ', '.join([str(die) for die in self.pool])
        last_comma = base_text.rfind(',') + 1
        check = '{} and{}'.format(base_text[:last_comma], base_text[last_comma:])
        # Check for a match.
        self.assertEqual(check, str(self.pool))

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
