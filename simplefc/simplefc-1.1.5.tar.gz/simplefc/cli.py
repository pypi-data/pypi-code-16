"""
simplefc (simple flash card)

Usage:
  simplefc [-h | --help]
  simplefc [-v | --version]
  simplefc create_set <setname>
  simplefc add_entry <setname> (-M <entry>... | -F <file>...)
  simplefc study [-tdbamfsr] <setname>
  simplefc view_set <setname>
  simplefc view_archive <setname>
  simplefc unarchive <setname> <ID>...
  simplefc delete_entry <setname> <ID>...
  simplefc list_sets
  simplefc delete_set <setname>
  simplefc view_dbpath
  simplefc change_dbpath <newpath>
  simplefc reset_data <setname>

Arguments:
  <setname>      The name of a simplefc flashcard set. Cannot 
                 contain spaces or special characters. Must begin 
                 with a letter. Use '.' in place of a setname with 
                 the 'study' command to study all sets at once.
  <entry>        An entry of the form 'term;;definition'.
  <file>         A text file containing unquoted entries of the 
                 above form. Each entry must have its own line.
  <ID>           The identification number of an entry.
  <newpath>      The location of simplefc's database file. Use 
                 'default' to restore the default location.

Options:
  -h --help      Show this page.
  -v --version   Show version.
  -M             Add entries manually.
  -F             Add entries from a file.
  -t             Study terms.
  -d             Study definitions.
  -b             Study with randomized terms and definitions.
  -a             'All' - Include all entries.
  -m             'Many' - Exclude easy entries (those with 
                 correct:incorrect ratio >= 2). 
  -f             'Few' - Include only hard entries (those with 
                 correct:incorrect ratio <= 0.75).
  -s             Go through entries sequentially (in the order 
                 they were recorded).
  -r             Go through entries in random order.


Examples:
  simplefc create_set BIO450_final
  simplefc add_entry BIO450_final -M 'xanthophyll;;a yellow or brown carotenoid pigment found in plants' 'anthocyanin;;a red flavonoid pigment found in plants' "Kingsfoil;;aye, it's a weed!"
  simplefc study -bar BIO450_final
  simplefc delete_entry BIO450_final 1 3
  simplefc delete_set BIO450_final

Help:
  For help using this tool, please open an issue on Github:
  https://github.com/vlahm/simplefc
"""
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

from future import standard_library
standard_library.install_aliases()
from inspect import getmembers, isclass
from docopt import docopt
from . import __version__ as VERSION

def main():
    """Main CLI entrypoint."""
    import simplefc.commands
    options = docopt(__doc__, version=VERSION)

    for k, v in options.items():
        if hasattr(simplefc.commands, k) and v:
            module = getattr(simplefc.commands, k)
            simplefc.commands = getmembers(module, isclass)
            command = [command[1] for command in simplefc.commands if command[0] != 'Base'][0]
            command = command(options)
            command.run()
