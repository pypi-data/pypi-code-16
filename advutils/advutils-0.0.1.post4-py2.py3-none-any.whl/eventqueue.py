"""
This module define event classes for queueing tasks
"""

from __future__ import print_function

from builtins import object


class Event(object):
    """
    Class defining an event
    """

    def __init__(self, doc=None):
        self.__doc__ = doc

    def sender(self, obj, objtype=None):
        if obj is None:
            return self
        return EventHandler(self, obj)

    def __set__(self, obj, value):
        pass
    __get__ = sender


class EventHandler(object):
    """
    Class to handle an Event instance
    """

    def __init__(self, event, sender):

        self.event = event
        self.sender = sender

    def _getfunctionlist(self):
        """(internal use) """

        try:
            eventhandler = self.sender.__eventhandler__
        except AttributeError:
            eventhandler = self.sender.__eventhandler__ = {}
        return eventhandler.setdefault(self.event, [])

    def append(self, func):
        """Add new event handler function.

        Event handler function must be defined like func(sender, earg).
        You can add handler also by using '+=' operator.
        """
        self._getfunctionlist().append(func)
        return self

    def remove(self, func):
        """Remove existing event handler function.

        You can remove handler also by using '-=' operator.
        """

        self._getfunctionlist().remove(func)
        return self

    def fire(self, *args, **kwargs):
        """
        Fire event and call all handler functions. You can call EventHandler
        object itself like `self(*args,**kwargs)` instead of
        `self.fire(*args,**kwargs)`.
        """

        for func in self._getfunctionlist():
            func(self.sender, *args, **kwargs)

    __iadd__ = append
    __isub__ = remove
    __call__ = fire


if __name__ == "__main__":

    class MockFileWatcher(object):
        #fileChanged = Event()
        def __init__(self, source_path):
            self.fileChanged = Event("this is a event").sender(self)
            self.source_path = source_path

        def changePath(self, source_path):
            self.fileChanged(source_path)
            self.source_path = source_path

    def log_file_change(Sender, source_path):
        if not Sender.source_path == source_path:
            print(
                "{} >>> Source path '{}' changed to '{}'.".format(
                    Sender,
                    Sender.source_path,
                    source_path))

    def log_file_change2(Sender, source_path):
        print("{} >>> {} inserted!".format(Sender, source_path))

    watcher = MockFileWatcher("Toro")
    watcher.fileChanged += log_file_change2
    watcher.fileChanged += log_file_change
    watcher.fileChanged += log_file_change
    watcher.fileChanged -= log_file_change
    watcher.changePath("foo")
    watcher.changePath("foo")
    watcher.changePath("cabra")
