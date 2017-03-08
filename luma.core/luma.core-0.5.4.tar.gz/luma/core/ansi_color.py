# -*- coding: utf-8 -*-
# Copyright (c) 2017 Richard Hull and contributors
# See LICENSE.rst for details.

import re

valid_attributes = {
    # Text attributes
    0:   ["reset"],    # All attributes off
    1:   ["set_bold", True],     # Bold on
    2:   ["set_bold", False],     # Bold off
    7:   ["reverse_colors"],  # Reverse video on

    # Foreground colors
    30:  ["foreground_color", "black"],
    31:  ["foreground_color", "red"],
    32:  ["foreground_color", "green"],    # Green
    33:  ["foreground_color", "yellow"],   # Yellow
    34:  ["foreground_color", "blue"],     # Blue
    35:  ["foreground_color", "magenta"],  # Magenta
    36:  ["foreground_color", "cyan"],     # Cyan
    37:  ["foreground_color", "white"],    # White

    # Background colors
    40:  ["background_color", "black"],    # Black
    41:  ["background_color", "red"],      # Red
    42:  ["background_color", "green"],    # Green
    43:  ["background_color", "yellow"],   # Yellow
    44:  ["background_color", "blue"],     # Blue
    45:  ["background_color", "magenta"],  # Magenta
    46:  ["background_color", "cyan"],     # Cyan
    47:  ["background_color", "white"],    # White
}


def parse_str(text):
    prog = re.compile('^\033\[(\d+(;\d+)*)m')
    text = str(text)

    while text != "":
        result = prog.match(text)
        print(text, result)
        if result:
            for code in result.group(1).split(";"):
                directive = valid_attributes.get(int(code), None)
                if directive:
                    yield directive
            n = len(result.group(0))
            text = text[n:]
        else:
            yield ["putch", text[0]]
            text = text[1:]
