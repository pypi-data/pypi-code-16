import argparse

from telnetlib import Telnet

from typing import List, Dict, NamedTuple


__all__ = ['HddtempClient']


class Drive(NamedTuple):
    path: str
    name: str
    temperature: int
    unit: str


class HddtempClient:

    def __init__(self, host: str='localhost',
                 port: int=7634, timeout: int=10, sep: str='|') -> None:
        """A simple Hddtemp client

        Arguments:
        host -- The host of the hddtemp server [default: localhost]
        port -- The port of the hddtemp server [default: 7634]
        timeout -- The timeout to wait until canceling a connection [default: 10]
        sep -- The separation character used by the hddtemp server [default: |]

        """

        self.host = host
        self.port = port
        self.timeout = timeout
        self.sep = sep

    def _parse_drive(self, drive: str) -> Drive:
        drive_data = drive.split(self.sep)
        return Drive(drive_data[0], drive_data[1], int(drive_data[2]), drive_data[3])

    def _parse(self, data: str) -> List[Drive]:
        # remove first and last sep character
        # so we don't have empty strings after splitting
        line = data.lstrip(self.sep).rstrip(self.sep)
        drives = line.split(self.sep * 2)
        return [self._parse_drive(drive) for drive in drives]

    def get(self) -> List[Drive]:
        """Get the current temperatures from the hddtemp server"""

        with Telnet(self.host, self.port, timeout=self.timeout) as tn:
            data = tn.read_all()

        return self._parse(data.decode('ascii'))


def test(host: str, port: int, timeout: int, sep: str) -> None:
    c = HddtempClient(host, port, timeout, sep)
    drives = c.get()
    for drive in sorted(drives, key=lambda x: x.path):
        print('{0.path} {0.name} {0.temperature}{0.unit}'.format(drive))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--timeout', '-t', default=10, type=int, metavar='TIMEOUT',
                        help='Specify a timeout [default: 10]')
    parser.add_argument('host', action='store',
                        default='localhost', type=str,
                        nargs='?',
                        help='Specify the host of the hddtemp server [default: localhost]')
    parser.add_argument('port', action='store',
                        default=7634, type=int,
                        nargs='?',
                        help='Specify the port of the hddtemp server [default: 7634]')
    parser.add_argument('sep', action='store',
                        default='|', type=str,
                        nargs='?',
                        help='Specify the separation character of the hddtemp server [default: |]')
    args = parser.parse_args()
    test(host=args.host, port=args.port, timeout=args.timeout, sep=args.sep)
