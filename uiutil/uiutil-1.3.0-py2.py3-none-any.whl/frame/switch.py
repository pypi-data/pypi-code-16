
from Tkinter import NORMAL, EW
from collections import OrderedDict

from ..widget.switch import Switch
from ..frame.label import BaseLabelFrame
from stateutil.persist import Persist


class BaseSwitchFrame(BaseLabelFrame):

    switch_widget = Switch

    def __init__(self,
                 title,
                 switches,
                 switch_states=None,
                 link=None,
                 width=None,
                 sort=True,
                 *args,
                 **kwargs):

        """
        :param title:
        :param switches:      A list of switch names or, if the switch objects
                              and labels are different, a dictionary:

                                  {"switch label": <switch object>,
                                   ...
                                   "switch label": <switch object>}

        :param switch_widget: A Switch object (or a subclass)
        :param link:          A Persist object (or subclass)
        :param switch_states: Initial switch states, a dictionary:

                                  {"switch label": <switch state>,
                                    ...
                                   "switch label": <switch state>}
        :param args:
        :param kwargs:
        """

        super(BaseSwitchFrame, self).__init__(*args, **kwargs)

        self._set_title(title=title)

        if not isinstance(switches, dict):
            # Only label labels, so make a dictionary
            # using those labels as the objects
            temp = OrderedDict()

            for switch in switches:
                # key=label: object=None
                temp[switch] = None

            switches = temp

        if sort:
            self.switches = OrderedDict(sorted(switches.items(),
                                               key=lambda t: t[0]))

        else:
            self.switches = switches

        self.switch_states = {} if switch_states is None else switch_states

        self.link = link

        if self.link:
            self.switch_states.update(self.link.get())
            self.link.set(self.switch_states)

        for switch_label, switch_widget in self.switches.iteritems():

            command = (lambda sw=switch_label: self.state_change(sw))

            switch_link = Persist(persistent_store=self.switch_states,
                                  key=switch_label,
                                  initial_value=self.switch_states.get(switch_label, Switch.ON))

            if switch_widget is None:
                # Initialise the widget if we weren't provided with one
                self.switches[switch_label] = self.switch_widget(frame=self,
                                                                 text=switch_label,
                                                                 state=NORMAL,
                                                                 width=width,
                                                                 command=command,
                                                                 link=switch_link,
                                                                 row=self.row.next(),
                                                                 column=self.column.start(),
                                                                 sticky=EW)

    def state_change(self,
                     switch):

        if self.switched_on(switch):
            self.switch_on(switch)

        else:
            self.switch_off(switch)

        if self.link:
            self.link.set(self.switch_states)

    def switch_state(self,
                     switch):
        return self.switches[switch].state

    def switched_on(self,
                    switch):
        return self.switches[switch].switched_on

    def switched_off(self,
                     switch):
        return self.switches[switch].switched_off

    def switch_on(self,
                  switch):

        """
        Override this method to take action when the
        state of a switch changes to on if the actions needs
        to be at the switch array level, otherwise override
        switch_on in the switch_widget
        """

        self.switches[switch].switch_on()

    def switch_off(self,
                   switch):

        """
        Override this method to take action when the
        state of a switch changes to off if the actions needs
        to be at the switch array level, otherwise override
        switch_off in the switch_widget
        """

        self.switches[switch].switch_off()

    @property
    def get_switched_on_list(self):
        return [switch for switch in self.switches if self.switched_on(switch)]

    def enable_all(self):
        for switch in self.switches.values():
            switch.enable()

    def disable_all(self):
        for switch in self.switches.values():
            switch.disable()
