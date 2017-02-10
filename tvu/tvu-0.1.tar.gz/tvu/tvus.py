from tvu._tvu import TVU
from tvu._compat import text


def bounded_int(minimum=None, maximum=None):

    class BoundedInt(TVU):

        TYPES = (int, float)

        def unify(self, value):
            if isinstance(value, float) and round(value) != value:
                self.error(u'a round number')
            return int(value)

        def validate(self, value):
            if minimum is not None and maximum is not None\
               and not (minimum <= value <= maximum):
                err_msg = \
                    u'an integer between %d and %d (inclusive)' % (minimum,
                                                                   maximum)
                self.error(err_msg)
            elif minimum is not None and value < minimum:
                err_msg = u'an integer greater or equal to %d' % (minimum,)
                self.error(err_msg)
            elif maximum is not None and value > maximum:
                err_msg = u'an integer lesser or equal to %d' % (maximum,)
                self.error(err_msg)

    return BoundedInt

PositiveInt = bounded_int(minimum=1)


class Iterable(TVU):

    def type_check(self):
        value = self._value
        try:
            iter(value)
            return
        except TypeError:
            err_msg = u'%s must be iterable, not %s' % (self._variable_name,
                                                        text(self._value))
            raise TypeError(err_msg)


class Text(TVU):

    TYPES = (text, bytes)

    def error(self, msg, soft=False):
        word = u'could' if soft else u'must'
        # skip adding unicode(value) to err_msg because there are problems
        # converting it to unicode
        raise ValueError((u'%s %s be ' + msg) % (self._variable_name, word))

    def unify(self, value):
        if isinstance(value, bytes):
            try:
                return value.decode('ascii')
            except UnicodeDecodeError:
                self.error(u'unicode text, or ascii-only bytestring')
        return value


class NonEmptyText(Text):

    def validate(self, value):
        if value is u'':
            self.error(u'non-empty string')
