from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError
import logging
import warnings

import ioc

from ea.cqrs.exc import CommandHandlingTimeout
from ea.cqrs.exc import CommandFailed
from ea.cqrs.exc import CommandRejected
from ea.cqrs.command.result import ICommandResult


class ICommandRunner(object):
    logger = logging.getLogger('ea.cqrs.command')
    storage = ioc.class_property('CommandStore')
    run_exception_fatal = False

    def __init__(self, storage=None):
        if storage is None:
            warnings.warn("Injecting CommandStore is deprecated.",
				DeprecationWarning)
        else:
            ioc.provide('CommandStore', storage, force=True)

    def get_result(self, handler, meta, command):
        """Execute a command request. This method may either run
        the handler(s) locally, or defer it to a remote host. It
        must return an implementation of :class:`ICommandResult`.
        """
        raise NotImplementedError("Subclasses must override this method.")

    def handle(self, handler, meta, command):
        """Handles a command and does additional housekeeping."""
        success = False
        result = None
        exc = None
        try:
            self.storage.persist(handler.command_class, meta, command)
            success, result = handler(meta, command.params)
        except CommandFailed as e:
            exc = e
            self.logger.exception("Failed to execute command %s", meta.id)
            if self.run_exception_fatal:
                raise e.exc

        return result or exc, success

    def run(self, request, handler):
        command = request.get_command(handler.command_class)
        if not command.is_valid():
            handler.on_invalid(command)
            raise CommandRejected(request, command, reason='invalid_parameters')

        return self.result_class(*self.get_result(handler, request.meta, command))


class LocalCommandRunner(ICommandRunner):
    """An :class:`ICommandRunner` that executes a command in the local
    thread.
    """
    class result_class(ICommandResult):

        def __init__(self, result, exception):
            self.result = result
            self.exception = exception

        def wait(self, timeout=None):
            if self.exception:
                raise self.exception
            return self.result

    def get_result(self, handler, meta, command):
        return self.handle(handler, meta, command)


class ProviderCommandRunner(LocalCommandRunner):

    def __init__(self, provider):
        self.provider = provider

    def run(self, request, *args, **kwargs):
        return super(ProviderCommandRunner, self).run(request,
            request.get_handler(self.provider))


class ThreadedCommandRunner(ICommandRunner):
    """A :class:`ICommandRunner` implementation that executes commands
    in separate threads.
    """

    class result_class(ICommandResult):

        def __init__(self, promise):
            self.promise = promise

        def then(self, fn):
            self.promise.add_done_callback(fn)

        def wait(self, timeout=None):
            return None
            if timeout is not None:
                timeout /= 1000
            try:
                result, exception =  self.promise.result(timeout=timeout)
                if exception is not None:
                    raise exception

                return result
            except TimeoutError:
                raise CommandHandlingTimeout

    def __init__(self, max_workers=5, *args, **kwargs):
        super(ThreadedCommandRunner, self).__init__(*args, **kwargs)
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def get_result(self, handler, meta, command):
        return [self.executor.submit(self.handle, handler, meta, command)]


class ThreadedProviderCommandRunner(ThreadedCommandRunner):
    run_exception_fatal = True

    def __init__(self, provider, *args, **kwargs):
        super(ThreadedProviderCommandRunner, self).__init__(*args, **kwargs)
        self.provider = provider

    def run(self, request, *args, **kwargs):
        return super(ThreadedProviderCommandRunner, self).run(request,
            request.get_handler(self.provider))
