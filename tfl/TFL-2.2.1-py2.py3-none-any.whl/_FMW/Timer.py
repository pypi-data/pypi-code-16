# -*- coding: utf-8 -*-
# Copyright (C) 2004-2010 Mag. Christian Tanzer. All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.FMW.Timer
#
# Purpose
#    Measure execution time of functions and methods without changing the
#    source code of the measured components
#
# Revision Dates
#    22-Sep-2004 (CT) Creation
#    ««revision-date»»···
#--

from   _TFL                   import TFL
import _TFL._FMW.Recorder
import _TFL._FMW.Wrapper

import time

class Time_Recorder_F (TFL.FMW.File_Recorder) :
    """Record execution time measurements into a file"""

    format = "%(wrapper)-40s : cpu = %(cpu)s, elapsed = %(elapsed)s\n"

# end class Time_Recorder_F

class Time_Recorder_D (TFL.FMW.Dict_Recorder) :
    """Record execution time measurements into a dictionary"""

# end class Time_Recorder_D

class Time_Measurer (TFL.FMW.Wrapped_Recorder) :
    """Measurer of execution time of a single function or method"""

    Default_Recorder = Time_Recorder_F

    def __call__ (self, * args, ** kw) :
        start_clock = time.clock ()
        start_time  = time.time  ()
        result      = self.fct   (* args, ** kw)
        end_clock   = time.clock ()
        end_time    = time.time  ()
        self.recorder.record \
            ( wrapper = self
            , cpu     = end_clock - start_clock
            , elapsed = end_time  - start_time
            )
        return result
    # end def __call__

# end class Time_Measurer

class Timer (TFL.FMW.Wrapper) :
    """Measure execution time of functions and methods without changing the
       source code of the measured components.
    """

    Wrapped_FM = Time_Measurer

# end class Timer

if __name__ != "__main__" :
    TFL.FMW._Export ("*")
### __END__ TFL.FMW.Timer
