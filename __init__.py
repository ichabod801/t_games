"""
__init__.py

Package initializer for t_games.

Copyright (C) 2018 by Craig O'Brien and the t_games contributors.

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
details.

See <http://www.gnu.org/licenses/> for details on this license (GPLv3).
"""


from . import board
from . import cards
from . import dice

from .interface import Interface
from .play import play, test


if __name__ == '__main__':
    play()
