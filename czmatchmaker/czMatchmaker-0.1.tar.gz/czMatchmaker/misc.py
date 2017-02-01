# -*- coding: utf-8 -*-
#
#   Copyright (C) 2016 Mateusz Krzysztof Łącki.
#
#   This file is part of czMatchmaker.
#
#   MassTodon is free software: you can redistribute it and/or modify
#   it under the terms of the GNU AFFERO GENERAL PUBLIC LICENSE
#   Version 3.
#
#   czMatchmaker is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#   You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#   Version 3 along with czMatchmaker.  If not, see
#   <https://www.gnu.org/licenses/agpl-3.0.en.html>.

from dplython import DelayFunction

@DelayFunction
def Round_and_Multi(x, times = 100):
    return [ int(round(a*times)) for a in x ]

@DelayFunction
def Round(x):
    return [ round(a) for a in x ]

@DelayFunction
def crossprod( x, y):
    return [ xx*yy for xx,yy in zip(x,y) ]
