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
from decimal import Decimal as D
X, Y = 0, 1

class Val(object):
    "A value"
    def __init__(self, val = None):
        self.val = val

    def __repr__(self):
        return str(self.val)

class Point:
    "A point in space"
    def __init__(self, pos = None):
        if pos == None:
            self.pos = ( Val(), Val() )
        else:
            self.pos = pos

    @property
    def x(self):
        "x co-ordinate"
        return self.pos[X]

    @x.setter
    def x(self, val):
        self.pos[X] = val

    @property
    def y(self):
        "y co-ordinate"
        return self.pos[Y]

    @y.setter
    def y(self, val):
        self.pos[Y] = val

    def __repr__(self):
        return """Point( %s )""" % ( str(self.pos) )

class FixedDist(object):
    "Represents a fixed distance constraint between two values"

    def __init__(self, sep, v1, v2):
        "Constrain so that v2 = v1 + sep"
        self.sep = sep
        self.v = (v1,v2)

    def resolvable(self):
        "Return True is it's possible to resolve this"
        if self.v[0].val != None or self.v[1].val != None:
            "We can do something if they're both not None"
            return True

        return False

    def resolve(self):
        "Attempt to resolve this constraint"

        if not self.resolvable():
            "Cannot be satisfied at this time"
            return False

        if self.v[0].val != None and self.v[1].val != None:
            "Both values are already set"

            if self.v[0].val + self.sep != self.v[1].val:
                "This constraint has not been satisfied"
                raise Exception("Unsatisfiable constraint")

            # Contraint already satisfied
            return True

        if self.v[0].val != None:
            self.v[1].val = self.v[0].val + self.sep
        else:
            self.v[0].val = self.v[1].val - self.sep

        return True

class Centred(object):
    "Centres a point between two other points"

    def __init__(self, p, del1, del2, axis):
        "Constrain p to be halfway between del1 and del2 in axis"
        assert axis in (X,Y)
        self.p = p.pos[axis]
        self.del1 = del1.pos[axis]
        self.del2 = del2.pos[axis]

    def resolvable(self):
        "Return True if it's possible to resolve this"
        vals = [ self.del1.val,
                 self.del2.val,
                 self.p.val ]

        if vals.count(None) == 1:
            "At least two things are defined, so we can do something"
            return True

        return False

    def resolve(self):
        "Attempt to resolve this constraint"

        if not self.resolvable():
            "Cannot be satisfied at this time"
            return self.resolvable()

        if self.p.val is None:
            self.p.val = (self.del1.val + self.del2.val) / 2
            return True

        if self.del1.val is None:
            self.del1.val = self.p.val - (self.del2.val - self.p.val)
            return True

        if self.del2.val is None:
            self.del2.val = self.p.val - (self.del1.val - self.p.val)
            return True

        # None of the points are None
        # Check that this is satisfied
        if (self.del2.val - self.p.val) != (self.p.val - self.del1.val):
            "This constraint has not been satisfied"
            raise Exception("Unsatisfiable constraint")

        return True
                

def Align( points, axis ):
    "Align all the given items in the specified axis"
    assert axis in (X,Y)
    c = []

    for p in points[1:]:
        c.append( FixedDist( D(0),
                             points[0].pos[axis],
                             p.pos[axis] ) )
    return c

class UnconstrainedPad(object):
    "A pad with no built-in constraints"
    def __init__(self, name,
                 clearance = 0,
                 mask_clearance = 0,
                 square = True,
                 paste = True,
                 opposite_side = False):
        self.cons = []
        self.name = name
        self.clearance = clearance
        self.mask_clearance = mask_clearance
        self.square = square
        self.paste = paste
        self.opposite_side = opposite_side

        # Initialise with four unknown corner points
        self.bl, self.br, self.tl, self.tr = [ Point( (Val(), Val()) ) for x in range(0,4) ]

class Pad(UnconstrainedPad):
    "A rectangular pad"
    def __init__(self, size, name,
                 clearance = 0,
                 mask_clearance = 0,
                 square = True,
                 paste = True,
                 opposite_side = False):
        UnconstrainedPad.__init__(self, name,
                                  clearance, mask_clearance,
                                  square, paste, opposite_side)
        # Constrain corners to be in-line
        self.cons.append( FixedDist( D(0), self.bl.x, self.tl.x ) )
        self.cons.append( FixedDist( D(0), self.br.x, self.tr.x ) )
        self.cons.append( FixedDist( D(0), self.bl.y, self.br.y ) )
        self.cons.append( FixedDist( D(0), self.tl.y, self.tr.y ) )

        # Space left-hand-side from right
        self.cons.append( FixedDist( size[X], self.bl.x, self.br.x ) )
        # Space top from bottom
        self.cons.append( FixedDist( size[Y], self.tl.y, self.bl.y ) )

        # Add a centre point
        self.centre = Point( (Val(), Val()) )
        # And put it in the centre
        self.cons.append( FixedDist( size[X]/2, self.bl.x, self.centre.x ) )
        self.cons.append( FixedDist( size[Y]/2, self.tl.y, self.centre.y ) )

    def __repr__(self):
        return "Pad( %s, %s, %s, %s )" % ( self.bl, self.br, self.tr, self.tl )

class CircularPad(object):
    "A circular pad"
    def __init__(self, diam, name,
                 clearance = 0,
                 mask_clearance = 0,
                 opposite_side = False):
        self.cons = []
        self.diam = diam
        self.name = name
        self.clearance = clearance
        self.mask_clearance = mask_clearance
        self.opposite_side = opposite_side
        self.centre = Point( (Val(), Val()) )

    def __repr__(self):
        return "CircularPad( %s )" % self.centre

class Hole(object):
    "A hole in the PCB"
    def __init__( self, diameter,
                  clearance = 0, mask_clearance = 0 ):
        self.diameter = diameter
        self.pos = Point( (Val(), Val()) )
        self.clearance = clearance
        self.mask_clearance = mask_clearance

    def __repr__(self):
        return "Hole( %s )" % self.pos

class Pin(object):
    "A pin (i.e. a hole with a pad)"
    def __init__( self, name, number,
                  hole_diameter, pad_diameter,
                  clearance = 0, mask_clearance = 0 ):
        self.name = name
        self.number = number
        self.hole_diameter = hole_diameter
        self.pad_diameter = pad_diameter
        self.centre = Point( (Val(), Val()) )
        self.clearance = clearance
        self.mask_clearance = mask_clearance

    def __repr__(self):
        return "Pin( %s )" % self.centre

class SilkLine(object):
    "A line on the silkscreen"
    def __init__( self, thickness ):
        self.thickness = thickness
        self.start = Point( (Val(), Val()) )
        self.end = Point( (Val(), Val()) )

class SilkCircle(object):
    "A circle on the silkscreen"
    def __init__( self, thickness, diameter ):
        self.thickness = thickness
        self.diameter = diameter
        self.pos = Point()

class SilkRect(object):
    "A silkscreen rectangle made of four lines"
    def __init__( self, thickness ):
        self.thickness = thickness
        self.lines = [ SilkLine(thickness) for x in range(0,4) ]
        # Some things for convenience
        self.t, self.b, self.r, self.l = self.lines
        self.bl = self.b.start
        self.br = self.b.end
        self.tl = self.t.start
        self.tr = self.t.end

        self.cons = []

        # Align everything we can
        self.cons += Align( ( self.t.start,
                              self.l.start, self.l.end,
                              self.b.start ), X )

        self.cons += Align( ( self.t.end,
                              self.r.start, self.r.end,
                              self.b.end ), X )

        self.cons += Align( ( self.t.start, self.t.end,
                              self.l.end,
                              self.r.end ), Y )

        self.cons += Align( ( self.b.start, self.b.end,
                              self.l.start,
                              self.r.start ), Y )

# The origin
O = Point( (Val(0),Val(0)) )

class Design(object):
    def __init__(self, desc):
        self.desc = desc

        # Constraints
        self.cons = []

        # Entities
        self.ents = []

        self.clearance = D("0.2")
        self.mask_clearance = D("0.1")

    def set_origin(self, point):
        self.cons.append( FixedDist( 0, point.x, O.x ) )
        self.cons.append( FixedDist( 0, point.y, O.y ) )

    def add_hole(self, diam,
                 clearance = None, mask_clearance = None ):
        if clearance == None:
            clearance = self.clearance
        if mask_clearance == None:
            mask_clearance = self.mask_clearance

        hole = Hole(diam, clearance = clearance, mask_clearance = mask_clearance)
        self.ents.append(hole)
        return hole

    def add_pad( self, size, name,
                 clearance = None,
                 mask_clearance = None,
                 square = True,
                 paste = True,
                 opposite_side = False):

        if clearance == None:
            clearance = self.clearance
        if mask_clearance == None:
            mask_clearance = self.mask_clearance

        pad = Pad( size, name,
                   clearance = clearance,
                   mask_clearance = mask_clearance,
                   square = square,
                   paste = paste,
                   opposite_side = opposite_side)
        self.ents.append(pad)
        return pad

    def add_circular_pad( self, diam, name,
                          clearance = None,
                          mask_clearance = None,
                          opposite_side = False):

        if clearance == None:
            clearance = self.clearance
        if mask_clearance == None:
            mask_clearance = self.mask_clearance

        pad = CircularPad( diam, name,
                           clearance = clearance,
                           mask_clearance = mask_clearance,
                           opposite_side = opposite_side)
        self.ents.append(pad)
        return pad

    def add_pin( self, name, number,
                 hole_diameter, pad_diameter,
                 clearance = None, mask_clearance = None ):

        if clearance is None:
            clearance = self.clearance
        if mask_clearance is None:
            mask_clearance = self.mask_clearance

        pin = Pin( name, number,
                   hole_diameter, pad_diameter,
                   clearance, mask_clearance )

        self.ents.append(pin)
        return pin

    def add_pin_array(self, hole_diameter, pad_diameter,
                      numbers, direction, pitch,
                      clearance = None, mask_clearance = None):
        pins = [self.add_pin(str(number), number,
                             hole_diameter, pad_diameter,
                             clearance, mask_clearance) for number in numbers]

        if direction == X:
            perp = Y
        else:
            perp = X

        for i in range(0, len(pins)-1):
            # Sort out the pitch
            self.cons += [ FixedDist( pitch,
                                      pins[i].centre.pos[direction],
                                      pins[i+1].centre.pos[direction] ) ]

        # Align them all in the perpendicular axis
        self.cons += Align( [p.centre for p in pins], perp )

        return pins

    def add_pad_array( self, pad_size, names, direction, pitch,
                       clearance = None, mask_clearance = None, square = True,
                       opposite_side = False):

        try:
            pad_sizes = [(x[0], x[1]) for x in pad_size]
        except TypeError:
            pad_sizes = [pad_size for x in names]

        pads = []
        for n in range(len(names)):
            name = names[n]
            pad_size = pad_sizes[n]

            pads.append(self.add_pad( pad_size, name,
                                      clearance = clearance,
                                      mask_clearance = mask_clearance,
                                      square = square,
                                      opposite_side = opposite_side ))

        if direction == X:
            perp = Y
        else:
            perp = X

        for i in range(0, len(pads)-1):
            # Sort out the pitch
            self.cons += [ FixedDist( pitch,
                                      pads[i].bl.pos[direction],
                                      pads[i+1].bl.pos[direction] ) ]

        # Align them all in the perpendicular axis
        self.cons += Align( [p.bl for p in pads], perp )

        return pads

    def add_circular_pad_array( self, diam, names, direction, pitch,
                                clearance = None, mask_clearance = None,
                                opposite_side = False):
        pads = [ self.add_circular_pad( diam, name,
                                        clearance = clearance,
                                        mask_clearance = mask_clearance,
                                        opposite_side = opposite_side) for name in names ]

        if direction == X:
            perp = Y
        else:
            perp = X

        for i in range(0, len(pads)-1):
            # Sort out the pitch
            self.cons += [ FixedDist( pitch,
                                      pads[i].centre.pos[direction],
                                      pads[i+1].centre.pos[direction] ) ]

        # Align them all in the perpendicular axis
        self.cons += Align( [p.centre for p in pads], perp )

        return pads

    def add_point_array(self, num_x, num_y, spacing_x, spacing_y):
        points = []
        for x in range(num_x):
            col = []
            for y in range(num_y):
                col.append(Point())

                if len(col) > 1:
                    self.cons += [FixedDist(spacing_y, col[-2].y, col[-1].y)]
                    self.cons += Align([col[-1], col[-2]], X)

            points.append(col)
            if len(points) > 1:
                self.cons += [FixedDist(spacing_x, points[-2][0].x, points[-1][0].x)]
                self.cons += Align((points[-1][0], points[-2][0]),Y)

        return points

    def add_silk_circle( self, thickness, diameter ):
        c = SilkCircle( thickness, diameter )
        self.ents.append( c )
        
        return c

    def add_silk_line( self, thickness ):
        l = SilkLine( thickness )
        self.ents.append( l )

        return l

    def add_silk_rect( self, thickness ):
        "Add a silk rectangle.  Returns the four lines "
        r = SilkRect( thickness )
        self.ents += r.lines
        self.ents += [r]
        return r

    def _filter_obj_cons(self, t):
        "Filter the constraints out of a list of objects"
        cons = []

        for i in t:
            try:
                cons += i.cons
            except AttributeError:
                pass
        return cons
        
    def resolve(self):
        unsat = []
        unsat += self.cons
        unsat += self._filter_obj_cons(self.ents)

        satisfied = []
        solved = 1

        while solved > 0 and len(unsat):
            "Loop until there are no more soluble constraints"
            sat = []

            for c in unsat:
                if c.resolve():
                    "Constraint solved"
                    sat.append(c)

            solved = len(sat)
            for c in sat:
                satisfied.append(c)
                unsat.remove(c)

        return len(unsat)
