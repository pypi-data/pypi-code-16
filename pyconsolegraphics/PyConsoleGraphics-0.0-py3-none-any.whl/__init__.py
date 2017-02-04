"""
PyConsoleGraphics is a "one size fits all" library for text-mode graphics.
It's designed to operate as a wrapper around the standard library curses
module, Pygame, and normal text output - enabling exactly the same code to run
under any supported backend on any supported system with no extra work on your
part. It also has wrappers around it, allowing drop-in replacement of other
console graphics libraries.

The MIT License (MIT)

Copyright (c) 2016 Schilcote

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

～  ～   ～～～
"""
import abc

import io
import threading

import time

import sys
from collections import namedtuple

import collections

import pyconsolegraphics.backends as backends

backend_attempt_order = ["pygamewindow"]
available_backends = set(backends.backend_funcs.keys())

keypress_code_set = {
    '!',
    '"',
    '#',
    '$',
    '&',
    "'",
    '(',
    ')',
    '*',
    '+',
    ',',
    '-',
    '.',
    '/',
    '0',
    '1',
    '2',
    '3',
    '4',
    '5',
    '6',
    '7',
    '8',
    '9',
    ':',
    ';',
    '<',
    '=',
    '>',
    '?',
    '@',
    '[',
    '\\',
    ']',
    '^',
    '_',
    '`',
    'a',
    'b',
    'backspace',
    'c',
    'clear',
    'd',
    'delete',
    'down',
    'e',
    'end',
    'enter',
    'escape',
    'f',
    'f1',
    'f10',
    'f11',
    'f12',
    'f13',
    'f14',
    'f15',
    'f2',
    'f3',
    'f4',
    'f5',
    'f6',
    'f7',
    'f8',
    'f9',
    'g',
    'h',
    'i',
    'insert',
    'j',
    'k',
    'l',
    'left',
    'm',
    'n',
    'o',
    'p',
    'page down',
    'page up',
    'pause',
    'printscreen',
    'q',
    'r',
    'right',
    's',
    'space',
    'sysrq',
    't',
    'tab',
    'u',
    'up',
    'v',
    'w',
    'x',
    'y',
    'z',
    'shift',
    'control',
    'alt',
    'capslock',
    'numlock',
    'scrollock'
}

#Copied from Pygame's color names. I think this is actually some kind of
#standard? Not sure.
colors = {'tomato3': (205, 79, 57, 255), 'deepskyblue2': (0, 178, 238, 255), 'slateblue2': (122, 103, 238, 255), 'skyblue4': (74, 112, 139, 255), 'navyblue': (0, 0, 128, 255), 'ivory2': (238, 238, 224, 255), 'darkmagenta': (139, 0, 139, 255), 'tan': (210, 180, 140, 255), 'gray14': (36, 36, 36, 255), 'goldenrod2': (238, 180, 34, 255), 'grey76': (194, 194, 194, 255), 'gray23': (59, 59, 59, 255), 'skyblue': (135, 206, 235, 255), 'darkgoldenrod4': (139, 101, 8, 255), 'firebrick2': (238, 44, 44, 255), 'darkslategrey': (47, 79, 79, 255), 'grey100': (255, 255, 255, 255), 'grey9': (23, 23, 23, 255), 'pink4': (139, 99, 108, 255), 'slategray4': (108, 123, 139, 255), 'grey69': (176, 176, 176, 255), 'gray5': (13, 13, 13, 255), 'turquoise4': (0, 134, 139, 255), 'mediumorchid3': (180, 82, 205, 255), 'darkslategray3': (121, 205, 205, 255), 'wheat1': (255, 231, 186, 255), 'chocolate3': (205, 102, 29, 255), 'grey25': (64, 64, 64, 255), 'darkslategray4': (82, 139, 139, 255), 'coral3': (205, 91, 69, 255), 'gray94': (240, 240, 240, 255), 'orange3': (205, 133, 0, 255), 'darkseagreen1': (193, 255, 193, 255), 'orangered3': (205, 55, 0, 255), 'grey12': (31, 31, 31, 255), 'gray62': (158, 158, 158, 255), 'grey79': (201, 201, 201, 255), 'lightcoral': (240, 128, 128, 255), 'mistyrose': (255, 228, 225, 255), 'gray75': (191, 191, 191, 255), 'slategray3': (159, 182, 205, 255), 'pink2': (238, 169, 184, 255), 'dimgrey': (105, 105, 105, 255), 'grey10': (26, 26, 26, 255), 'green1': (0, 255, 0, 255), 'grey20': (51, 51, 51, 255), 'dimgray': (105, 105, 105, 255), 'grey24': (61, 61, 61, 255), 'khaki2': (238, 230, 133, 255), 'grey13': (33, 33, 33, 255), 'mediumpurple': (147, 112, 219, 255), 'dodgerblue2': (28, 134, 238, 255), 'gray20': (51, 51, 51, 255), 'grey71': (181, 181, 181, 255), 'darkorange2': (238, 118, 0, 255), 'grey80': (204, 204, 204, 255), 'magenta3': (205, 0, 205, 255), 'lemonchiffon3': (205, 201, 165, 255), 'lightblue1': (191, 239, 255, 255), 'lightgoldenrod4': (139, 129, 76, 255), 'lawngreen': (124, 252, 0, 255), 'grey94': (240, 240, 240, 255), 'olivedrab2': (179, 238, 58, 255), 'gold': (255, 215, 0, 255), 'green': (0, 255, 0, 255), 'navajowhite4': (139, 121, 94, 255), 'grey45': (115, 115, 115, 255), 'mediumorchid': (186, 85, 211, 255), 'lemonchiffon1': (255, 250, 205, 255), 'lightsteelblue3': (162, 181, 205, 255), 'lightyellow2': (238, 238, 209, 255), 'gray45': (115, 115, 115, 255), 'peachpuff': (255, 218, 185, 255), 'peachpuff4': (139, 119, 101, 255), 'blue': (0, 0, 255, 255), 'chartreuse3': (102, 205, 0, 255), 'lightcyan3': (180, 205, 205, 255), 'gray15': (38, 38, 38, 255), 'grey6': (15, 15, 15, 255), 'gainsboro': (220, 220, 220, 255), 'cyan4': (0, 139, 139, 255), 'grey0': (0, 0, 0, 255), 'grey21': (54, 54, 54, 255), 'deeppink3': (205, 16, 118, 255), 'aquamarine4': (69, 139, 116, 255), 'moccasin': (255, 228, 181, 255), 'violetred4': (139, 34, 82, 255), 'grey17': (43, 43, 43, 255), 'red': (255, 0, 0, 255), 'grey53': (135, 135, 135, 255), 'indianred3': (205, 85, 85, 255), 'lightskyblue2': (164, 211, 238, 255), 'gray41': (105, 105, 105, 255), 'slateblue4': (71, 60, 139, 255), 'gold1': (255, 215, 0, 255), 'orangered4': (139, 37, 0, 255), 'yellowgreen': (154, 205, 50, 255), 'grey54': (138, 138, 138, 255), 'brown3': (205, 51, 51, 255), 'slategray1': (198, 226, 255, 255), 'olivedrab4': (105, 139, 34, 255), 'lightgrey': (211, 211, 211, 255), 'gray95': (242, 242, 242, 255), 'hotpink': (255, 105, 180, 255), 'paleturquoise2': (174, 238, 238, 255), 'navajowhite1': (255, 222, 173, 255), 'gray63': (161, 161, 161, 255), 'gray32': (82, 82, 82, 255), 'mintcream': (245, 255, 250, 255), 'yellow': (255, 255, 0, 255), 'gray61': (156, 156, 156, 255), 'slategray': (112, 128, 144, 255), 'gray52': (133, 133, 133, 255), 'lemonchiffon4': (139, 137, 112, 255), 'gray67': (171, 171, 171, 255), 'gray89': (227, 227, 227, 255), 'purple1': (155, 48, 255, 255), 'grey78': (199, 199, 199, 255), 'darkgoldenrod1': (255, 185, 15, 255), 'lightsalmon4': (139, 87, 66, 255), 'gray79': (201, 201, 201, 255), 'grey93': (237, 237, 237, 255), 'ivory3': (205, 205, 193, 255), 'bisque4': (139, 125, 107, 255), 'gray2': (5, 5, 5, 255), 'mediumorchid1': (224, 102, 255, 255), 'goldenrod': (218, 165, 32, 255), 'ghostwhite': (248, 248, 255, 255), 'gray46': (117, 117, 117, 255), 'magenta': (255, 0, 255, 255), 'azure4': (131, 139, 139, 255), 'gray39': (99, 99, 99, 255), 'grey22': (56, 56, 56, 255), 'violetred1': (255, 62, 150, 255), 'darkgoldenrod3': (205, 149, 12, 255), 'lavenderblush3': (205, 193, 197, 255), 'gray88': (224, 224, 224, 255), 'pink3': (205, 145, 158, 255), 'seagreen3': (67, 205, 128, 255), 'deeppink1': (255, 20, 147, 255), 'steelblue4': (54, 100, 139, 255), 'lightsalmon': (255, 160, 122, 255), 'lightcyan': (224, 255, 255, 255), 'chocolate1': (255, 127, 36, 255), 'grey43': (110, 110, 110, 255), 'maroon4': (139, 28, 98, 255), 'gray60': (153, 153, 153, 255), 'darkorchid1': (191, 62, 255, 255), 'indianred1': (255, 106, 106, 255), 'darkseagreen4': (105, 139, 105, 255), 'palevioletred4': (139, 71, 93, 255), 'darkblue': (0, 0, 139, 255), 'cyan': (0, 255, 255, 255), 'paleturquoise3': (150, 205, 205, 255), 'grey49': (125, 125, 125, 255), 'lightskyblue4': (96, 123, 139, 255), 'honeydew3': (193, 205, 193, 255), 'royalblue1': (72, 118, 255, 255), 'indianred2': (238, 99, 99, 255), 'lavenderblush4': (139, 131, 134, 255), 'gray92': (235, 235, 235, 255), 'darkviolet': (148, 0, 211, 255), 'grey85': (217, 217, 217, 255), 'gray87': (222, 222, 222, 255), 'grey55': (140, 140, 140, 255), 'darkorange': (255, 140, 0, 255), 'darkgoldenrod': (184, 134, 11, 255), 'lightskyblue3': (141, 182, 205, 255), 'grey34': (87, 87, 87, 255), 'rosybrown4': (139, 105, 105, 255), 'seagreen4': (46, 139, 87, 255), 'gray53': (135, 135, 135, 255), 'magenta4': (139, 0, 139, 255), 'orange': (255, 165, 0, 255), 'cornsilk3': (205, 200, 177, 255), 'darkorange1': (255, 127, 0, 255), 'red4': (139, 0, 0, 255), 'gray64': (163, 163, 163, 255), 'blue4': (0, 0, 139, 255), 'peachpuff1': (255, 218, 185, 255), 'gray25': (64, 64, 64, 255), 'lavenderblush': (255, 240, 245, 255), 'snow2': (238, 233, 233, 255), 'paleturquoise4': (102, 139, 139, 255), 'gray0': (0, 0, 0, 255), 'darkturquoise': (0, 206, 209, 255), 'orange2': (238, 154, 0, 255), 'blueviolet': (138, 43, 226, 255), 'lightcyan1': (224, 255, 255, 255), 'mediumspringgreen': (0, 250, 154, 255), 'antiquewhite4': (139, 131, 120, 255), 'rosybrown3': (205, 155, 155, 255), 'dodgerblue3': (24, 116, 205, 255), 'snow3': (205, 201, 201, 255), 'gray33': (84, 84, 84, 255), 'lightslateblue': (132, 112, 255, 255), 'gray54': (138, 138, 138, 255), 'navajowhite': (255, 222, 173, 255), 'grey63': (161, 161, 161, 255), 'skyblue1': (135, 206, 255, 255), 'beige': (245, 245, 220, 255), 'grey31': (79, 79, 79, 255), 'magenta1': (255, 0, 255, 255), 'gray24': (61, 61, 61, 255), 'grey67': (171, 171, 171, 255), 'lightsteelblue2': (188, 210, 238, 255), 'darkseagreen': (143, 188, 143, 255), 'mistyrose3': (205, 183, 181, 255), 'gray40': (102, 102, 102, 255), 'violetred': (208, 32, 144, 255), 'purple4': (85, 26, 139, 255), 'grey47': (120, 120, 120, 255), 'purple2': (145, 44, 238, 255), 'tan3': (205, 133, 63, 255), 'mediumseagreen': (60, 179, 113, 255), 'blanchedalmond': (255, 235, 205, 255), 'springgreen2': (0, 238, 118, 255), 'pink1': (255, 181, 197, 255), 'coral2': (238, 106, 80, 255), 'seashell': (255, 245, 238, 255), 'gray59': (150, 150, 150, 255), 'grey66': (168, 168, 168, 255), 'chocolate4': (139, 69, 19, 255), 'lightgray': (211, 211, 211, 255), 'thistle2': (238, 210, 238, 255), 'ivory4': (139, 139, 131, 255), 'cyan2': (0, 238, 238, 255), 'purple': (160, 32, 240, 255), 'grey81': (207, 207, 207, 255), 'orangered2': (238, 64, 0, 255), 'grey15': (38, 38, 38, 255), 'brown': (165, 42, 42, 255), 'gray100': (255, 255, 255, 255), 'grey7': (18, 18, 18, 255), 'grey51': (130, 130, 130, 255), 'palegoldenrod': (238, 232, 170, 255), 'lightsalmon3': (205, 129, 98, 255), 'slateblue1': (131, 111, 255, 255), 'mistyrose2': (238, 213, 210, 255), 'ivory': (255, 255, 240, 255), 'burlywood3': (205, 170, 125, 255), 'lightslategrey': (119, 136, 153, 255), 'grey97': (247, 247, 247, 255), 'orangered': (255, 69, 0, 255), 'lightgoldenrod3': (205, 190, 112, 255), 'darkolivegreen1': (202, 255, 112, 255), 'firebrick': (178, 34, 34, 255), 'hotpink1': (255, 110, 180, 255), 'navy': (0, 0, 128, 255), 'darkolivegreen': (85, 107, 47, 255), 'turquoise2': (0, 229, 238, 255), 'grey92': (235, 235, 235, 255), 'grey16': (41, 41, 41, 255), 'grey26': (66, 66, 66, 255), 'honeydew1': (240, 255, 240, 255), 'aquamarine2': (118, 238, 198, 255), 'dodgerblue4': (16, 78, 139, 255), 'lightgoldenrodyellow': (250, 250, 210, 255), 'blue3': (0, 0, 205, 255), 'azure': (240, 255, 255, 255), 'salmon1': (255, 140, 105, 255), 'blue2': (0, 0, 238, 255), 'lightpink': (255, 182, 193, 255), 'deeppink': (255, 20, 147, 255), 'palegreen4': (84, 139, 84, 255), 'grey91': (232, 232, 232, 255), 'grey18': (46, 46, 46, 255), 'gray81': (207, 207, 207, 255), 'gray7': (18, 18, 18, 255), 'lightsteelblue': (176, 196, 222, 255), 'seagreen2': (78, 238, 148, 255), 'grey73': (186, 186, 186, 255), 'cyan3': (0, 205, 205, 255), 'grey88': (224, 224, 224, 255), 'gray35': (89, 89, 89, 255), 'peachpuff2': (238, 203, 173, 255), 'gray28': (71, 71, 71, 255), 'bisque2': (238, 213, 183, 255), 'orchid': (218, 112, 214, 255), 'grey61': (156, 156, 156, 255), 'grey11': (28, 28, 28, 255), 'mediumaquamarine': (102, 205, 170, 255), 'lightslategray': (119, 136, 153, 255), 'grey87': (222, 222, 222, 255), 'brown1': (255, 64, 64, 255), 'darkorchid2': (178, 58, 238, 255), 'coral1': (255, 114, 86, 255), 'forestgreen': (34, 139, 34, 255), 'darkorchid4': (104, 34, 139, 255), 'lightyellow3': (205, 205, 180, 255), 'violetred2': (238, 58, 140, 255), 'dodgerblue1': (30, 144, 255, 255), 'plum3': (205, 150, 205, 255), 'burlywood4': (139, 115, 85, 255), 'orchid1': (255, 131, 250, 255), 'antiquewhite': (250, 235, 215, 255), 'grey44': (112, 112, 112, 255), 'papayawhip': (255, 239, 213, 255), 'darkseagreen2': (180, 238, 180, 255), 'khaki1': (255, 246, 143, 255), 'gray82': (209, 209, 209, 255), 'olivedrab1': (192, 255, 62, 255), 'magenta2': (238, 0, 238, 255), 'azure3': (193, 205, 205, 255), 'sienna4': (139, 71, 38, 255), 'lightblue4': (104, 131, 139, 255), 'bisque3': (205, 183, 158, 255), 'cornsilk4': (139, 136, 120, 255), 'grey4': (10, 10, 10, 255), 'grey23': (59, 59, 59, 255), 'salmon4': (139, 76, 57, 255), 'cornsilk2': (238, 232, 205, 255), 'grey64': (163, 163, 163, 255), 'darkolivegreen4': (110, 139, 61, 255), 'grey56': (143, 143, 143, 255), 'deepskyblue3': (0, 154, 205, 255), 'wheat2': (238, 216, 174, 255), 'grey14': (36, 36, 36, 255), 'peru': (205, 133, 63, 255), 'brown4': (139, 35, 35, 255), 'lightpink2': (238, 162, 173, 255), 'lemonchiffon': (255, 250, 205, 255), 'gray29': (74, 74, 74, 255), 'cadetblue4': (83, 134, 139, 255), 'gray31': (79, 79, 79, 255), 'darkolivegreen2': (188, 238, 104, 255), 'dodgerblue': (30, 144, 255, 255), 'seagreen': (46, 139, 87, 255), 'honeydew2': (224, 238, 224, 255), 'gray51': (130, 130, 130, 255), 'gray19': (48, 48, 48, 255), 'darkgray': (169, 169, 169, 255), 'orchid2': (238, 122, 233, 255), 'paleturquoise1': (187, 255, 255, 255), 'greenyellow': (173, 255, 47, 255), 'firebrick4': (139, 26, 26, 255), 'darkred': (139, 0, 0, 255), 'antiquewhite3': (205, 192, 176, 255), 'mediumblue': (0, 0, 205, 255), 'salmon': (250, 128, 114, 255), 'gray43': (110, 110, 110, 255), 'lightgoldenrod1': (255, 236, 139, 255), 'wheat3': (205, 186, 150, 255), 'lightblue': (173, 216, 230, 255), 'gray57': (145, 145, 145, 255), 'grey58': (148, 148, 148, 255), 'lightsteelblue4': (110, 123, 139, 255), 'steelblue': (70, 130, 180, 255), 'grey2': (5, 5, 5, 255), 'saddlebrown': (139, 69, 19, 255), 'azure1': (240, 255, 255, 255), 'gray77': (196, 196, 196, 255), 'turquoise1': (0, 245, 255, 255), 'mistyrose4': (139, 125, 123, 255), 'purple3': (125, 38, 205, 255), 'grey39': (99, 99, 99, 255), 'seashell3': (205, 197, 191, 255), 'slategrey': (112, 128, 144, 255), 'paleturquoise': (175, 238, 238, 255), 'olivedrab3': (154, 205, 50, 255), 'grey52': (133, 133, 133, 255), 'royalblue2': (67, 110, 238, 255), 'grey74': (189, 189, 189, 255), 'grey72': (184, 184, 184, 255), 'gray58': (148, 148, 148, 255), 'lightpink4': (139, 95, 101, 255), 'cadetblue': (95, 158, 160, 255), 'grey70': (179, 179, 179, 255), 'mediumorchid4': (122, 55, 139, 255), 'gray90': (229, 229, 229, 255), 'grey29': (74, 74, 74, 255), 'darkorchid3': (154, 50, 205, 255), 'floralwhite': (255, 250, 240, 255), 'lightyellow4': (139, 139, 122, 255), 'grey5': (13, 13, 13, 255), 'violet': (238, 130, 238, 255), 'yellow3': (205, 205, 0, 255), 'sienna3': (205, 104, 57, 255), 'hotpink2': (238, 106, 167, 255), 'gray50': (127, 127, 127, 255), 'lavenderblush2': (238, 224, 229, 255), 'aquamarine': (127, 255, 212, 255), 'hotpink4': (139, 58, 98, 255), 'grey83': (212, 212, 212, 255), 'bisque': (255, 228, 196, 255), 'tomato4': (139, 54, 38, 255), 'mistyrose1': (255, 228, 225, 255), 'gold4': (139, 117, 0, 255), 'goldenrod1': (255, 193, 37, 255), 'goldenrod3': (205, 155, 29, 255), 'navajowhite2': (238, 207, 161, 255), 'gray78': (199, 199, 199, 255), 'red1': (255, 0, 0, 255), 'grey19': (48, 48, 48, 255), 'darkseagreen3': (155, 205, 155, 255), 'honeydew': (240, 255, 240, 255), 'grey89': (227, 227, 227, 255), 'darkorchid': (153, 50, 204, 255), 'gray99': (252, 252, 252, 255), 'slateblue3': (105, 89, 205, 255), 'khaki': (240, 230, 140, 255), 'lightpink3': (205, 140, 149, 255), 'palegreen1': (154, 255, 154, 255), 'grey1': (3, 3, 3, 255), 'gray26': (66, 66, 66, 255), 'olivedrab': (107, 142, 35, 255), 'steelblue2': (92, 172, 238, 255), 'rosybrown2': (238, 180, 180, 255), 'gray18': (46, 46, 46, 255), 'seagreen1': (84, 255, 159, 255), 'tan1': (255, 165, 79, 255), 'gray38': (97, 97, 97, 255), 'darkgrey': (169, 169, 169, 255), 'mediumpurple4': (93, 71, 139, 255), 'orchid4': (139, 71, 137, 255), 'grey40': (102, 102, 102, 255), 'palevioletred3': (205, 104, 137, 255), 'darkorange3': (205, 102, 0, 255), 'gray48': (122, 122, 122, 255), 'coral4': (139, 62, 47, 255), 'grey30': (77, 77, 77, 255), 'cyan1': (0, 255, 255, 255), 'gray42': (107, 107, 107, 255), 'maroon1': (255, 52, 179, 255), 'grey86': (219, 219, 219, 255), 'grey65': (166, 166, 166, 255), 'khaki3': (205, 198, 115, 255), 'darkslategray1': (151, 255, 255, 255), 'palegreen3': (124, 205, 124, 255), 'skyblue2': (126, 192, 238, 255), 'indianred': (205, 92, 92, 255), 'linen': (250, 240, 230, 255), 'oldlace': (253, 245, 230, 255), 'goldenrod4': (139, 105, 20, 255), 'gray69': (176, 176, 176, 255), 'gray93': (237, 237, 237, 255), 'steelblue1': (99, 184, 255, 255), 'orange4': (139, 90, 0, 255), 'seashell4': (139, 134, 130, 255), 'gray98': (250, 250, 250, 255), 'thistle4': (139, 123, 139, 255), 'darkslategray2': (141, 238, 238, 255), 'grey': (190, 190, 190, 255), 'deeppink4': (139, 10, 80, 255), 'violetred3': (205, 50, 120, 255), 'coral': (255, 127, 80, 255), 'lightyellow': (255, 255, 224, 255), 'tomato1': (255, 99, 71, 255), 'aquamarine3': (102, 205, 170, 255), 'gray97': (247, 247, 247, 255), 'peachpuff3': (205, 175, 149, 255), 'azure2': (224, 238, 238, 255), 'grey33': (84, 84, 84, 255), 'rosybrown1': (255, 193, 193, 255), 'snow1': (255, 250, 250, 255), 'lightskyblue': (135, 206, 250, 255), 'grey38': (97, 97, 97, 255), 'antiquewhite2': (238, 223, 204, 255), 'grey90': (229, 229, 229, 255), 'gold2': (238, 201, 0, 255), 'palegreen': (152, 251, 152, 255), 'salmon3': (205, 112, 84, 255), 'grey77': (196, 196, 196, 255), 'lightcyan4': (122, 139, 139, 255), 'grey59': (150, 150, 150, 255), 'lightgoldenrod': (238, 221, 130, 255), 'red3': (205, 0, 0, 255), 'gray76': (194, 194, 194, 255), 'gray17': (43, 43, 43, 255), 'gray74': (189, 189, 189, 255), 'mediumturquoise': (72, 209, 204, 255), 'mediumorchid2': (209, 95, 238, 255), 'gray85': (217, 217, 217, 255), 'gray71': (181, 181, 181, 255), 'bisque1': (255, 228, 196, 255), 'maroon2': (238, 48, 167, 255), 'gray37': (94, 94, 94, 255), 'gray91': (232, 232, 232, 255), 'royalblue3': (58, 95, 205, 255), 'khaki4': (139, 134, 78, 255), 'gray13': (33, 33, 33, 255), 'sienna1': (255, 130, 71, 255), 'tomato2': (238, 92, 66, 255), 'slategray2': (185, 211, 238, 255), 'navajowhite3': (205, 179, 139, 255), 'tomato': (255, 99, 71, 255), 'turquoise': (64, 224, 208, 255), 'springgreen': (0, 255, 127, 255), 'lightsalmon2': (238, 149, 114, 255), 'lightsalmon1': (255, 160, 122, 255), 'grey60': (153, 153, 153, 255), 'gray34': (87, 87, 87, 255), 'salmon2': (238, 130, 98, 255), 'grey62': (158, 158, 158, 255), 'grey82': (209, 209, 209, 255), 'plum4': (139, 102, 139, 255), 'burlywood': (222, 184, 135, 255), 'gray96': (245, 245, 245, 255), 'chocolate': (210, 105, 30, 255), 'yellow1': (255, 255, 0, 255), 'lightyellow1': (255, 255, 224, 255), 'gray68': (173, 173, 173, 255), 'palevioletred': (219, 112, 147, 255), 'firebrick1': (255, 48, 48, 255), 'plum1': (255, 187, 255, 255), 'springgreen4': (0, 139, 69, 255), 'seashell1': (255, 245, 238, 255), 'indianred4': (139, 58, 58, 255), 'gray1': (3, 3, 3, 255), 'thistle1': (255, 225, 255, 255), 'lightskyblue1': (176, 226, 255, 255), 'lightcyan2': (209, 238, 238, 255), 'mediumvioletred': (199, 21, 133, 255), 'grey95': (242, 242, 242, 255), 'lemonchiffon2': (238, 233, 191, 255), 'cornflowerblue': (100, 149, 237, 255), 'springgreen3': (0, 205, 102, 255), 'lightsteelblue1': (202, 225, 255, 255), 'lavender': (230, 230, 250, 255), 'chartreuse1': (127, 255, 0, 255), 'whitesmoke': (245, 245, 245, 255), 'grey96': (245, 245, 245, 255), 'grey50': (127, 127, 127, 255), 'gray84': (214, 214, 214, 255), 'orange1': (255, 165, 0, 255), 'firebrick3': (205, 38, 38, 255), 'burlywood2': (238, 197, 145, 255), 'snow': (255, 250, 250, 255), 'gray47': (120, 120, 120, 255), 'blue1': (0, 0, 255, 255), 'green2': (0, 238, 0, 255), 'deeppink2': (238, 18, 137, 255), 'gray65': (166, 166, 166, 255), 'gray8': (20, 20, 20, 255), 'gray55': (140, 140, 140, 255), 'gray27': (69, 69, 69, 255), 'seashell2': (238, 229, 222, 255), 'lightgoldenrod2': (238, 220, 130, 255), 'grey98': (250, 250, 250, 255), 'gray11': (28, 28, 28, 255), 'deepskyblue': (0, 191, 255, 255), 'plum2': (238, 174, 238, 255), 'snow4': (139, 137, 137, 255), 'cornsilk': (255, 248, 220, 255), 'darkcyan': (0, 139, 139, 255), 'orangered1': (255, 69, 0, 255), 'lavenderblush1': (255, 240, 245, 255), 'gray': (190, 190, 190, 255), 'darkkhaki': (189, 183, 107, 255), 'grey37': (94, 94, 94, 255), 'black': (0, 0, 0, 255), 'darkolivegreen3': (162, 205, 90, 255), 'darkgreen': (0, 100, 0, 255), 'chocolate2': (238, 118, 33, 255), 'sienna2': (238, 121, 66, 255), 'darkslateblue': (72, 61, 139, 255), 'grey27': (69, 69, 69, 255), 'gray21': (54, 54, 54, 255), 'darkslategray': (47, 79, 79, 255), 'wheat': (245, 222, 179, 255), 'grey3': (8, 8, 8, 255), 'maroon3': (205, 41, 144, 255), 'gray70': (179, 179, 179, 255), 'springgreen1': (0, 255, 127, 255), 'cornsilk1': (255, 248, 220, 255), 'palevioletred2': (238, 121, 159, 255), 'powderblue': (176, 224, 230, 255), 'thistle': (216, 191, 216, 255), 'aliceblue': (240, 248, 255, 255), 'gray12': (31, 31, 31, 255), 'grey36': (92, 92, 92, 255), 'lightpink1': (255, 174, 185, 255), 'ivory1': (255, 255, 240, 255), 'white': (255, 255, 255, 255), 'lightblue3': (154, 192, 205, 255), 'grey42': (107, 107, 107, 255), 'royalblue': (65, 105, 225, 255), 'gray80': (204, 204, 204, 255), 'mediumpurple1': (171, 130, 255, 255), 'gray56': (143, 143, 143, 255), 'gray36': (92, 92, 92, 255), 'lightseagreen': (32, 178, 170, 255), 'gray22': (56, 56, 56, 255), 'cadetblue2': (142, 229, 238, 255), 'mediumpurple2': (159, 121, 238, 255), 'wheat4': (139, 126, 102, 255), 'gray9': (23, 23, 23, 255), 'gray83': (212, 212, 212, 255), 'mediumslateblue': (123, 104, 238, 255), 'gray30': (77, 77, 77, 255), 'darksalmon': (233, 150, 122, 255), 'cadetblue1': (152, 245, 255, 255), 'darkgoldenrod2': (238, 173, 14, 255), 'grey84': (214, 214, 214, 255), 'yellow4': (139, 139, 0, 255), 'chartreuse': (127, 255, 0, 255), 'palegreen2': (144, 238, 144, 255), 'deepskyblue4': (0, 104, 139, 255), 'slateblue': (106, 90, 205, 255), 'thistle3': (205, 181, 205, 255), 'turquoise3': (0, 197, 205, 255), 'sienna': (160, 82, 45, 255), 'deepskyblue1': (0, 191, 255, 255), 'skyblue3': (108, 166, 205, 255), 'grey8': (20, 20, 20, 255), 'red2': (238, 0, 0, 255), 'steelblue3': (79, 148, 205, 255), 'grey48': (122, 122, 122, 255), 'limegreen': (50, 205, 50, 255), 'grey46': (117, 117, 117, 255), 'green4': (0, 139, 0, 255), 'gray44': (112, 112, 112, 255), 'chartreuse2': (118, 238, 0, 255), 'grey68': (173, 173, 173, 255), 'grey35': (89, 89, 89, 255), 'grey41': (105, 105, 105, 255), 'aquamarine1': (127, 255, 212, 255), 'darkorange4': (139, 69, 0, 255), 'grey57': (145, 145, 145, 255), 'gray10': (26, 26, 26, 255), 'tan2': (238, 154, 73, 255), 'chartreuse4': (69, 139, 0, 255), 'antiquewhite1': (255, 239, 219, 255), 'mediumpurple3': (137, 104, 205, 255), 'gray6': (15, 15, 15, 255), 'lightgreen': (144, 238, 144, 255), 'rosybrown': (188, 143, 143, 255), 'tan4': (139, 90, 43, 255), 'gray86': (219, 219, 219, 255), 'brown2': (238, 59, 59, 255), 'grey28': (71, 71, 71, 255), 'palevioletred1': (255, 130, 171, 255), 'grey75': (191, 191, 191, 255), 'hotpink3': (205, 96, 144, 255), 'sandybrown': (244, 164, 96, 255), 'green3': (0, 205, 0, 255), 'gray3': (8, 8, 8, 255), 'midnightblue': (25, 25, 112, 255), 'gray16': (41, 41, 41, 255), 'gray66': (168, 168, 168, 255), 'gray4': (10, 10, 10, 255), 'grey99': (252, 252, 252, 255), 'yellow2': (238, 238, 0, 255), 'maroon': (176, 48, 96, 255), 'burlywood1': (255, 211, 155, 255), 'grey32': (82, 82, 82, 255), 'cadetblue3': (122, 197, 205, 255), 'lightblue2': (178, 223, 238, 255), 'royalblue4': (39, 64, 139, 255), 'gray72': (184, 184, 184, 255), 'gray49': (125, 125, 125, 255), 'gold3': (205, 173, 0, 255), 'honeydew4': (131, 139, 131, 255), 'gray73': (186, 186, 186, 255), 'orchid3': (205, 105, 201, 255), 'pink': (255, 192, 203, 255), 'plum': (221, 160, 221, 255)}

class PyConsoleGraphicsException(Exception):
    """Base exception for PyConsoleGraphics-specific errors."""

class InputAlreadyActiveError(PyConsoleGraphicsException):
    """When you try to activate an InputCursor but another InputCursor is
    already active, it raises this exception."""

class CursorOverflowError(PyConsoleGraphicsException):
    """Raised by the Cursor when it's asked to do something that would push
    it past the edges of the terminal. This should never be raised itself;
    HorizontalCursorOverflow or VerticleCursorOverflow should be raised
    instead; catching CursorOverflow will catch both."""

class HorizontalCursorOverflowError(CursorOverflowError):
    """Raised by the Cursor when it is asked to do something that would push
    its x position below zero or past the terminal's width, and has been told
    not to deal with the problem itself."""

class VerticalCursorOverflowError(CursorOverflowError):
    """Raised by the Cursor when it is asked to do something that would push
    its y position below zero or past the terminal's height, and has been
    told not to deal with the problem itself."""

class Pos(collections.namedtuple("Position", ["x","y"])):
    """Think 'vector' if you know what that means. Represents a location in 2-D cartesian space.

    This is a very simple class, basically just a named tuple plus addition and subtraction operators
    that make it easier to offest positions from one another."""

    def __add__(self, other):
        return Pos(self[0]+other[0], self[1]+other[1])

    def __sub__(self, other):
        return Pos(self[0]-other[0], self[1]+other[1])

class Cursor:
    """A cursor on the terminal screen. A terminal supports an arbitrary
    number of cursors. Cursors have position and write characters in the cells
    under them, moving left (and wrapping around to the next line when they
    run out of left) as they do.

    pos is a 2-tuple representing the initial position of the cursor.

    fgcolor and bgcolor are the foreground and background color respectively of
    text printed with this cursor. A color of "None" represents "whatever
    color is set globally on the Terminal," so text printed with a cursor
    who'se .fgcolor is None will change color when the terminal's .fgcolor
    changes.

    If cursorchar is None, the cursor is invisible. If cursorchar is an empty
    string, the cursor does not override the character under it but does still
    draw the bgcolor under the character that is there.

    If .autoscroll is True (which it is by default) the cursor will
    automatically have the terminal scroll down when the cursor moves on from
    the last column of the last row. If .autoscroll is False the cursor will
    just stay where it is in that case.

    The Cursor's initializer automatically adds itself to the terminal's
    .cursors list. Make sure to delete it from this list when you don't need
    it anymore."""

    def __init__(self, terminal, pos=(0, 0), fgcolor=None, bgcolor=None,
                 cursorchar='▏', cursorcolorinverse=False, autoscroll=True,
                 blink=True, blinkrate=0.5, allow_wrap=True):
        self.terminal = terminal
        terminal.cursors.append(self)
        self.x, self.y = pos
        self.fgcolor = _color_name_conversion(fgcolor)
        self.bgcolor = _color_name_conversion(bgcolor)
        self.cursorcolorinverse = cursorcolorinverse
        self.autoscroll = autoscroll
        self.allow_wrap = allow_wrap
        self.blink = blink
        self.blinkrate = blinkrate
        self.cursorchar = cursorchar

        self.lastblink = None
        self.currently_blinked = False

        #This is acquired during any modification to the terminal's state;
        #drawing will block until it's not held by anyone.
        self.semaphore = threading.Semaphore(0)

    @property
    def pos(self):
        """Represents the tuple of (self.x, self.y), both for getting and
        setting."""
        return self.x, self.y
    @pos.setter
    def pos(self, newpos):
        self.x, self.y = newpos

    @property
    def fgcolor(self):
        """Foreground color of text written with this cursor. If set to a
        color name, will be converted to a tuple representing that color."""
        return self._fgcolor
    @fgcolor.setter
    def fgcolor(self,newfgcolor):
        self._fgcolor = _color_name_conversion(newfgcolor)

    @property
    def bgcolor(self):
        """Background color of cells written on with this cursor. If set to a
        color name, will be converted to a tuple representing that color."""
        return self._bgcolor
    @bgcolor.setter
    def bgcolor(self,newbgcolor):
        self._bgcolor = _color_name_conversion(newbgcolor)


    def writechar_raw(self, character):
        """Write the given character at this cursor's position and move to
        the next cell.

        This is a 'raw' way of putting characters at the cursor's position;
        smart_writechar also does things like going down to the next line
        when it sees a newline character.

        By default, if printing the character would cause the cursor to go off
        the right side of the terminal, the cursor will 'wrap' to the beginning
        of the next row; if it sees it will 'wrap' off of the bottom of the
        terminal, it will call .scroll_down() on the terminal first.

        If .autoscroll is not True, the cursor will raise
        VerticalCursorOverflow upon reaching the end of the last line. If
        .wrapping_allowed is not true, the cursor will raise
        HorizontalCursorOverflow upon reaching the end of a line.
        """
        cell = self.terminal[self.x, self.y]
        cell.character = character
        if self.fgcolor:
            cell.fgcolor = self.fgcolor
        if self.bgcolor:
            cell.bgcolor = self.bgcolor

        self.x += 1
        if self.x >= self.terminal.width:

            if not self.allow_wrap:
                #If we can't wrap, we can't wrap, just stay put and
                #raise an exception so the caller knows
                self.x = self.terminal.width - 1
                raise HorizontalCursorOverflowError(
                    "Printing '{0}' would put cursor out of bounds "
                    "horizontally."
                        .format(character))

            self.y += 1
            self.x = 0

            if self.y >= self.terminal.height:
                if self.autoscroll:
                    self.terminal.scroll_down()
                    # Go back to the beginning of the new line.
                    self.y -= 1
                    self.x = 0
                else:
                    # Going off the end of the terminal would be bad,
                    # so instead we just go back to where we just were
                    self.x = self.terminal.width - 1
                    self.y -= 1
                    #And raise an exception so the caller knows what's up
                    raise VerticalCursorOverflowError(
                        "Printing '{0}' would put cursor out of bounds "
                        "vertically."
                            .format(character))

    def process_control_character(self, character):
        r"""If character is a control character, handle it; otherwise raise
        ValueError. Code points < 0x1F (31) and 0x7f (127) are considered
        control characters, control characters other than the ones listed
        here are silently ignored and not printed.

        This is meant to be called from smart_writechar, but you can call it
        yourself if you see a reason to.

        Non-ASCII control characters such as U+200F RIGHT-TO-LEFT MARK are not
        yet supported and will be printed with the U+FFFD REPLACEMENT CHARACTER
        glyph.

        Valid control characters:
        esc. code  Hex  Decimal

        \n         0xC  10      Line feed

        Scrolls the terminal down one line. Note that Python turns CRLFs into
        \n-s automatically when reading from file-like objects or decoding
        byte strings; you _should_ be able to rely on it transparently
        converting the various newline denotations into \n-s for you.

        The terminal does not respect 0xD (carriage return) codes and silently
        ignores them like any other code < 0x1F that it does not know how to
        process.

        \t        0x9  9        Horizontal tab

        Equivalent to printing 4 spaces, unless the cursor is less than 4 spaces
        away from the end of the row, in which case we print spaces up till the
        end of the row and then move down to the next row.

        In other words, move four spaces right, or to the next line if that's
        not possible.


        Input cursors treat these next two characters differently; please see
        the docstring for InputCursor.process_control_character for more
        information.

        \x08       0x8  8       Backspace

        Replace the character at the current cursor position with a space, and
        move the cursor one space to the left.

        \x7F      0x7F  177     Delete

        Replace the character one space to the left of the current cursor
        position with a space.
        """
        # Note the r before this docstring, which among other things disables
        # the \ escape codes

        if ord(character) > 31 and character != "\x7F":
            raise ValueError("Non-control character {0} (code point > 31) "
                             "passed to process_control_character.".format(
                character))

        if character == "\n":
            self._newline()

        elif character == "\x08":
            self._backspace()

        elif character == "\x7F":
            self._delete()

        elif character == "\t":
            spaces = min(4, self.terminal.width - self.y)
            for t in range(spaces): self.writechar_raw(" ")

    def _backspace(self):
        """"Called by process_control_character to handle backspaces."""
        self.x -= 1
        if self.x < 0:
            self.y -= 1
            self.x = self.terminal.width - 1
            if self.y < 0:
                self.x = 0
                self.y = 0

        self.terminal[self.x, self.y].character = " "

    def _newline(self):
        """Called by process_control_character to handle newlines."""
        if self.y < self.terminal.height - 1:
            self.y += 1
            self.x = 0
        else:
            if self.autoscroll:
                self.terminal.scroll_down()
            self.x = 0

    def _delete(self):
        """Called by process_control_character to handle the DELETE
        character."""
        try:
            self.terminal[self.x, self.y + 1].character = " "
        except KeyError:
            pass

    def smart_writechar(self, character):
        """Write the given character at this cursor's position and move to
        the next cell unless it's a special character that must be handled
        differently, like backspace and carriage return.

        Depending on how this Cursor is configured, this may fail and raise
        CursorOverflowError-s; see the documentation for writechar_raw()."""
        try:
            # self.control_char_dispatch[character](self)
            self.process_control_character(character)
        except ValueError:
            self.writechar_raw(character)

    def pre_draw(self):
        """Called by the Terminal right before the backend draws it,
        every time its .draw() is called."""

        if self.blink:
            # The blink timer is based on the system monotonic clock
            # the monotonic goes up by 1 every 1 second, so
            # time.monotonic() - value_from_last_time_you_blinked >
            # blink_every_this_many_seconds will evaluate True every
            # that many seconds.
            if self.lastblink is None:
                # If we haven't set up the blink timer, do so.
                self.lastblink = time.monotonic()
            elif time.monotonic() - self.lastblink >= self.blinkrate:
                self.currently_blinked = not self.currently_blinked
                self.lastblink = time.monotonic()

    def should_draw(self):
        """Called by the backend; return True if the backend should actually
        draw this cursor instead of whatever it's over."""

        # if self.currently_blinked: return False
        # if self.cursorchar is None: return False
        # return True

        # Equivalent to the above
        return not (self.currently_blinked or self.cursorchar is None)


class InputCursor(Cursor):
    """Cursor that can take in text from the keyboard. If .echo is True this
    also writes inputted text to the console at its position just like a
    normal cursor with writechar.

    If input_line_mode is True, the user can't navigate the cursor around the
    screen freely; it can only move as far left (including backspaces) as it
    has right. In other words it means that you can't go and delete text
    that's already there when the program has called input(), you can only
    backspace the text you just entered."""

    def __init__(self, *args, echo=True, input_line_mode=True, **kwargs):
        self.echo = echo
        super().__init__(*args, **kwargs)
        self.buffer = []
        self.bufferposition = 0
        self.input_line_mode = input_line_mode
        self.currently_getting_line = False
        self.return_pressed = True
        self.autodraw_active = False
        # Gets incremented whenever we delete a character so we know later to
        # go back and clear any "dangling" characters from the en dof the line
        self.cleanupcount = 0

    @property
    def currently_active(self):
        """Whether the active input cursor is this cursor. Not
        settable; use activate() and finish() instead."""
        return self.terminal.active_input_cursor == self

    def activate(self):
        """Make this InputCursor the active InputCursor and begin receiving
        keypresses. Will raise InputAlreadyActiveError if another InputCursor
        is already active; wait for it to be done."""
        if self.terminal.active_input_cursor:
            raise InputAlreadyActiveError("There is already an InputCursor "
                                          "listening for keypresses on that "
                                          "terminal.")

        self.terminal.active_input_cursor = self
        self.start_pos = (self.x, self.y)
        self.buffer = []
        self.bufferposition = 0

    def writechar_raw(self, character):
        super().writechar_raw(character)
        if self.currently_active:
            self.buffer.insert(self.bufferposition, character)
            self.bufferposition += 1

    def _process_chars(self, characters):
        """Only meant to be called by the Terminal this InputCursor is part
        of. Get characters from the backend and add them to the buffer,
        doing whatever extra processing (i.e. printing them if .echo is true) is
        called for."""

        for thecharacter in characters:
            try:
                self.process_control_character(thecharacter)
            except ValueError:
                if self.echo:
                    self.smart_writechar(thecharacter)

    def _process_keys(self, keys):
        for thekey in keys:
            if thekey == "left":
                self.bufferposition -= 1
                if self.bufferposition < 0:
                    self.bufferposition = 0
                else:
                    self.x -= 1

            elif thekey == "right":
                self.bufferposition += 1
                if self.bufferposition > len(self.buffer):
                    self.bufferposition = len(self.buffer)
                else:
                    self.x += 1

    def _backspace(self):
        # If the buffer is empty and we're in "don't backspace the whole
        # screen" mode, abort
        if self.input_line_mode and not self.buffer:
            self.terminal[self.x, self.y].character = " "
            return

        del self.buffer[self.bufferposition - 1]
        self.bufferposition -= 1
        # There'll be a floating character at the end of the line, so remember
        # to write a space over it
        self.cleanupcount += 1
        super()._backspace()

    def _newline(self):
        if self.currently_getting_line:
            self.return_pressed = True
        if self.currently_active: self.buffer.append("\n")
        super()._newline()

    def finish(self):
        """Deactivate this InputCursor, allowing other InputCursor-s to
        become active, and return the contents of its buffer as a string.
        You'll want to check the .buffer for '\r' to detect the user pressing
        return; the InputCursor just treats it like any other character."""

        self.terminal.active_input_cursor = None
        return "".join(self.buffer)

    def get_line(self, fps=30):
        """Allow the user to type a line of text, returning the text
        currently there when the user presses enter. This is used instead of
        the activate() ... finish() stuff, use this if you just want to
        synchronously get a line of text, allowing the user to type it in
        wherever this InputCursor currently is and finishing and returning
        the string when the user presses Enter.

        Update_rate is the number of times per second this function should
        call its terminal's .draw()."""

        self.currently_getting_line = True
        self.return_pressed = False

        self.activate()

        while not self.return_pressed:
            self.terminal.draw()
            time.sleep(1 / fps)

        return self.finish()

    def pre_draw(self):
        if self.currently_active:
            reprintcursor = Cursor(self.terminal, self.start_pos, self.fgcolor,
                                   self.bgcolor)
            for thechar in self.buffer:
                reprintcursor.smart_writechar(thechar)

            # Write spaces over any cells on the terminal that have suddenly become
            # just past the end of our line
            for t in range(self.cleanupcount):
                reprintcursor.smart_writechar(" ")

            self.terminal.cursors.remove(reprintcursor)

        super().pre_draw()


class Cell:
    """A single cell in a terminal. Contains the character that's there,
    the foreground and background color, whether or not the cell has been
    updated since the last time the terminal has been blitted, etc..."""

    def __init__(self, terminal):
        self.terminal = terminal
        self.character = ' '
        self.fgcolor = None
        self.bgcolor = None

    @property
    def fgcolor(self):
        if self._fgcolor is None:
            return self.terminal.fgcolor
        else:
            return self._fgcolor

    @fgcolor.setter
    def fgcolor(self, newfgcolor):
        self._fgcolor = newfgcolor

    @property
    def bgcolor(self):
        if self._bgcolor is None:
            return self.terminal.bgcolor
        else:
            return self._bgcolor

    @bgcolor.setter
    def bgcolor(self, newbgcolor):
        self._bgcolor = newbgcolor


class Backend(abc.ABC):
    """The thing that actually translates a Terminal into pictures on a
    user's screen."""

    @abc.abstractmethod
    def draw(self):
        """Make the terminal show up on the screen, doing whatever needs to
        happen to make it actually visible to the user (i.e. clearing old
        debris off the screen, flipping buffers, stuff like that)"""
        pass

    @abc.abstractmethod
    def get_characters(self):
        r"""Get keypresses from the keyboard for purposes of putting
        characters on an InputCursor line. Returns a list of one-character
        strings representing each symbol-producing key (i.e. not arrow keys)
        pressed since the last call to this function.

        Alphanumeric and symbol keys should obviously correspond to their
        respective character. Pressing enter should be represented by \n
        ( chr(10) ), tab with \t, delete with \x7F, and backspace with \x08.

        All other control buttons (ex. arrow keys) will be handled through
        the get_keypresses method."""

    @abc.abstractmethod
    def get_keypresses(self, exclude_characters=True):
        """Return a list of keypress codes, representing keys the user has
        pressed since the last call to this function in the order they were
        pressed. If exclude_characters is True, which it is by default,
        this should *not* include presses that produce characters in
        get_characters()'s return list.

        This is meant as a way for applications to receive non-textual
        keypress info (i.e. a game that uses WASD for movement) as well as
        for textual applications to do things like move the input cursor with
        the arrow keys. The user accesses these through a buffer on the
        Terminal object which the Terminal appends the result of this
        function to every draw() call.

        Bear in mind that this is all done through the Terminal though,
        by calling methods on the .active_input_cursor; users aren't supposed
        to be messing with the backend directly.

        The set of valid keypress codes and what they mean is in
        pyconsolegraphics.keypress_code_set (defined in __init__.py.)"""

    @abc.abstractmethod
    def get_mouse(self):
        """Return the current position of the mouse cursor in cell
        coordinates (from (0, 0) to (W, H).) Not
        required; return (-1, -1) to signify that it isn't implemented."""

    @abc.abstractmethod
    def get_left_click(self):
        """Return True if the left mouse button has been pressed _and released_
        since the last time this function was called - NOT -  if it's currently
        being pressed. If not, or if your backend doesn't support the mouse,
        return False."""

    @abc.abstractmethod
    def get_right_click(self):
        """Return True if the _right_ mouse button has been pressed _and
        released_  since the last time this function was called - NOT -  if
        it's currently being pressed. If not, or if your backend doesn't
        support the mouse, return False."""

class Terminal:
    """Represents a virtual terminal; a grid of Unicode characters that is
    presumably going to be displayed on a screen somewhere (though you can
    also make terminals with no intention of ever blitting them to a real
    display device.)

    A Terminal is also a container; myterminal[x, y] gives the Cell object at
    (x,y). Setting items in the terminal is not supported; set the Cell's
    attributes to change the displayed character or color, etc...

    If font is none, the Terminal picks a default font. Otherwise it should
    be the name of an installed font or the full path to a TrueType font file.

    backend should be a string that is in pyconsolegraphics.backends or None;
    if it's None, pyconsolegraphics will pick one for you and will raise
    ValueError if none of them appear to work.

    A terminal can also work text I/O object. Though it does not implement
    the full TextIOBase interface, setting sys.stdin and sys.stdout to a
    Terminal should work correctly, and after doing that print() and input()
    can be used to interact with the Terminal just as in a text-mode program.

    Indeed, calling pyconsolegraphics.override_standard_io() will set this up
    for you, allowing two lines of code (the other being
    'import pyconsolegraphics') to seamlessly convert legacy text-mode
    programs to run under pyconsolegraphics.
    """

    def __init__(self, size=(80, 40), font=None, fontsize=16, backend=None,
                 bgcolor="black", fgcolor="white"):
        self.width, self.height = size
        # Note that .cells is in [y][x] order; it's a list of rows, not columns.
        self.cells = [[Cell(self) for t in range(self.width)]
                      for i in range(self.height)]
        self.bgcolor = _color_name_conversion(bgcolor)
        self.fgcolor = _color_name_conversion(fgcolor)

        self.font = font
        self.fontsize = fontsize

        self.cursors = []  # type: list[Cursor]
        self.active_input_cursor = None  # type: InputCursor

        self.autodrawactive = False

        if backend:
            self.backend = backends.backend_funcs[backend](self)
        else:
            for thebend in backend_attempt_order:
                try:
                    self.backend = backends.backend_funcs[thebend](self)
                    break
                except ImportError:
                    print("Failed to load {0} backend".format(thebend))
                    continue
            else:
                raise ImportError("None of the graphics libraries "
                                  "Pyconsolegraphics knows how to use seem to "
                                  "be installed")

    def __getitem__(self, item):
        x, y = item
        return self.cells[y][x]

    def __iter__(self):
        for therow in self.cells:
            for thecell in therow:
                yield thecell

    def blank(self):
        """Set the .character of every cell to ' ', and the .fgcolor and
        .bgcolor to None."""
        for therow in self.cells:
            for thecell in therow:
                thecell.bgcolor=None
                thecell.fgcolor=None
                thecell.character=" "

    def scroll_down(self):
        """Scroll the terminal down one line. Completely different to
        scroll(-1, 0); scroll() moves the characters in the cells, whereas
        this deletes the top row of cells and appends a blank row to the
        bottom. Much more efficient, not that that really matters."""

        self.cells.pop(0)
        self.cells.append([Cell(self) for t in range(self.width)])

    def draw(self, called_from_autodraw=False):
        """Command this terminal's backend to draw it to the screen, however
        it accomplishes that.

        If autodraw() has been called on this function, calling draw() on it
        outside of the autodraw thread does nothing."""

        # Don't want autodraw scooping up all the input
        if self.active_input_cursor and not called_from_autodraw:
            self.active_input_cursor._process_chars(
                self.backend.get_characters())
            self.active_input_cursor._process_keys(
                self.backend.get_keypresses())

        # Having two threads calling backend.draw() often makes very bad
        # things happen.
        if self.autodrawactive and not called_from_autodraw:
            return

        for thecursor in self.cursors:
            thecursor.pre_draw()

        self.backend.draw()

    def write(self, text):
        """Write the given text to the stdio cursor, creating it if it does
        not exist. This is not the recommended way to simply write text to
        the console, see ezmode.writeline for that. This exists so the
        Terminal can be used as a sys.stdout replacement."""
        if not hasattr(self, "stdiocursor"):
            self.stdiocursor = InputCursor(self)

        for thechar in text:
            self.stdiocursor.smart_writechar(thechar)

    @property
    def center(self):
        """A 2-tuple of integers representing the X, Y coordinates of the
        cell in the center of the terminal, or an approximation thereof if
        the terminal is an even number of cells in size."""
        x = self.width // 2 - 1
        y = self.height // 2 - 1

        return Pos(x, y)

    @property
    def topleft(self):
        """The 2-tuple (0, 0), in other words the coordinates of top left
        corner of the terminal."""
        return Pos(0, 0)

    @property
    def topright(self):
        """The 2-tuple (W, 0), where W is the width of the terminal,
        in other words the coordinates of the top right corner of the
        terminal."""
        return Pos(self.width - 1, 0)

    @property
    def bottomleft(self):
        """The 2-tuple (0, H - 1), where H is the height of the terminal,
        in other words the coordinates of the bottom left corner of the
        terminal."""
        return Pos(0, self.height - 1)

    @property
    def bottomright(self):
        """The 2-tuple (W - 1, H - 1), where H and W are the height and width
        of the
        terminal. In other words coordinates of the bottom right corner of the
        terminal."""
        return Pos(self.width - 1, self.height - 1)

    @property
    def topcenter(self):
        """The 2-tuple (X, 0) where X is (an approximation of) the width-wise
        center of the terminal."""
        return Pos(self.width // 2 - 1, 0)

    @property
    def bottomcenter(self):
        """The 2-tuple (X, H - 1) where X is (an approximation of) the
        width-wise center of the terminal, and H is the height of the
        terminal."""

        return Pos(self.width // 2 - 1, self.height - 1)

    @property
    def centerleft(self):
        """The 2-tuple (0, Y) where Y is (an approximation of) the height-wise
        center of the terminal."""

        return Pos(0, self.height // 2)

    @property
    def centerright(self):
        """The 2-tuple (W - 1, Y) where Y is (an approximation of) the
        width-wise center of the terminal and W is the height of the terminal."""

        return Pos(self.width - 1, self.height // 2)

    def readline(self):
        """A small part of the TextIO interface, which just so happens to be
        the part that gets called on sys.stdio by input(). In other words
        this is what lets input() be used to get input from the terminal's
        stdiocursor when the terminal is replacing stdin."""
        if not hasattr(self, "stdiocursor"):
            self.stdiocursor = InputCursor(self)

        return self.stdiocursor.get_line()

    def flush(self):
        """Called by print() on stdout under certain conditions."""
        #@TODO: This probably ought to just be a stub...
        self.draw()


def autodraw(term, fps=30):
    """Spawn a thread that draws the given terminal every 1/fps seconds,
    so you don't have to worry about calling .draw(); just put the characters
    you want on the terminal and they'll magically appear on the user's screen!
    Returns the drawing thread; feel free to just throw it out, it'll keep
    working.
    :type term Terminal
    """

    def drawfunc():
        while True:
            term.draw(called_from_autodraw=True)
            time.sleep(1 / fps)

    thethread = threading.Thread(target=drawfunc,
                                 name="pyconsolegraphics_autodraw",
                                 daemon=True)
    thethread.start()
    term.autodrawactive = True
    return thethread


def override_standard_io(**kwargs):
    """Set pyconsolegraphics up automatically so that you can use print() and
    input() just like in a console-mode application, but without the
    inconveniences that come with actually being a console-mode application.

    This creates a Terminal object, sets stdout and stdin to it, and then
    calls autodraw on it; no further manipulation is necessary, and it'll
    go away when the main program terminates.

    Takes the same keyword arguments the Terminal class takes for configuring
    the window, i.e. size, font, color, etc... or those can be omitted to
    leave them at defaults."""

    sys.stdin = sys.stdout = theterm = Terminal(**kwargs)
    autodraw(theterm)

def _color_name_conversion(x):
    """If x is in colors, return colors[x], otherwise return x."""
    try:
        return colors[x]
    except KeyError:
        return x
