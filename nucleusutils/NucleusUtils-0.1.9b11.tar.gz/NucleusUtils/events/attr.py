from NucleusUtils.events import Event

EVENT_NAME_PATTERN = '{owner}.{attribute}:changed'


class ValueEvent(Event):
    def __init__(self, name=None, reverse=False, threaded=True, value=None):
        super(ValueEvent, self).__init__(name, reverse, threaded)
        self.__value = value

    @property
    def value(self):
        return self.__value

    @value.getter
    def value_setter(self, value):
        self.__value = value
        self.trigger(value)
        return self.value


class EventAttr:
    def __init__(self, event=None):
        self.event = event

    def __get__(self, instance, owner):
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value
        self.event.trigger(value)

    def __delete__(self, instance):
        del instance.__dict__[self.name]

    def __set_name__(self, owner, name):
        self.owner = owner
        self.name = name
        self.attr_name = name

        if self.event is None:
            self.event = Event(EVENT_NAME_PATTERN.format(owner=owner.__name__, attribute=self.name))
            setattr(self.owner, self.name + '__changed', self.event)


class SpecificEventAttr(EventAttr):
    def __init__(self, validator, event=None):
        self.validator = validator
        super(SpecificEventAttr, self).__init__(event)

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value
        if self.validator(value):
            self.event.trigger(value)
