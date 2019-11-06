"""
full_credits.py

Generate the full credits for tgames.

Copyright (C) 2018 by Craig O'Brien and the t_games contributors.
See the top level __init__.py file for details on the t_games license.

Constants:
CREDITS_DATA: The sections and people who worked on those sections. (list)
FULL_CREDITS: The formatted text of CREDITS_DATA. (str)

Functions:
data_to_text: Convert CREDITS_DATA to formatted text. (str)
"""


CREDITS_DATA = [('Interface Programming', """Craig O'Brien, Micah Page"""),
    ('Game Design', """Humans; Paul Alfille, C. Graham Baker, Elwood T. Baker, Matt Baker,
        Richard A. Canfield, Melvin Dresher, Doug Dyment, Charles Fey, Merrill Flood, Michael Keller,
        Bernard de Marigny, Albert Morehead, Geoffrey Mott-Smith, Craig O'Brien, Ned Strongin, Sid Sackson,
        John Suckling, Howard Wexler, Gregory Yob"""),
    ('Game Programming', """Thomas Ahle, Craig O'Brien, David B. Wilson"""),
    ('Bot Design', """Robert Axelrod, B. Beaufils, S. Braver, K. Deb, J. Delahaye, James Friedman,
        Roger Johnson, Reiner Knizia, J. Komorita, David Kraines, Vivian Kraines, S. Mittal, Todd Neller,
        Craig O'Brien, Mathieu Our, Clifton Presser, Anatol Rapoport, J. Sheposh, Gerry Tesauro"""),
    ('Bot Programming', """Craig "Ichabod" O'Brien"""),
    ('Documentation', """wma, Craig O'Brien"""),
    ('Play Testing', """Doug Edmunds, Craig O'Brien, Micah Page, Dustin Roberts"""),
    ('Special Thanks', """Guido van Rossum; python-forum.io, github.com, Wikipedia, pagat.com;
        Alan Beale, Bill Budge, Kris Burm, George Carlin, Matt Groening, Lawrence Lasker, Walter F. Parks,
        David Parlett""")]


def data_to_text():
    """Convert CREDITS_DATA to formatted text. (str)"""
    credits_text = ''
    # Loop through the sections.
    for section, people in CREDITS_DATA:
        # Show the section title.
        credits_text += '\n{:^79}\n{:^79}\n'.format(section, '-' * len(section))
        for line in people.split(';'):
            # Loop through the names.
            names = line.strip().split(',')
            while names:
                # Display the names four at a time.
                quad, names = names[:4], names[4:]
                quad_text = ''.join(['{:^20}'.format(name.strip()) for name in quad])
                credits_text += '{:^79}\n'.format(quad_text)
    return credits_text


# The formatted text of CREDITS_DATA.
FULL_CREDITS = data_to_text()


if __name__ == '__main__':
    print(FULL_CREDITS)
