"""Wrapped around Pygame (which is itself a wrapper around SDL...) for
PyConsoleGraphics. Draws the console in a Pygame window or onto a Pygame
surface."""
import os.path
import traceback

import pygame
import pygame.freetype
from pygame.locals import *
import sys
import math

import pyconsolegraphics

def initialize_pygame():
    if pygame.freetype.was_init():
        return
    pygame.init()

keycode_to_pcg_key={
    K_BACKSPACE : "backspace",
    K_TAB : "tab",
    K_CLEAR : "clear", #the fuck is this
    K_RETURN : "enter",
    K_PAUSE : "pause",
    K_ESCAPE : "escape",
    K_SPACE : "space",
    K_EXCLAIM : "!",
    K_QUOTEDBL : '"',
    K_HASH : "#",
    K_DOLLAR : "$",
    K_AMPERSAND : "&",
    K_QUOTE: "'",
    K_LEFTPAREN : "(",
    K_RIGHTPAREN: ")",
    K_ASTERISK: "*",
    K_PLUS : "+",
    K_COMMA : ",",
    K_MINUS : "-",
    K_PERIOD : ".",
    K_SLASH : "/",
    K_0 : "0",
    K_1 : "1",
    K_2 : "2",
    K_3 : "3",
    K_4 : "4",
    K_5 : "5",
    K_6 : "6",
    K_7 : "7",
    K_8 : "8",
    K_9 : "9",
    K_COLON : ":",
    K_SEMICOLON : ";",
    K_LESS : "<",
    K_EQUALS : "=",
    K_GREATER : ">",
    K_QUESTION : "?",
    K_AT : "@",
    K_LEFTBRACKET : "[",
    K_RIGHTBRACKET : "]",
    K_BACKSLASH : "\\",
    K_CARET : "^",
    K_UNDERSCORE : "_",
    K_BACKQUOTE : "`",
    K_a: "a",
    K_b: "b",
    K_c: "c",
    K_d: "d",
    K_e: "e",
    K_f: "f",
    K_g: "g",
    K_h: "h",
    K_i: "i",
    K_j: "j",
    K_k: "k",
    K_l: "l",
    K_m: "m",
    K_n: "n",
    K_o: "o",
    K_p: "p",
    K_q: "q",
    K_r: "r",
    K_s: "s",
    K_t: "t",
    K_u: "u",
    K_v: "v",
    K_w: "w",
    K_x: "x",
    K_y: "y",
    K_z: "z",
    K_DELETE : "delete",
    K_KP0 : "0",
    K_KP1 : "1",
    K_KP2 : "2",
    K_KP3 : "3",
    K_KP4 : "4",
    K_KP5 : "5",
    K_KP6 : "6",
    K_KP7 : "7",
    K_KP8 : "8",
    K_KP9 : "9",
    K_UP: "up",
    K_DOWN : "down",
    K_RIGHT : "right",
    K_LEFT : "left",
    K_INSERT : "insert",
    K_HOME : "end",
    K_PAGEUP : "page up",
    K_PAGEDOWN : "page down",
    K_F1 : "f1",
    K_F2: "f2",
    K_F3: "f3",
    K_F4: "f4",
    K_F5: "f5",
    K_F6: "f6",
    K_F7: "f7",
    K_F8: "f8",
    K_F9: "f9",
    K_F10: "f10",
    K_F11: "f11",
    K_F12: "f12",
    K_F13: "f13",
    K_F14: "f14",
    K_F15: "f15",
    K_PRINT : "printscreen",
    K_SYSREQ : "sysrq",
    K_LSHIFT : "shift",
    K_RSHIFT : "shift",
    K_LCTRL : "control",
    K_RCTRL : "control",
    K_LALT : "alt",
    K_RALT : "alt",
    K_CAPSLOCK : "capslock",
    K_NUMLOCK : "numlock",
    K_SCROLLOCK : "scrolllock"
}

class PygameSurfaceBackend(pyconsolegraphics.Backend):
    """Pyconsolegraphics backend for a Pygame surface, which you can then
    blit wherever you want it. The surface object itself is in this object's
    .surface attribute For simpler programs you probably want
    PygameWindowBackend instead."""

    def __init__(self, term):
        self.term=term
        self.keybuffer=[]
        self.characterbuffer=[]

        self.left_click_registered = False
        self.right_click_registered = False

        initialize_pygame()

        #Load the font first so we know how big to make the window
        #Pygame makes a distinction between loading a font file and loading
        #a font whose name is known by the OS, and PCG accepts both ways of
        # specifying a font, so we must determine which one we're dealing with.
        #Unless the font is None, of course, in which case we just use a
        # default.

        if term.font is None:
            term.font=pygame.freetype.get_default_font()

        if os.path.exists(term.font):
            #It's a font file, load it
            thefont = pygame.freetype.Font(term.font, term.fontsize)
        else:
            #It's a system font, ask the system for it
            thefont = pygame.freetype.SysFont(term.font, term.fontsize)

        if thefont is None:
            raise ValueError("Failed to load font {0}".format(term.font))
        thefont.ucs4=True
        thefont.fgcolor=pygame.Color(255,255,255,255)
        thefont.origin=True
        self.font=thefont

        widths=[]
        #Since font rendering is slow, we also need to pre-generate all the
        #individual character images. fontcache.keys also serves as a set of
        #all the code points the font actually supports.
        self.fontcache={}
        for t in range(ord('A'), ord('z')):
            try:
                fontsurf, rect=self.font.render(chr(t))
                self.fontcache[chr(t)]=fontsurf
                width=rect.width
                if width:
                    widths.append(width)
            except UnicodeError:
                #Failure to deal with a code point is not really a
                # problem but worth noting
                traceback.print_last(file=sys.stdout)
                continue

        self.cellwidth = math.ceil( sum(widths) / len(widths)) + 3
        self.cellheight = self.font.get_sized_glyph_height()

        #Now fire up the surface (or window if we're a PygameWindowBackend)
        # we'll be rendering to...
        self.initialize_surface(self.cellwidth * term.width,
                                self.cellheight * term.height)

    def initialize_surface(self, w, h):
        """This is separate from __init__ because PygameWindowBackend will
        override it; this initializes the in-memory-only or display surface
        we'll be drawing out terminal to."""
        #If he's using PygameSurfaceBackend straight up, then presumably the
        # user knows what he's doing; just put the surface in our .surface
        # attr and let him get it out when he needs it.

        self.surface=pygame.Surface((w, h))

    def draw(self):
        #Do some housekeeping while we're at it
        pygame.event.pump()

        cellrect = pygame.Rect(0, 0, self.cellwidth, self.cellheight)
        fontcache=self.fontcache

        cursorposes={(thecursor.x,thecursor.y) : thecursor for thecursor in
                     self.term.cursors}
        termfg, termbg = self.term.fgcolor, \
                         self.term.bgcolor

        for y, thecolumn in enumerate(self.term.cells):
            for x, thecell in enumerate(thecolumn):
                if not thecell.dirty: continue
                thecell.dirty = False
                cellrect.topleft = (x*self.cellwidth, y*self.cellheight)

                textrect=cellrect.copy()
                textrect.y += self.cellheight // 1.5

                #Cursors override the text under them (unless they... don't.)
                if (x,y) in cursorposes and cursorposes[x,y].should_draw():
                    thecursor=cursorposes[x,y]

                    #the cursorchar being "" means we should draw the regular
                    # character but with the cursor's bgcolor
                    if thecursor.cursorchar == "":
                        character=thecell.character
                    else:
                        character=thecursor.cursorchar

                    #if the cursor has no color draw with the cell's color, but
                    fgcolor = thecursor.fgcolor if thecursor.fgcolor \
                                                else thecell.fgcolor
                    bgcolor = thecursor.bgcolor if thecursor.bgcolor \
                                                else thecell.bgcolor

                else:
                    fgcolor=thecell.fgcolor
                    bgcolor=thecell.bgcolor
                    character=thecell.character

                #if the cell has no color then draw with the term's color
                if not fgcolor: fgcolor = termfg
                if not bgcolor: bgcolor = termbg

                #put a rect in the bgcolor behind it...
                pygame.draw.rect(self.surface,bgcolor,cellrect)

                if character:
                    self.font.render_to(self.surface,textrect, character,
                                        fgcolor=fgcolor)

        pygame.display.flip()

    def _process_events(self):
        for theevent in pygame.event.get():
            if theevent.type is pygame.KEYDOWN:
                if theevent.unicode:

                    #Pygame gives us \rs when enter is pressed, we need \ns.
                    if theevent.unicode == "\r":
                        self.characterbuffer.append("\n")
                    else:
                        self.characterbuffer.append(theevent.unicode)

                else:
                    # Also note down the key events for calls to get_keypresses.
                    try:
                        self.keybuffer.append(keycode_to_pcg_key[theevent.key])
                    except KeyError:
                        print("Unknown non-character keypress {0}".format(
                            theevent), file=sys.__stderr__)

            if theevent.type is pygame.MOUSEBUTTONUP:
                if theevent.button == 1:
                    self.left_click_registered = True
                elif theevent.button == 3:
                    self.right_click_registered = True

    def get_characters(self):
        """Get keypresses from the keyboard for purposes of putting
        characters on an InputCursor line. Returns a list of one-character
        strings, which may be empty."""

        self._process_events()

        retlist = self.characterbuffer.copy()
        self.characterbuffer.clear()

        return retlist

    def get_keypresses(self):
        """Return a list of keypress codes, representing keys the user has
        pressed since the last call to this function in the order they were
        pressed. If exclude_characters is True, which it is by default,
        this should *not* include presses that produce characters in
        get_characters()'s return list.
        """
        self._process_events()
        rlist = self.keybuffer.copy()
        self.keybuffer.clear()
        return rlist

    def get_mouse(self):
        return self._px_to_cell(pygame.mouse.get_pos())

    def get_left_click(self):
        self._process_events()
        state = self.left_click_registered
        self.left_click_registered = False
        return state

    def get_right_click(self):
        self._process_events()
        state = self.right_click_registered
        self.right_click_registered = False
        return state

    def _px_to_cell(self, pxpos):
        """Internal function. Given a pixel position, return the coordinates
        of the cell that it's in."""
        x, y = pxpos
        x = x // self.cellwidth + 1
        y = y // self.cellheight + 1

        x = max(0, min(self.term.width,  x))
        y = max(0, min(self.term.height, y))

        return x, y

class PygameWindowBackend(PygameSurfaceBackend):
    """Pyconsolegraphics backend that renders the terminal to a window using
    the Pygame SDL wrapper."""

    def initialize_surface(self, w, h):
        """Get a Pygame display surface."""
        self.surface=pygame.display.set_mode((w, h))