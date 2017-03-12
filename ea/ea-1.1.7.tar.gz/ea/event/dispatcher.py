from concurrent.futures import ThreadPoolExecutor
import logging

from ea.lib.datastructures import ImmutableDTO


class BaseEventDispatcher:
    """The base class for all event dispatchers."""
    logger = logging.getLogger('eda.dispatcher')

    def __init__(self, provider):
        self.provider = provider

    def dispatch(self, event):
        self.logger.debug("Dispatching event %s (type: %s)", event.id, event.type)

        listeners = self.provider.get(event)
        for listener, params in listeners:
            self.run_listener(self.handle, listener,
                ImmutableDTO(headers=event.headers, params=params))

    def run_listener(self, runner, listener, dto):
        raise NotImplementedError("Subclasses must override this method.")

    def handle(self, listener, dto):
        try:
            listener(dto)
            self.logger.debug("Finished running listener %s for event %s",
                type(listener).__name__, dto.headers.id)
        except Exception as e:
            self.logger.exception("Caught fatal exception during event handling.")
            raise

    def join(self, *args, **kwargs):
        """Block until all listeners have finished handling an
        event. The default implementation does nothing.
        """
        return


class LocalEventDispatcher(BaseEventDispatcher):

    def run_listener(self, runner, listener, dto):
        runner(listener, dto)


class ThreadedEventDispatcher(BaseEventDispatcher):
    max_workers = 20

    def __init__(self, provider):
        super(ThreadedEventDispatcher, self).__init__(provider)
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)

    def run_listener(self, runner, listener, dto):
        self.executor.submit(runner, listener, dto)

    def join(self, *args, **kwargs):
        return self.executor.shutdown(*args, **kwargs)
