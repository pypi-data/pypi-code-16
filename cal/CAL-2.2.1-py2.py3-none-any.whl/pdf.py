# -*- coding: utf-8 -*-
# Copyright (C) 2003-2014 Mag. Christian Tanzer. All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    CAL.pdf
#
# Purpose
#    Create pdf file of calendar with appointments
#
# Revision Dates
#    18-Apr-2003 (CT) Creation
#    20-Apr-2003 (CT) `is_holiday` added
#     1-Jan-2004 (CT) `PDF_Plan_L` and `-landscape` added
#     1-Jan-2004 (CT) `_cooked` added and used
#    19-Dec-2004 (CT) Small fixes to make it work again
#    25-Dec-2005 (CT) Default for `pdf_name` computed dynamically (otherwise
#                     it defaults to the current, not the specified `year`)
#    25-Dec-2005 (CT) Deprecation warnings killed (`/` --> `//`)
#    25-Dec-2005 (CT) `line_generator` de-obfuscated
#    25-Dec-2005 (CT) Options `xl` and `yl` added
#     4-Jan-2007 (CT) Removed stale __future__  import of `generators`
#     4-Jan-2007 (CT) Pass `default_to_now = True` to `Date`
#     6-Jan-2007 (CT) Options `xo` and `yo` added
#    11-Aug-2007 (CT) Imports corrected
#    22-Dec-2007 (CT) Color added
#    12-Feb-2008 (CT) Use current version of reportlab.pdfgen
#                     (instead of ancient one named pdfgen)
#    12-Feb-2008 (CT) Refactored, `PDF_Plan_Month` started
#    13-Feb-2008 (CT) `PDF_Plan_Month` finished
#     8-Dec-2009 (CT) 3-compatibility (tuple parameter unpacking)
#    16-Jun-2010 (CT) Encode holiday names with `TFL.I18N.Config.encoding`
#    16-Jun-2010 (CT) Use `CAO` instead of `Command_Line`
#    17-Jun-2010 (CT) Use `TFL.I18N.encode_o` instead of home-grown code
#     5-Feb-2011 (CT) `PDF_Plan_Year` added
#    12-Feb-2013 (CT) Change `PDF_Plan_Month.one_day` to show single appointment
#    ««revision-date»»···
#--

from   _TFL           import TFL
from   _CAL           import CAL

from   _TFL.Filename  import *
from   _TFL.predicate import *
from   _TFL.pyk       import pyk
from   _TFL.Regexp    import *
from   _TFL           import sos

import _TFL._Meta.Object
import _TFL.CAO
import _TFL.defaultdict

import _CAL.Plan
import _CAL.Year
import _CAL.Date

class PDF_P (TFL.Meta.Object) :

    inch   = INCH = 72
    cm     = inch / 2.54
    mm     = 0.1 * cm

    wpx    = 2
    wpy    = 2
    xsiz   = 21.0 * cm
    ysiz   = 29.7 * cm
    xo     = 0.5  * cm
    xof    = 1.0
    yo     = 0.5  * cm
    yof    = 1.0
    ts     = 30
    lw     = 1.0
    font   = "Helvetica"
    black  = 0.000, 0.000, 0.000
    blue   = 0.285, 0.668, 0.902
    dark   = 0.400, 0.400, 0.400
    gray   = 0.700, 0.700, 0.700
    holi   = 0.902, 0.902, 1.000
    light  = 0.875, 0.875, 0.875
    orange = 1.000, 0.627, 0.133
    white  = 1.000, 1.000, 1.000

# end class PDF_P

class PDF_L (PDF_P) :

    cm     = PDF_P.cm
    wpx    = 3
    wpy    = 1
    xsiz   = 29.7 * cm
    ysiz   = 21.0 * cm
    xo     = 0.9  * cm

# end class PDF_L

class PDF_Plan (PDF_P) :

    ac_map = TFL.defaultdict \
        ( lambda : None
        , O      = PDF_P.orange
        )

    def __init__ ( self, Y, filename, first_unit, last_unit
                 , linewidth  = 0.6, xl = None, yl = None, xo = None, yo = None
                 ) :
        from reportlab.pdfgen.canvas import Canvas
        self.Y          = Y
        self.filename   = filename
        self.first_unit = first_unit
        self.last_unit  = last_unit
        self.linewidth  = linewidth
        if xo :
            self.xo     = xo * self.cm
        if yo :
            self.yo     = yo * self.cm
        if xl :
            self.xl     = xl * self.cm
        else :
            self.xl     = (self.xsiz - self.xo) / self.wpx
        if yl :
            self.yl     = yl * self.cm
        else :
            self.yl     = (self.ysiz - self.yo) / self.wpy
        self.canvas = c = Canvas (filename, pagesize = (self.xsiz, self.ysiz))
        self.pager  = p = self.page_generator (c)
        c.setPageCompression (0)
        c.setLineJoin        (2)
        c.setFillColorRGB    (* self.gray)
        self.generate_pdf    (Y, p, self.wpx * self.wpy)
        c.save               ()
    # end def __init__

    def draw_line (self, c, x1, y1, x2, y2, color, width = None) :
        c.setLineWidth      (width or self.linewidth)
        c.setStrokeColorRGB (* color)
        c.line              (x1, y1, x2, y2)
    # end def draw_line

    def draw_rect (self, c, x, y, w, h, color) :
        c.setFillColorRGB (* color)
        c.rect            (x, y, w, h, stroke = False, fill = True)
    # end def draw_rect

    def draw_text (self, c, x, y, txt, color, right = False) :
        drawer = (c.drawString, c.drawRightString) [right]
        c.setFillColorRGB (* color)
        drawer            (x, y, self._cooked (txt))
    # end def draw_text

    def generate_pdf (self, Y, pager, wpp) :
        for w in self.seq_generator (self.first_unit, self.last_unit, wpp) :
            page = next (pager)
            if w is not None :
                self.one_unit (Y, w, page)
    # end def generate_pdf

    def line_generator (self, ds, x, xl, y, ts) :
        lines = int (ds / (ts + 2))
        yo    = y + ds - ts - 1
        ys    = [(yo - (l * (ts + 1))) for l in range (lines)]
        for xo in [x, x + xl // 2] :
            for yo in ys :
                yield xo + 0.1 * self.cm, yo + 1
    # end def line_generator

    def page_generator (self, c) :
        xo = self.xo
        yo = self.yo
        xl = self.xl
        yl = self.yl
        xd = xl - xo * self.xof
        yd = yl - yo * self.yof
        ds = (yl - self.yo - 1 * self.cm) / self.dpu
        xs = [(xo + i * xl) for i in range (self.wpx)]
        ys = [(yo + i * yl) for i in range (self.wpy)]
        ys.reverse ()
        while True :
            for y in ys :
                for x in xs :
                    yield (x, x + xd), (y + 0.3, y + 0.3 + yd), ds
            c.showPage ()
    # end def page_generator

    def seq_generator (self, first, last, wpp) :
        s, r   = divmod (last - first, wpp)
        stride = s + (r > 0)
        for w in range (first, first + stride) :
            for i in range (wpp) :
                d = i * stride
                if w + d < last :
                    yield w + d
                else :
                    yield None
    # end def seq_generator

    def _cooked (self, text) :
        return pyk.text_type (text, "utf-8", "replace")
    # end def _cooked

# end class PDF_Plan

class PDF_Plan_Month (PDF_Plan) :

    dpu      = 31
    dark     = 0.500, 0.500, 0.500
    darker   = 0.400, 0.400, 0.400
    head_fmt = "%B %Y"
    rjd_fmt  = "[%d-%d]"

    def __init__ (self, Y, filename, first_month = 1, last_month = 12, ** kw) :
        self.__super.__init__ (Y, filename, first_month, last_month + 1, ** kw)
    # end def __init__

    def one_day (self, c, d, ds, x, xl, y, yl, font, ts, cm, mm) :
        xo = x + 0.10 * cm
        yo = y + 0.15 * cm
        lw = self.linewidth
        hd = d.is_holiday or ""
        if hd :
            hd = TFL.I18N.encode_o (hd)
        if d.weekday == 6 : ### it's a sunday
            self.draw_rect (c, x + lw, y, xl - x - lw, ds - lw, self.light)
        elif hd :
            self.draw_rect (c, x + lw, y, xl - x - lw, ds - lw, self.holi)
        if d.day == 1 or d.weekday == 0 : ### it's a monday (or the first)
            self.draw_text (c, xl, yo, "%2.2d" % d.week, self.gray, True)
        self.draw_line (c, x, y, xl, y, self.dark)
        self.draw_text (c, xo, yo, d.formatted ("%A") [:2], self.dark)
        self.draw_text (c, xo + 0.4 * cm, yo, d.formatted ("%d"), self.darker)
        if hd :
            self.draw_text (c, xo + 0.8 * cm, yo, hd, self.blue)
        apps = getattr (d, "appointments", [])
        if len (apps) == 1 :
            app = apps [0]
            xa  = xl - 0.4 * cm
            txt = app.activity [:35 - len (hd) - (5 if hd else 0)]
            col = self.ac_map [app.prio]
            if col :
                self.draw_text (c, xa, yo, txt, col, right = True)
    # end def one_day

    def one_unit (self, Y, n, spec) :
        ((x, xl), (y, yl), ds) = spec
        m    = Y.months [n - 1]
        c    = self.canvas
        cm   = self.cm
        dpu  = self.dpu
        font = self.font
        mm   = self.mm
        ts   = self.ts
        yd   = (self.dpu - len (m.days)) * ds
        self.draw_line (c, x, y + yd, x, yl - 1 * cm, self.dark)
        y = y + dpu * ds
        self.draw_line (c, x, y, xl, y, self.dark)
        c.setFont (font, ts // 2)
        txt = m.head.formatted (self.head_fmt)
        self.draw_text (c, x + 0.1 * cm, y + 0.2 * cm, txt, self.blue)
        c.setFont (font, ts // 5)
        if self.rjd_fmt :
            txt = self.rjd_fmt % (m.head.rjd, m.tail.rjd)
            self.draw_text (c, xl, y + 0.2 * cm, txt, self.gray, True)
        for d in m.days :
            y -= ds
            self.one_day (c, d, ds, x, xl, y, yl, font, ts, cm, mm)
    # end def one_unit

# end class PDF_Plan_Month

class PDF_Plan_Week (PDF_Plan) :

    dpu = 7

    def __init__ (self, Y, filename, first_unit = 0, last_unit = -1, ** kw) :
        if last_unit < 0 :
            last_unit  += len (Y.weeks) + 1
        self.__super.__init__ (Y, filename, first_unit, last_unit, ** kw)
    # end def __init__

    def one_day (self, c, d, ds, x, xl, y, yl, font, ts, cm, mm) :
        xo = xl - 0.2 * cm
        c.setFont      (font, ts)
        self.draw_line (c, x, y, xl, y, self.dark)
        self.draw_text \
            (c, xo, y + ds * 0.95 - ts, d.formatted ("%d"), self.gray, True)
        c.setFont      (font, ts // 5)
        self.draw_text (c, xo, y + mm,  d.formatted ("%A"), self.dark, True)
        lg = self.line_generator (ds, x, xo - 0.15 * (xl - x), y, ts // 5)
        hd = d.is_holiday
        if hd :
            hd = TFL.I18N.encode_o (hd)
        if hd :
            next (lg)
            xo, yo = next  (lg)
            c.setFont      (font, ts // 2)
            self.draw_text (c, xo, yo, hd [:20], self.blue)
            c.setFont      (font, ts // 5)
        for a in getattr (d, "appointments", []) :
            try :
                 xo, yo = next (lg)
            except StopIteration :
                break
            txt = ("%s %s" % (a.time or ">", a.activity)) [:40]
            self.draw_text (c, xo, yo, txt, self.gray)
    # end def one_day

    def one_unit (self, Y, n, spec) :
        ((x, xl), (y, yl), ds) = spec
        w    = Y.weeks [n]
        c    = self.canvas
        cm   = self.cm
        dpu  = self.dpu
        font = self.font
        mm   = self.mm
        ts   = self.ts
        c.setFont      (font, ts // 2)
        self.draw_line (c, x, y, x, yl - 1 * cm, self.dark)
        y += dpu * ds
        self.draw_line (c, x, y, xl, y, self.dark)
        self.draw_text \
            (c, x  + 0.2 * cm, y + 0.2 * cm, "Week %2.2d" % w.number, self.blue)
        if w.mon.month == w.sun.month :
            m_head = w.mon.formatted ("%B %Y")
        else :
            if w.mon.year == w.sun.year :
                mon_format = "%b"
            else :
                mon_format = "%b %Y"
            m_head = "%s/%s" % \
                (w.mon.formatted (mon_format), w.sun.formatted ("%b %Y"))
        self.draw_text (c, xl - 0.2 * cm, y + 0.2 * cm, m_head, self.blue, True)
        for d in w.days :
            y -= ds
            self.one_day (c, d, ds, x, xl, y, yl, font, ts, cm, mm)
    # end def one_unit

# end class PDF_Plan_Week

class PDF_Plan_Year (PDF_Plan_Month) :

    xo       = 0.25 * PDF_P.cm
    xof      = 0.25
    yo       = 0.25 * PDF_P.cm
    wpx      = 6
    wpy      = 2
    head_fmt = "%b %Y"

    def seq_generator (self, first, last, wpp) :
        for w in range (first, last) :
            yield w
    # end def seq_generator

# end class PDF_Plan_Year

class PDF_Plan_Month_L (PDF_L, PDF_Plan_Month) :

    pass

# end class PDF_Plan_Month_L

class PDF_Plan_Week_L (PDF_L, PDF_Plan_Week) :

    pass

# end class PDF_Plan_Week_L

class PDF_Plan_Year_L (PDF_L, PDF_Plan_Year) :

    xo       = 0.25 * PDF_P.cm
    yo       = 0.25 * PDF_P.cm
    wpx      = 6
    wpy      = 1

# end class PDF_Plan_Year_L

def _main (cmd) :
    year      = cmd.year
    head      = cmd.head
    tail      = cmd.tail
    path      = sos.path.join (sos.expanded_path (cmd.diary), "%4.4d" % year)
    Y         = CAL.Year  (year)
    file_name = sos.path.join (path, cmd.filename)
    pdf_name  = Filename (cmd.pdf or ("plan_%s.pdf" % year), ".pdf").name
    head      = cmd.head or 1
    tail      = cmd.tail or 12
    if cmd.monthly :
        Plan  = [PDF_Plan_Month, PDF_Plan_Month_L] [bool (cmd.landscape)]
    elif cmd.Yearly :
        Plan  = [PDF_Plan_Year, PDF_Plan_Year_L] [bool (cmd.landscape)]
    else :
        Plan  = [PDF_Plan_Week, PDF_Plan_Week_L] [bool (cmd.landscape)]
        head  = cmd.head or 0
        tail  = cmd.tail or -1
        wd    = Y.weeks [0].number
        if tail < 0 :
            tail += len (Y.weeks)
        head -= wd
        tail += 1 - wd
    CAL.read_plan (Y, file_name)
    Plan \
        ( Y, pdf_name, head, tail
        , xl  = cmd.XL
        , yl  = cmd.YL
        , xo  = cmd.XO
        , yo  = cmd.YO
        )
# end def _main

_Command = TFL.CAO.Cmd \
    ( handler     = _main
    , opts        =
        ( "diary:S=~/diary?Path for calendar file"
        , "filename:S=plan?Filename of plan for `year`"
        , "head:I?Number of first week/month to process"
        , "landscape:B?Print in landscape format"
        , "monthly:B?Generate monthly instead of weekly sheets"
        , "pdf:S=?Generate PDF file with plan"
        , "tail:I?Number of last week/month to process"
        , "XL:F?X length of one week/month (in cm)"
        , "XO:F=0.9?X offset of one week/month (in cm relative to XL)"
        , "YL:F?Y length of one week/month"
        , "YO:F=0.5?Y offset of one week/month (in cm relative to YL)"
        , "year:I=%d?Year for which to process calendar" % (CAL.Date ().year, )
        , "Yearly:B?Generate yearly instead of weekly sheets"
        )
    , max_args    = 0
)

"""
python ~/Y/_CAL/pdf.py -year 2008 -landscape -XL 8.95 -YL 16.85 -XO=1.5
python ~/Y/_CAL/pdf.py -year 2008 -landscape -XL 8.95 -YL 16.85 -XO=1.5 -monthly
"""

if __name__ != "__main__" :
    CAL._Export ("*")
else :
    _Command ()
### __END__ CAL.pdf
