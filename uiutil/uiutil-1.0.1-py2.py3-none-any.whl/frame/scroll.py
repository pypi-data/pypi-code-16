
import ttk
from Tkconstants import VERTICAL, HORIZONTAL, RIGHT, Y, BOTTOM, X, LEFT, BOTH, YES, NW
from Tkinter import Canvas, Scrollbar

from frame import BaseFrame

# TODO: WORK IN PROGRESS


# TODO: Add options to disable h/v scrollbars!
class BaseScrollFrame(BaseFrame):

    def __init__(self, parent=None, *args, **kwargs):

        BaseFrame.__init__(self, parent=parent, *args, **kwargs)

        self._canvas = Canvas(self, borderwidth=0, highlightthickness=0)
        self.canvas_frame = ttk.Frame(self)

        self._vbar = Scrollbar(self,
                               orient=VERTICAL,
                               command=self._canvas.yview)

        self._hbar = Scrollbar(self,
                               orient=HORIZONTAL,
                               command=self._canvas.xview)

        self._canvas[u'yscrollcommand'] = self._vbar.set
        self._canvas[u'xscrollcommand'] = self._hbar.set

        self._vbar.pack(side=RIGHT, fill=Y)
        self._hbar.pack(side=BOTTOM, fill=X)
        self._canvas.pack(side=LEFT, fill=BOTH, expand=YES)
        self._canvas_window = \
            self._canvas.create_window((0, 0),
                                       window=self.canvas_frame,
                                       anchor=NW)

        self.canvas_frame.bind("<Configure>",
                               self.on_frame_configure)

        # reset the view
        self._canvas.xview_moveto(0)
        self._canvas.yview_moveto(0)

        # track changes to the canvas and frame width
        # and sync them, also updating the scrollbar
        def _configure_interior(event):

            # update the scrollbars to match the size of the inner frame
            size = (self.canvas_frame.winfo_reqwidth(),
                    self.canvas_frame.winfo_reqheight())

            self._canvas.config(scrollregion=u"0 0 %s %s" % size)

            if self.canvas_frame.winfo_reqwidth() != self._canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                self._canvas.config(width=self.canvas_frame.winfo_reqwidth())

        self.canvas_frame.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):

            if self.canvas_frame.winfo_reqwidth() != self._canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                if self._canvas.winfo_width() > \
                 self.canvas_frame.winfo_reqwidth():

                    self._canvas.itemconfigure(
                        self._canvas_window,
                        width=self._canvas.winfo_width())
                else:
                    self._canvas.itemconfigure(
                        self._canvas_window,
                        width=self.canvas_frame.winfo_reqwidth())

        self._canvas.bind('<Configure>', _configure_canvas)

    def on_frame_configure(self, event):
        """Reset the scroll region to encompass the inner frame"""
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

""" Alternate testing scroll frame code

from Tkinter import *

def update_canvas(event):
    canvas.config(width=frame.winfo_width())
    canvas.configure(scrollregion=canvas.bbox(ALL))

# Setup Window
root=Tk()
root.wm_geometry("500x500+500+500")

# Place a frame in window
myframe=Frame(root, borderwidth=1, background=u'#123456', padx=5, pady=5)
myframe.grid(sticky=NSEW)
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)

# Create Canvas on frame
canvas=Canvas(myframe, background=u'#FFFF88', highlightthickness=0)

# Add a frame to be used for placing widgets
frame=Frame(canvas, borderwidth=1, background=u'#654321')
w = canvas.create_window((0,0), window=frame, anchor=NW)

# Update the canvas whenever the frame changes
frame.bind("<Configure>", update_canvas)

# Add vertical scrollbar
myscrollbar=Scrollbar(myframe, orient=VERTICAL,command=canvas.yview)
myscrollbar.pack(side=RIGHT,fill=Y)
canvas.configure(yscrollcommand=myscrollbar.set)

# Add horizontal scrollbar
myscrollbar2=Scrollbar(myframe, orient=HORIZONTAL,command=canvas.xview)
myscrollbar2.pack(side=BOTTOM,fill=X)
canvas.configure(xscrollcommand=myscrollbar2.set)

# Place the canvas
canvas.pack(side=LEFT, fill=BOTH, expand=YES)

# Add data to usable frame
for i in range(50):
    Label(frame, text=i).grid(row=i, column=0)
    Label(frame, text="my text" + str(i)).grid(row=i, column=1)
    Label(frame, text="..........").grid(row=i, column=2)

root.update_idletasks()

print root.winfo_geometry()
print myframe.winfo_geometry()
print canvas.winfo_geometry()
print
print myframe.winfo_width()
print myframe.winfo_height()
print
print frame.winfo_reqwidth()
print frame.winfo_reqheight()

root.mainloop()

"""
