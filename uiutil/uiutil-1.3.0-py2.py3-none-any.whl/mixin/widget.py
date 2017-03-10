
import ttk
from Tkinter import Listbox

from ..helper.layout import nice_grid
from ..widget.tooltip import ToolTip
from ..helper.event import bind_events
from ..widget.ttk_spinbox import Spinbox
from stateutil.incrementor import Incrementor


class WidgetMixIn(object):

    GRID_KWARGS = (u'row',
                   u'column',
                   u'columnspan',
                   u'sticky',
                   u'padx',
                   u'pady')

    def __init__(self,
                 parent,
                 *args,
                 **kwargs):

        self.parent = parent
        self.row = Incrementor()
        self.column = Incrementor()

    def nice_grid(self):
        nice_grid(self)

    def add_widget_and_position(self,
                                widget,
                                name=u'',
                                frame=None,
                                tooltip=None,
                                **kwargs):

        """
        Adds a widget, sets its position and adds an optional tooltip

        :param widget:
        :param name:
        :param frame:
        :param tooltip: tooltip text/function or a parameter dictionary into
                        Tooltip
        :return:
        """

        frame = frame if frame else self

        grid_kwargs = {key: value
                       for key, value in kwargs.iteritems()
                       if key in self.GRID_KWARGS}

        # Don't need to set row or column if it it's the current value
        grid_kwargs[u'row'] = grid_kwargs.get(u'row', frame.row.current)
        grid_kwargs[u'column'] = grid_kwargs.get(u'column', frame.column.current)

        widget_kwargs = {key: value
                         for key, value in kwargs.iteritems()
                         if key not in self.GRID_KWARGS}

        if name.startswith(u'__'):
            raise ValueError(u"Private names (beginning with '__') aren't"
                             u"allowed. Mangling can't be done at runtime.")

        widget_object = widget(frame,
                               **widget_kwargs)

        widget_object.grid(**grid_kwargs)

        if name:
            setattr(self,
                    name,
                    widget_object)
            setattr(widget_object,
                    u'name',
                    name)

        if tooltip:
            if not isinstance(tooltip, dict):
                tooltip = {u'text': tooltip}

            tooltip = ToolTip(widget=widget_object,
                              **tooltip)

            if name:
                setattr(self,
                        u'{name}_tooltip'.format(name=name),
                        tooltip)

            return widget_object, tooltip

        return widget_object

    def label(self,
              **kwargs):

        """
        Adds and positions a label
        """

        return self.add_widget_and_position(widget=ttk.Label,
                                            **kwargs)

    def button(self,
               **kwargs):

        """
        Adds and positions a button
        """

        return self.add_widget_and_position(widget=ttk.Button,
                                            **kwargs)

    def radio_button(self,
                     **kwargs):

        """
        Adds and positions a radio button
        """

        return self.add_widget_and_position(widget=ttk.Radiobutton,
                                            **kwargs)

    def separator(self,
                  **kwargs):

        """
        Adds and positions a separator line
        """

        return self.add_widget_and_position(widget=ttk.Separator,
                                            **kwargs)

    def combobox(self,
                 **kwargs):

        """
        Adds and positions a combobox
        """

        return self.add_widget_and_position(widget=ttk.Combobox,
                                            **kwargs)

    def entry(self,
              **kwargs):

        """
        Adds and positions a Entry field
        """

        return self.add_widget_and_position(widget=ttk.Entry,
                                            **kwargs)

    def spinbox(self,
                **kwargs):

        """
        Adds and positions a spinbox
        """

        return self.add_widget_and_position(widget=Spinbox,
                                            **kwargs)

    def checkbutton(self,
                    **kwargs):
        """
        Adds and positions a checkbutton
        """
        return self.add_widget_and_position(widget=ttk.Checkbutton,
                                            **kwargs)

    def checkbox(self,
                 **kwargs):

        """
        Adds and positions a checkbutton
        """

        return self.checkbutton(**kwargs)

    def radiobutton(self,
                    **kwargs):

        """
        Adds and positions a radiobutton
        """

        return self.add_widget_and_position(widget=ttk.Radiobutton,
                                            **kwargs)

    def progressbar(self,
                    **kwargs):

        """
        Adds and positions a progress bar
        """

        return self.add_widget_and_position(widget=ttk.Progressbar,
                                            **kwargs)

    def listbox(self,
                **kwargs):

        """
        Adds and positions a listbox
        """

        return self.add_widget_and_position(widget=Listbox,
                                            **kwargs)

    def blank_row(self):
        self.label(text=u'',
                   row=self.row.next(),
                   column=self.column.start())

    @staticmethod
    def bind_events(*args,
                    **kwargs):
        bind_events(*args, **kwargs)
