import os
import sys

class BaseGPIO:
    @property
    def value(self):
        raise NotImplementedError()
    @value.setter
    def value(self, value):
        raise NotImplementedError()

    @property
    def direction(self):
        raise NotImplementedError()
    @direction.setter
    def direction(self, direction):
        raise NotImplementedError()

class LinuxGPIO(BaseGPIO):
    attributes = ('value', 'direction', 'active_low')

    def __init__(self, index):
        self.index = index
        self._file = {}
        self.export = True

    @property
    def path(self):
        return '/sys/class/gpio/gpio{:d}/'.format(self.index)

    @property
    def export(self):
        return os.path.exists(self.path)

    @export.setter
    def export(self, export):
        exported = self.export
        if   export and not exported:
            with open("/sys/class/gpio/export",   'w') as h:
                h.write(str(self.index))
        elif not export and exported:
            with open("/sys/class/gpio/unexport", 'w') as h:
                h.write(str(self.index))
        if export and not len(self._file):
            for name in self.attributes:
                self._file[name] = open(
                    os.path.join(self.path, name), 'w+b',
                    buffering=0)
        elif not export:
            for h in self._file.values():
                h.close()
            self._file.clear()

    def _write(self, name, data):
        file = self._file[name]
        file.seek(0)
        file.write(data)

    def _read(self, name):
        file = self._file[name]
        file.seek(0)
        return file.read()

    @property
    def value(self):
        return int(self._read("value"))
    @value.setter
    def value(self, value):
        self._write("value",
                    str(value).encode('ascii'))

    @property
    def direction(self):
        return self._read("direction").decode('ascii').strip()
    @direction.setter
    def direction(self, direction):
        self._write("direction",
                    direction.encode('ascii'))

    @property
    def active_low(self):
        return int(self._read("active_low"))
    @active_low.setter
    def active_low(self, active_low):
        self._write("active_low",
                    str(active_low).encode('ascii'))

