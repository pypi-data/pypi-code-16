# Copyright 2011 Robert Spanton
# 
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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from . import pcons
from .pcons import Pad
import sys

def output_pad( x1, y1, x2, y2, thickness, clearance, mask, name, square, paste, f = sys.stdout, opposite_side = False ):
    flags = []
    if square:
        flags.append("square")
    if not paste:
        flags.append("nopaste")
    if opposite_side:
        flags.append("onsolder")

    print ("""\tPad[ {x1:.6f}mm {y1:.6f}mm {x2:.6f}mm {y2:.6f}mm {thickness:.6f}mm {clearance:.6f}mm {mask:.6f}mm "{name}" "{name}" "{flags}"]""".format(
        x1=x1, y1=y1, x2=x2, y2=y2,
        thickness=thickness*2,
        clearance=clearance * 2,
        mask=mask + thickness*2,
        name=name,
        flags = ",".join(flags)), file=f)


def render_square_pad( pad, f = sys.stdout ):
    "pcb doesn't support square pads - so hack it with two rectangles"
    d = pad.tr.x.val - pad.bl.x.val
    assert d == (pad.bl.y.val - pad.tl.y.val)

    thickness = d / 4

    p1 = ( ( pad.tl.x.val + thickness, pad.tl.y.val + thickness ),
           ( pad.tr.x.val - thickness, pad.tl.y.val + thickness ) )

    p2 = ( ( pad.bl.x.val + thickness, pad.bl.y.val - thickness ),
           ( pad.br.x.val - thickness, pad.bl.y.val - thickness ) )

    for p in (p1, p2):
        output_pad( p[0][0], p[0][1], p[1][0], p[1][1],
                    thickness = thickness,
                    clearance = pad.clearance,
                    mask = pad.mask_clearance,
                    name = pad.name,
                    square = pad.square,
                    paste = pad.paste,
                    f = f,
                    opposite_side = pad.opposite_side)

def render_pad( pad, f = sys.stdout ):
    # Need to work out the longest dimension
    dims = ( pad.tr.x.val - pad.bl.x.val,
             pad.bl.y.val - pad.tl.y.val )

    if dims[0] > dims[1]:
        "Draw the pad in the x-direction"
        thickness = dims[1] / 2

        r1 = ( pad.bl.x.val + thickness,
               pad.bl.y.val - thickness )

        r2 = ( pad.br.x.val - thickness,
               pad.bl.y.val - thickness )

    elif dims[0] < dims[1]:
        "Draw the pad in the y-direction"
        thickness = dims[0] / 2

        r1 = ( pad.bl.x.val + thickness,
               pad.bl.y.val - thickness )

        r2 = ( pad.bl.x.val + thickness,
               pad.tr.y.val + thickness )
    else:
        render_square_pad(pad, f)
        return

    output_pad( r1[0], r1[1], r2[0], r2[1],
                thickness = thickness,
                clearance = pad.clearance,
                mask = pad.mask_clearance,
                name = pad.name,
                square = pad.square,
                paste = pad.paste,
                f = f,
                opposite_side = pad.opposite_side )

def render_circular_pad( pad, f=sys.stdout ):
    output_pad( pad.centre.x.val, pad.centre.y.val,
                pad.centre.x.val, pad.centre.y.val,
                thickness = pad.diam/2,
                clearance = pad.clearance,
                mask = pad.mask_clearance,
                name = pad.name,
                square = False,
                paste = True,
                f = f,
                opposite_side = pad.opposite_side )

def render_hole( hole, f = sys.stdout ):
    print ("""\tPin[ %smm %smm %smm %smm %smm %smm"" "" "hole"]""" % (
        hole.pos.x.val, hole.pos.y.val,
        hole.diameter,
        hole.clearance * 2, hole.mask_clearance + hole.diameter,
        hole.diameter + 0), file=f)

def render_pin( pin, f = sys.stdout ):
    print ("""\tPin[ %smm %smm %smm %smm %smm %smm "%s" "%s" ""]""" % (
        pin.centre.x.val, pin.centre.y.val,
        pin.pad_diameter,
        pin.clearance * 2,
        pin.mask_clearance + pin.pad_diameter,
        pin.hole_diameter,
        pin.name,
        pin.number ), file=f)

def render_silk_line( line, f = sys.stdout ):
    print ("""\tElementLine[ %smm %smm %smm %smm %smm ]""" % (
        line.start.x.val, line.start.y.val,
        line.end.x.val, line.end.y.val,
        line.thickness ), file=f)

def render_silk_circle( c, f = sys.stdout ):
    print ("""\tElementArc[ %smm %smm %smm %smm 0 360 %smm ]""" % (
        c.pos.x.val, c.pos.y.val,
        c.diameter/2, c.diameter/2,
        c.thickness ), file=f)

renderers = {
    pcons.Pad: render_pad,
    pcons.CircularPad: render_circular_pad,
    pcons.Pin: render_pin,
    pcons.Hole: render_hole,
    pcons.SilkLine: render_silk_line,
    pcons.SilkCircle: render_silk_circle,
    pcons.SilkRect: None,
}

def render( des, f = sys.stdout ):
    print ("""Element[0x00 "%s" "" "" 0 0 0 0 0 100 0x00000000]""" % des.desc, file=f)
    print ("(", file=f)

    for obj in des.ents:
        if hasattr(obj, "render"):
            obj.render(f)
        else:
            rendered = False
            for k,r in renderers.items():
                if isinstance( obj, k ):
                    if r != None:
                        r( obj, f )
                    rendered = True
                    break

            if not rendered:
                raise Exception("No renderer for object.")

    print (")", file=f)



