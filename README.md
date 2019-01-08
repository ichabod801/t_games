## t_games

The t_games project is a suite of text games to play on a command-line interface (CLI). It contains board games, card games, dice games, and other miscellany. It is also a framework of useful objects for writing your own CLI games. You can easily write your own game as a subclass of the main Game class. If you include the game in the t_games folders, it will be detected by the system and included in the t_games interface.

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

The t_games project is currently looking for people to playtest it looking for bugs before the final release. If you are interested in being invovled, send an email to t_admin at xenomind dot com.

### Versioning

The t_games project uses a three number versioning system compatible with [PEP 440](https://www.python.org/dev/peps/pep-0440/). The first number is the major release cycle, the second number is the number of games contained in the release, and the third number is a sequential, zero-indexed serial number. Beta (open play testing) releases will be identified as per PEP 440.

### Authors

* **Craig "Ichabod" O'Brien** :skull: wrote the original interface and the initial games.

Type `credits` from the main menu to see a list of contributors and acknowledgements.

### License

This project is licensed under the GPLv3 license. See the LICENSE.md file for details.