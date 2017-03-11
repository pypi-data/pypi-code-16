import six

from ea.cqrs.exc import CommandFailed
from ea.exc import ImplementationError


class CommandHandlerMeta(type):

    def __new__(cls, name, bases, attrs):
        super_new = super(CommandHandlerMeta, cls).__new__
        if name in ('NewBase', 'CommandHandler'):
            return super_new(cls, name, bases, attrs)
        attrs['command_name'] = None
        attrs['__command__'] = None

        new_class = super_new(cls, name, bases, attrs)

        return new_class


class CommandHandler(six.with_metaclass(CommandHandlerMeta)):
    PHASE_PREHANDLE  = 0x001
    PHASE_HANDLE     = 0x010
    PHASE_POSTHANDLE = 0x100

    @property
    def command_class(self):
        return self.__command__

    def on_invalid(self, command):
        """Invoked when a command is received that had invalid
        parameters. The default implementation does nothing.
        """
        pass

    def on_exception(self, phase, exception, meta, command, retval=None):
        """Invoked when an exception is raised during the :meth:`handle()`
        call. It returns a boolean indicating if the exception is to be
        suppressed. The default implementation returns ``False``.
        """
        return False

    def handle(self, cmd):
        raise NotImplementedError("Subclasses must override this method.")

    def pre_handle(self, meta, cmd):
        """Hook that is executed before handling the command."""
        pass

    def post_handle(self, meta, cmd, result=None):
        """Executed after the succesful handling of a command. Here
        you can, for example, publish events.
        """
        pass

    def __call__(self, meta, cmd):
        phase = self.PHASE_PREHANDLE
        success = True
        result = None
        try:
            self.pre_handle(meta, cmd)
            phase |= self.PHASE_HANDLE
            result = self.handle(cmd)
            phase |= self.PHASE_POSTHANDLE
            self.post_handle(meta, cmd, result)
        except Exception as e:
            success = False
            if not self.on_exception(phase, e, meta, cmd, retval=result):
                raise CommandFailed(type(self).__name__, e)

        return success, result
