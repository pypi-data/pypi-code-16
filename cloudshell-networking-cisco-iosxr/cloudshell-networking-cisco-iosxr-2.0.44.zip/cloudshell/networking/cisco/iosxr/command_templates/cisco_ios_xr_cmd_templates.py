from collections import OrderedDict
from cloudshell.cli.command_template.command_template import CommandTemplate

COMMIT_REPlACE = CommandTemplate(command="commit replace")

LOAD = CommandTemplate(command="load {source_file} [vrf {vrf}]", action_map=OrderedDict({
    '[\[\(][Yy]es/[Nn]o[\)\]]|\[confirm\]': lambda session: session.send_line('yes'),
    '\(y\/n\)': lambda session: session.send_line('y'),
    '[\[\(][Yy]/[Nn][\)\]]': lambda session: session.send_line('y'),
    'overwrit+e': lambda session: session.send_line('yes'),
    'Do you wish to proceed': lambda session: session.send_line('yes')
}))


