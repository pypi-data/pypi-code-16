import argparse
import os
import sys

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

# Our vendored TermEmulator from https://github.com/sivachandran/TermEmulator
import TermEmulator as te

_COLORS = {
    1: (0, 0, 0),
    2: (255, 0, 0),
    3: (0, 255, 0),
    4: (255, 255, 0),
    5: (0, 0, 255),
    6: (255, 0, 255),
    7: (0, 255, 255),
    8: (255, 255, 255),
}


def term2image(infile, outfile):
    buf = infile.read()
    infile.close()

    cols = 120
    font_size = 16
    rows = buf.count(b'\n')
    term = te.V102Terminal(rows=rows, cols=cols)
    term.ProcessInput(buf)
    screen = term.GetRawScreen()

    regular = ImageFont.truetype("Courier New.ttf", font_size)
    font_width, font_height = regular.getsize('E')
    margin_left = font_width

    bold = ImageFont.truetype("Courier New Bold.ttf", font_size)

    # No, I don't know why we need this adjustment.
    img = Image.new('RGB',
                    (int(cols * font_width * 0.7), rows * font_height),
                    'white')

    draw = ImageDraw.Draw(img)

    for row, line in enumerate(screen):
        for col, c in enumerate(line):
            font = regular
            fill = 'black'

            style, fgcolor, bgcolor = term.GetRendition(row, col)
            if style & term.RENDITION_STYLE_BOLD:
                font = bold

            if style & term.RENDITION_STYLE_UNDERLINE:
                fill = 'red'

            draw.text((col * font_width + margin_left, row * font_height),
                      c, fill, font)

    img.save(outfile)


def main():
    parser = argparse.ArgumentParser(
        description="Convert terminal command output to an image")

    parser.add_argument('-i', '--infile', type=argparse.FileType('r'),
                        default='-', required=False)
    parser.add_argument('-o', '--outfile', type=argparse.FileType('wb'))
    opts, args = parser.parse_known_args()
    if len(args) > 1 or args and opts.infile is not sys.stdin:
        parser.error("too many arguments")

    if args:
        opts.infile = open(args[0], 'r')

    if not opts.outfile:
        if opts.infile is sys.stdin:
            parser.error("--outfile is required when reading from stdin")

        path, _ = os.path.splitext(opts.infile.name)
        opts.outfile = '%s.png' % path
    else:
        _, ext = os.path.splitext(opts.outfile.name)
        if not ext:
            parser.error(
                'bad outfile "%s", it must have an extension like ".png"' % (
                    opts.outfile.name))

    term2image(opts.infile, opts.outfile)
