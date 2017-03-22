from argparse import ArgumentParser
from time import sleep, time
import mpris_scrobbler
from mpris_scrobbler.scrobble import Scrobble

__version__ = "0.0.1"


def run():
    print("MPRIS Scrobbler ver. {}".format(mpris_scrobbler.__version__))
    parser = ArgumentParser(description="Scrobble from MPRIS-enabled devices")
    parser.add_argument("-u", "--username", help="Scrobble service username",
                        default=None)
    parser.add_argument("-p", "--password", help="Scrobble service password",
                        default=None)
    parser.add_argument("-s", "--service",
                        help="Scrobble service. Options: wiltfm (default)",
                        default="wiltfm")
    parser.add_argument("-d", "--device", help="MPRIS device to scrobble from")

    args = parser.parse_args()
    starttime = time()
    scrob = Scrobble(args.username, args.password, args.service, args.device)

    if scrob.started is not True:
        print(scrob.started)
    else:
        while scrob.started is True:
            try:
                push = scrob.push()
                if push:  # Prevent "None" from being printed.
                    print(push)

                sleep(30.0 - ((time() - starttime) % 30.0))
            except KeyboardInterrupt:
                exit()
