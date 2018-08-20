"""
__init__.py

Package initializer for t_games.

Copyright (C) 2018 by Craig O'Brien and the t_game contributors.

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
details.

See <http://www.gnu.org/licenses/> for details on this license (GPLv3).

Functions:
play: Play some text games. (None)
"""

from __future__ import print_function

import t_games.dice as dice
import t_games.game as game
import t_games.interface as interface
import t_games.player as player
from t_games.play import play
from t_games.test import test


if __name__ == '__main__':
    play()
