# -*- coding: utf-8 -*-
"""
	commmon helpers
	https://github.com/erazor83/pyblynk/blob/master/lib/common.py
	The MIT License (MIT)

	Copyright (c) 2015 Alexander Krause

	Permission is hereby granted, free of charge, to any person obtaining a copy
	of this software and associated documentation files (the "Software"), to deal
	in the Software without restriction, including without limitation the rights
	to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
	copies of the Software, and to permit persons to whom the Software is
	furnished to do so, subject to the following conditions:

	The above copyright notice and this permission notice shall be included in all
	copies or substantial portions of the Software.

	THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
	IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
	FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
	AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
	LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
	OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
	SOFTWARE.

"""
__author__	= """Alexander Krause <alexander.krause@ed-solutions.de>"""
__date__ 		= "2016-01-11"
__version__	= "0.2.0"
__credits__	= """Copyright e-design, Alexander Krause <alexander.krause@ed-solutions.de>"""
__license__	= "MIT"

import struct

MSG_RSP				= 0
MSG_LOGIN			= 2
MSG_PING			= 6
MSG_BRIDGE		= 15
MSG_HW				= 20

MSG_STATUS_OK	= 200


ProtocolHeader = struct.Struct("!BHH")

def ArgsToBuffer(*args):
	# Convert params to string and join using \0
	return "\0".join(map(str, args))

def BufferToArgs(buff):
	return (buff.decode('ascii')).split("\0")
