from __future__ import unicode_literals, print_function, absolute_import
from giles.utils import load_subcommands


for name in ('giles', 'jira', 'github'):
    load_subcommands('giles.commands.' + name)