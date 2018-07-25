"""
_test_all.py

Overall unit testing for the t_games project.
"""

import unittest

if __name__ == '__main__':
	test_suite = unittest.defaultTestLoader.discover('.', pattern = '*_test.py')
	unittest.TextTestRunner(verbosity = 1).run(test_suite)