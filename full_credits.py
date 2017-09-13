"""
full_credits.py

Generate the full credits for tgames.

Constants:
CREDITS_DATA: The sections and people who worked on those sections. (list)
FULL_CREDITS: The formatted text of CREDITS_DATA. (str)

Functions:
data_to_text: Convert CREDITS_DATA to formatted text. (str)
"""


CREDITS_DATA = [('Interface Programming', """Craig "Ichabod" O'Brien"""),
    ('Game Design', """Humans; Paul Alfille, Richard A. Canfield, Sid Sackson, Gregory Yob"""),
    ('Game Programming', """Craig "Ichabod" O'Brien"""),
    ('Bot Design', """Roger Johnson, Reiner Knizia, Todd Neller, Craig O'Brien, Clifton Presser"""),
    ('Bot Programming', """Craig "Ichabod" O'Brien"""),
    ('Play Testing', """Craig "Ichabod" O'Brien"""),
    ('Special Thanks', """Guido van Rossum; python-forum.io, github.com, Wikipedia; 
        Kris Burm, Matt Groening""")]


def data_to_text():
    """Convert CREDITS_DATA to formatted text. (str)"""
    credits_text = ''
    for section, people in CREDITS_DATA:
        credits_text += '\n{:^79}\n{:^79}\n'.format(section, '-' * len(section))
        for line in people.split(';'):
            names = line.strip().split(',')
            while names:
                quad, names = names[:4], names[4:]
                quad_text = ''.join(['{:^20}'.format(name.strip()) for name in quad])
                credits_text += '{:^79}\n'.format(quad_text)
    return credits_text
FULL_CREDITS = data_to_text()


if __name__ == '__main__':
    print(FULL_CREDITS)