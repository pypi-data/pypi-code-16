# -*- coding: utf-8 -*-
import subprocess
from watson.mail.backends import abc


class Sendmail(abc.Base):
    """Send an email via the `sendmail` command.
    """

    command = None

    def __init__(self, command='sendmail'):
        self.command = command

    def send(self, message):
        command, message_string = self._prepare_command(self.command, message)
        try:
            process = subprocess.Popen(
                command,
                shell=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE)
        except (IOError, OSError):
            raise Exception('Unable to open pipe to sendmail.')
        try:
            process.stdin.write(message_string.encode(message.encoding))
            process.stdin.close()
        finally:
            while process.poll() is None:
                process.stdout.read(100)
            process.stdout.close()

    def _prepare_command(self, command, message):
        prepared = message.prepared
        prepared['From'] = str(message.senders.from_.email)
        message_string = prepared.as_string()
        command = '{0} {1}'.format(command, str(message.recipients.to))
        return command, message_string
