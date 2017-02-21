
from Tkinter import NORMAL, DISABLED

from ..mixin import AllMixIn
from stateutil.switch import Switch as _Switch


class Switch(AllMixIn,
             _Switch):

    TEXT = u'text'

    def __init__(self,
                 frame,
                 switch_object=None,
                 trace=None,
                 link=None,
                 switch_state=None,
                 **kwargs):

        super(Switch, self).__init__(parent=frame, **kwargs)

        if switch_state is None:
            # Set a default switch state
            switch_state = self.ON

        elif switch_state not in [self.ON, self.OFF]:
            raise ValueError(u'Switch state should be one of Switch.ON or Switch.OFF!')

        self._state = switch_state  # initialise the base classes state param
        self.link = link
        self.text = kwargs[Switch.TEXT]
        self.switch_object = switch_object if switch_object else self.text

        if self.link:
            self._var = self.boolean_var(link=self.link)

        else:
            self._var = self.boolean_var(value=switch_state,
                                         trace=trace)

        # Setup trace on self.var to update self._state
        # We have to do this as we are using a Tk variable instead of base classes self._state
        # however for switch_on/off to work we have to keep these in sync.
        self._var.trace(u"w", lambda: self.__update_state())

        self.switch = self.checkbutton(frame=frame,
                                       variable=self._var,
                                       onvalue=self.ON,
                                       offvalue=self.OFF,
                                       **kwargs)

    def __update_state(self):
        self._state = self._var.get()

    def _switch_on_action(self):
        # Synchronise self.state & self._var as with trace above
        self._var.set(self._state)

    def _switch_off_action(self):
        # Synchronise self.state & self._var as with trace above
        self._var.set(self._state)

    def enable(self):
        self.switch.config(state=NORMAL)

    def disable(self):
        self.switch.config(state=DISABLED)

    @property
    def object(self):
        return self.switch_object
