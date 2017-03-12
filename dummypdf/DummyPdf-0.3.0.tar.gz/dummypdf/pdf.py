#!/usr/bin/env python3

# Copyright Louis Paternault 2011-2015
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>. 1

"""PDF generation."""

from reportlab.lib import colors
from reportlab.pdfgen import canvas
import papersize

from dummypdf import errors

LINEWIDTH = 5

# Very very approximate size of a "Times-Roman" digit, in font 1
CHARWIDTH = 0.497923228
CHARHEIGHT = 0.704205709

def shift(coordinate):
    """Shift line coordinate.

    If we do not do that, half of lines are printed outside the page.
    """
    if coordinate == 0:
        return LINEWIDTH // 2
    else:
        return coordinate - LINEWIDTH // 2

def fontsize(pagenumber, paperwidth, paperheight):
    """Return the font size to be used to display page numbers."""
    if papersize.is_portrait(paperwidth, paperheight):
        size = int(paperheight/(3*CHARHEIGHT))
    else:
        size = int(paperheight/(2*CHARHEIGHT))
    charnumber = max(0, len(str(pagenumber)))
    if charnumber*CHARWIDTH*size > 0.9 * paperwidth:
        size = int(0.9 * paperwidth / (charnumber * CHARWIDTH))
    return size

def generate(name, first, color, paperformat):
    """Generate the pdf.

    Arguments:
    - name: file name
    - first: number of first page
    - color: line colors, as a list of three colors (RGB, from 0 to 255) or a
      named color recognisez by reportlab.
    - paperformat: list of paper formats, as tuples of dimensions.
    """
    # pylint: disable=too-many-locals
    pdf = canvas.Canvas(name)

    if isinstance(color, list):
        red, green, blue = color
        def set_line_color():
            """Set color of lines, using RGB color"""
            pdf.setFillColorRGB(red/255, green/255, blue/255)
            pdf.setStrokeColorRGB(red/255, green/255, blue/255)
    elif isinstance(color, str):
        def set_line_color():
            """Set color of lines, using named color"""
            pdf.setFillColor(getattr(colors, color))
            pdf.setStrokeColor(getattr(colors, color))

    pagenumber = first
    for pagewidth, pageheight in paperformat:
        # Set page size
        pdf.setPageSize((pagewidth, pageheight))

        # Draw lines
        set_line_color()
        pdf.setLineWidth(LINEWIDTH)
        for x1, y1, x2, y2 in [ # pylint: disable=invalid-name
                (0, 0, pagewidth, 0),
                (pagewidth, 0, pagewidth, pageheight),
                (pagewidth, pageheight, 0, pageheight),
                (0, pageheight, 0, 0),
            ]:
            pdf.line(
                shift(x1),
                shift(y1),
                shift(x2),
                shift(y2),
                )
        pdf.line(pagewidth, pageheight, 0, 0)
        pdf.line(pagewidth, 0, 0, pageheight)

        # Drawing text
        pdf.setFont("Times-Roman", fontsize(pagenumber, pagewidth, pageheight))
        pdf.setFillColor(colors.lightgrey)
        pdf.drawCentredString(
            pagewidth//2,
            pageheight//2-0.33*fontsize(pagenumber, pagewidth, pageheight),
            str(pagenumber),
            )

        # Next page
        pagenumber += 1
        pdf.showPage()

    pdf.setAuthor("Generated using dummypdf — http://git.framasoft.org/spalax/dummypdf")
    pdf.setTitle("Dummy pdf")
    pdf.save()

def get_color(name=None):
    """Return color names.

    If name is None, return the list of available colors (as strings).
    If name is a string, return the string if this color exists; raises an
    error otherwise.
    """
    available = [color for color in dir(colors) if isinstance(getattr(colors, color), colors.Color)]
    if name is None:
        return available
    elif name in available:
        return name
    else:
        raise errors.ArgumentError(
            "No such color '{}'. See help for the list of available colors."
            .format(name))
