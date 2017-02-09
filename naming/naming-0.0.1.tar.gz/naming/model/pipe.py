# -*- coding: utf-8 -*-
"""
The pipe module.
"""
# package
from .base import Name


class Pipe(Name):
    """docstring for Pipe"""

    def _set_values(self):
        super(Pipe, self)._set_values()
        self._version = '\d+'
        self._output = '[a-zA-Z0-9]+'
        self._frame = '\d+'
        self._pipe = rf'(({self._separator_pattern}{self._output})?[.]{self._version}([.]{self._frame})?)'

    def _set_patterns(self):
        super(Pipe, self)._set_patterns()
        self._set_pattern('pipe', 'output', 'version', 'frame')

    def _get_joined_pattern(self):
        return rf'{super(Pipe, self)._get_joined_pattern()}{self._pipe}'

    @property
    def pipe_name(self):
        try:
            return rf'{self.nice_name}{self.pipe}'
        except AttributeError:
            return rf'{self.nice_name}{self.separator}[pipe]'

    def _filter_k(self, k):
        return k == 'pipe'

    def get_name(self, **values):
        if not values and self.name:
            return super(Pipe, self).get_name(**values)
        if 'pipe' in values:
            pipe = values['pipe'] or ''
        else:
            if 'version' in values:
                version = rf'{values["version"]}'
            else:
                version = getattr(self, 'version', None)
                if version is not None:
                    version = rf'{version}'

            if 'output' in values or 'frame' in values:
                if 'output' in values:
                    output = rf'{values["output"]}'
                else:
                    output = getattr(self, 'output', None)
                    if output:
                        output = rf'{output}'

                if 'frame' in values:
                    frame = rf'{values["frame"]}'
                else:
                    frame = getattr(self, 'frame', None)
                    if frame is not None:
                        frame = rf'{frame}'

                if version is output is frame is None:
                    suffix = rf'{self.separator}[pipe]'
                    pipe = self.pipe or suffix if self.name else suffix
                else:
                    pipe = rf'.{version or "[version]"}'
                    if output or frame:
                        pipe = rf'{self.separator}{output or "[output]"}{pipe}'
                        if frame:
                            pipe = rf'{pipe}.{frame}'
            else:
                if version is None:
                    suffix = rf'{self.separator}[pipe]'
                    pipe = self.pipe or suffix if self.name else suffix
                else:
                    suffix = rf'.{version}'
                    pipe = self.pipe or suffix if self.name else suffix

        return rf'{super(Pipe, self).get_name(**values)}{pipe}'
