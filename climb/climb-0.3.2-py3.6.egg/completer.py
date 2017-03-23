import os
import glob
import readline


def current_argument(buffer, begin, end):
    trimmed_buffer = buffer[:end]
    position = ' '.join(trimmed_buffer.split()).count(' ')
    if trimmed_buffer.endswith(' '):
        position += 1

    space_position = buffer.rfind(' ', 0, begin)
    argument = buffer[space_position+1:end]

    return position, argument


class Completer(object):

    def __init__(self, cli):
        self._cli = cli
        self._commands = [command.name for command in self._cli.args.commands]

    def complete(self, text, state):
        buffer = readline.get_line_buffer()
        begin = readline.get_begidx()
        end = readline.get_endidx()

        position, argument = current_argument(buffer, begin, end)
        if position > 0:
            command, _ = self._cli.parse(*buffer.split())
            completer_name = self._cli.commands.get_completer(command, position)
            completer = getattr(self, completer_name)
        else:
            completer = self.commands

        completions = completer(argument, text)

        if state < len(completions):
            return completions[state]
        else:
            return None

    def commands(self, arg, text):
        commands = [c for c in self._commands
                    if c.startswith(arg)]

        if len(commands) == 1:
            return ["{} ".format(commands[0])]

        return commands

    def system_path(self, arg, text):
        glob_path = "{}*".format(os.path.expanduser(arg))

        paths = [path for path in glob.iglob(glob_path)
                 if path.startswith(arg)]

        if len(paths) == 1:
            child = paths[0].split('/')[-1]
            if os.path.isdir(paths[0]):
                return ["{}/".format(child)]
            else:
                return ["{} ".format(child)]

        return [path.split('/')[-1] for path in paths]
