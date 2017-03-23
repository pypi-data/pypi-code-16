
import ttk
from Tkinter import W, EW

from uiutil.mixin.var import VarMixIn
from uiutil.frame.frame import BaseFrame
from uiutil.window.root import RootWindow
from ..validation import valid_ipv4, valid_ipv6


class IPEntry(VarMixIn,
              ttk.Entry):

    def __init__(self,
                 master=None,
                 ipv6=False,
                 allow_invalid_values=True,
                 initial_value=None,
                 **kwargs):

        self.allow_invalid_values = allow_invalid_values
        self.ipv6 = ipv6

        if initial_value is None:
            initial_value = u'::' if self.ipv6 else u'0.0.0.0'

        if u'textvariable' in kwargs:
            self.text = self.string_var(link=kwargs.pop(u'textvariable'))

        else:
            self.text = self.string_var(value=initial_value)

        ttk.Entry.__init__(self,
                           master=master,
                           textvariable=self.text,
                           **kwargs)

        registered_validate_ip = self.register(self.validate_ip)

        self[u'validate'] = u"key",
        self[u'validatecommand'] = (registered_validate_ip, u"%P")

    def get(self):
        return self.text.get()

    def set(self,
            value):
        return self.text.set(value)

    def validate_ip(self,
                    ip):

        valid_ip = valid_ipv6(ip) if self.ipv6 else valid_ipv4(ip)

        self.config(foreground=u'black' if valid_ip else u'red')

        return True if self.allow_invalid_values else valid_ip


class IPTestFrame(BaseFrame):

    def __init__(self,
                 *args,
                 **kwargs):

        BaseFrame.__init__(self, *args, **kwargs)

        self.label(text=u'IPv4:',
                   row=self.row.next(),
                   column=self.column.start(),
                   sticky=W)

        self.__ipv4_field = IPEntry(self,
                                    width=len(u'255.255.255.255'))
        self.__ipv4_field.grid(row=self.row.current,
                               column=self.column.next(),
                               sticky=W)

        self.label(text=u'IPv6:',
                   row=self.row.next(),
                   column=self.column.start(),
                   sticky=W)

        self.__ipv6_field = IPEntry(self,
                                    ipv6=True,
                                    width=len(u'abcd:abcd:abcd:abcd:abcd:abcd:abcd:abcd'))
        self.__ipv6_field.grid(row=self.row.current,
                               column=self.column.next(),
                               sticky=W)


class DeviceIPEntryTest(RootWindow):

    def __init__(self, *args, **kwargs):
        super(DeviceIPEntryTest, self).__init__(*args, **kwargs)

    def _setup(self):

        self.title(u"Test Device Frame")
        self.ip_frame = IPTestFrame(parent=self._main_frame)
        self.ip_frame.grid(sticky=EW)


if __name__ == u'__main__':
    DeviceIPEntryTest()
