from argparse import ArgumentParser

from devip.loader import get_services
from devip.service import Service
from devip.utils import RequireError


def run():
    parser = ArgumentParser()
    parser.add_argument('command', help='', default='scan', choices=['setup', 'show', 'clear', 'move', 'add', 'remove'])
    parser.add_argument('-s', '--services', help='service names', choices=['aws'], nargs='+', default=[])
    parser.add_argument('-t', '--temp', help='temporary ip list', action='store_true')
    parser.add_argument('-p', '--perm', help='permanent ip list', action='store_true')
    parser.add_argument('-a', '--address', help='ip address or `.` to auto-detect current ip')

    options = parser.parse_args()
    options.list = 'perm' if options.perm else 'temp' if options.temp else None

    switcher = {
        'setup': (),
        'show': (options.list,),
        'clear': (options.list,),
        'move': (options.address, options.list),
        'add': (options.list, options.address),
        'remove': (options.list, options.address)
    }
    args = switcher.get(options.command, None)

    if options.command in ['setup', 'move']:
        services = get_services(*options.services)
    else:
        services = [Service]

    try:
        [getattr(x(), options.command)(*args) for x in services]
    except RequireError:
        pass
