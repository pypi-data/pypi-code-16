from proton.reactor import EventInjector
from proton.reactor import ApplicationEvent


class EventInjectorMixin:
    event_class = ApplicationEvent

    def __init__(self, injector=None):
        self.injector = injector or EventInjector()

    def on_start(self, event):
        event.container.selectable(self.injector)

    def event(self, typename, **kwargs):
        self.injector.trigger(self.event_class(typename, **kwargs))

