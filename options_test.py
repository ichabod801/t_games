"""
options_test.py

Unit testing of options.py
"""


import unittest

from tgames import game
from tgames import options


class ParseTestTest(unittest.TestCase):
	"""Tests of OptionSet.parse_settings changing OptionSet.settings_text"""

	def setUp(self):
		self.option_set = options.OptionSet(object())
		self.option_set.add_option('spam')
		self.option_set.add_option('three', ['3'], int, 5)

	def testBasic(self):
		"""Test a simple option."""
		self.option_set.parse_settings('spam')
		self.assertEqual('spam', self.option_set.settings_text)

	def testEquals(self):
		"""Test setting an option value."""
		self.option_set.parse_settings('three=5')
		self.assertEqual('three=5', self.option_set.settings_text)

	def testEqualsSpace(self):
		"""Test setting an option value with spaces."""
		self.option_set.parse_settings('three = 5')
		self.assertEqual('three=5', self.option_set.settings_text)

	def testEqualsSpaceAfter(self):
		"""Test setting an option value with a space after."""
		self.option_set.parse_settings('three= 5')
		self.assertEqual('three=5', self.option_set.settings_text)

	def testEqualsSpaceBefore(self):
		"""Test setting an option value with a space before."""
		self.option_set.parse_settings('three =5')
		self.assertEqual('three=5', self.option_set.settings_text)

	def testEqualsSpaceMultiple(self):
		"""Test setting an option value with multiple spaces."""
		self.option_set.parse_settings('three  =  5')
		self.assertEqual('three=5', self.option_set.settings_text)

	def testSort(self):
		"""Test sorting multiple options."""
		self.option_set.parse_settings('three=3 spam')
		self.assertEqual('spam three=3', self.option_set.settings_text)


if __name__ == '__main__':
	unittest.main()