#
# Copyright 2023 Universidad Complutense de Madrid
#
# This file is part of RepDoc
#
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSE.txt
#


def ctext(s=None,
          fg=None,
          bg=None,
          under=False,
          rev=False,
          bold=False):
    """Return coloured string using ANSI Escape Sequences

    See ANSI Escape values in:
    https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797

    Parameters
    ----------
    s : object
        Object to be displayed
    fg : str
        Foreground colour.
    bg : str
        Background colour.
    under : bool
        If True, add underline style.
    rev : bool
        If True, add reverse style.
    bold : bool
        If True, add bold style

    """

    colour = {
        'black': 0,
        'red': 1,
        'green': 2,
        'yellow': 3,
        'blue': 4,
        'magenta': 5,
        'cyan': 6,
        'white': 7,
        'default': 9,
        'reset': 0
    }

    if s is None:
        print(f'Available colours: {list(colour.keys())}')
        return

    # foreground
    if fg is not None:
        fg = fg.lower()
        if fg not in colour:
            raise ValueError(f'Unexpected foreground colour: {fg}')

    # background
    if bg is not None:
        bg = bg.lower()
        if bg not in colour:
            raise ValueError(f'Unexpected background colour: {bg}')

    style_list = []
    if under:
        style_list.append('\x1B[4m')
    if rev:
        style_list.append('\x1B[7m')
    if bold:
        style_list.append('\x1B[1m')

    if fg is not None:
        style_list.append(f'\x1B[3{colour[fg]}m')

    if bg is not None:
        style_list.append(f'\x1B[4{colour[bg]}m')

    final_style = ''.join(style_list)

    return f'{final_style}{s}\x1B[0m'
