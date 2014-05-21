# -*- coding: utf-8 -*-
# Copyright © 2014 SEE AUTHORS FILE
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

BG = {}
BG['BLACK'] = '\033[40m'
BG['RED'] = '\033[41m'
BG['GREEN'] = '\033[42m'
BG['YELLOW'] = '\033[43m'
BG['BLUE'] = '\033[44m'
BG['PURPLE'] = '\033[45m'
BG['CYAN'] = '\033[46m'
BG['LIGHTGRAY'] = '\033[47m'
COLORS = {}
COLORS['RESTORE'] = '\033[0m'
COLORS['RED'] = '\033[00;31m'
COLORS['GREEN'] = '\033[00;32m'
COLORS['YELLOW'] = '\033[00;33m'
COLORS['BLUE'] = '\033[00;34m'
COLORS['PURPLE'] = '\033[00;35m'
COLORS['CYAN'] = '\033[00;36m'
COLORS['TEAL'] = '\033[00;36m'
COLORS['LIGHTGRAY'] = '\033[00;37m'
COLORS['LRED'] = '\033[01;31m'
COLORS['LGREEN'] = '\033[01;32m'
COLORS['LYELLOW'] = '\033[01;33m'
COLORS['LBLUE'] = '\033[01;34m'
COLORS['LPURPLE'] = '\033[01;35m'
COLORS['LCYAN'] = '\033[01;36m'
COLORS['WHITE'] = '\033[01;37m'


def colorize(item, color=None, underline=False, background=None):
    if underline:
        ul = "\033[4m"
    else:
        ul = ''

    if background:
        bg = BG[background.upper()]
    else:
        bg = ""

    if color:
        c = COLORS[color.upper()]
    else:
        c = COLORS["WHITE"]

    return "%s%s%s%s%s%s" % (COLORS['RESTORE'],
                             c,
                             bg, ul, item,
                             COLORS['RESTORE'])


def hr(msg=None, color=None):
    print colorize("---------------------------------------------", color=color)
    if msg:
        print colorize("| %s" % msg, color=color)
        print colorize("---------------------------------------------", color=color)


def main():
    hr(msg="Just different Text colors", color="cyan")

    print "Red text, black background:"
    print colorize("Red text, black background:", "red")
    print "Green text, black background:"
    print colorize("Green text, black background:", "green")
    print "Yellow text, black background:"
    print colorize("Yellow text, black background:", "yellow")

    hr(msg="Text with backgrounds", color="cyan")

    print "White text, red background:"
    print colorize("White text, red background:", color="white", background="red")
    print "White text, green background:"
    print colorize("White text, green background:", color="white", background="green")
    print "Yellow text, lightgray background:"
    print colorize("Yellow text, lightgray background:", color="yellow", background="lightgray")

    hr(msg="Different text colors, with underlines", color="cyan")

    print "Red underlined text, black background:"
    print colorize("Red underlined text, black background:", "red", underline=True)
    print "Green underlined text, black background:"
    print colorize("Green underlined text, black background:", "green", underline=True)
    print "Yellow underlined text, black background:"
    print colorize("Yellow underlined text, black background:", "yellow", underline=True)

    hr("Underlined texts with backgrounds", color="cyan")

    print "White underlined text, red background:"
    print colorize("White underlined text, red background:", color="white", background="red", underline=True)
    print "White underlined text, green background:"
    print colorize("White underlined text, green background:", color="white", background="green", underline=True)
    print "Yellow underlined text, lightgray background:"
    print colorize("Yellow underlined text, lightgray background:", color="yellow", background="lightgray", underline=True)


if __name__ == '__main__':
    main()
