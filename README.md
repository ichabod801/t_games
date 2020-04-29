## t_games

The t_games project is a suite of text games to play on a command-line interface (CLI). It contains board games, card games, dice games, and other miscellany. It is also a framework of useful objects for writing your own CLI games. You can easily write your own game as a subclass of the main Game class. If you include the game in the t_games folders, it will be detected by the system and included in the t_games interface. See [Game Objects](https://github.com/ichabod801/t_games/wiki/Game-Objects) in the wiki for more details.

### Getting Started

Simply download the files and use the play function:

```python
import t_games
t_games.play()
```

If you download the files to a folder in your Python path, you should be able to do this from any location. Otherwise you will need to be in the parent folder of the t_games folder (2.7 or 3.0+) or the t_games folder itself (3.0+ only).

Alternatively, you can go to the folder you downloaded them into and run `python play.py`.

The system will ask you three questions to uniquely identify you, and then it will set up a player profile so you can play games. It's a standard, old-fashioned menu system, but you can type `help` for ways to get around that.

#### Prerequisites

None. The t_games system is designed to run in base Pyton, in either 2.7 or the latest 3.x.

### Contributing

The t_games project is idling at the moment. I wanted to get the project to a point I could call "finished," and it's there. Now I want to move on. If you would like to do some development on the project or add some games to it, please email me at t_admin at xenomind dot com.

I will certainly work on any bug reports I get. Either make an issue and add it to the Weevilwood project, or email me at t_admin at xenomind dot com. Please include as much information as possible. Best is a copy and paste from the console including the last game state, your last action, and the full text of the traceback (or a description of why the output was wrong). If you were playing the game with any options, please include those as well.

### Versioning

The t_games project uses a three number versioning system compatible with [PEP 440](https://www.python.org/dev/peps/pep-0440/). The first number is the major release cycle, the second number is the number of games contained in the release, and the third number is the number of changes since the last game was released. Alpha and beta releases will be identified as per GitHub conventions.

### Authors

* **Craig "Ichabod" O'Brien** :skull: wrote the original interface and the initial games.

Type `credits` from the main menu to see a list of contributors and acknowledgements.

### License

This project is licensed under the GPLv3 license. See the LICENSE.md file for details.