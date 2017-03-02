import logging
import sys
import os
import json
from collections import deque
from datetime import datetime, timedelta

from dynamat2050 import Client

log = logging.getLogger("download")
logging.basicConfig(level=logging.INFO)

now = datetime.now()
one_year = timedelta(days=365)

class ArgParser(object):
    """
    Check args for command line script
    First arg is the config file
    Second arg is the command
    """
    def __init__(self, args):
        print("\n==========================")
        print(" downloading dynamat data ")
        print("==========================\n")
        self.args = deque(args)
        self.script = self.args.popleft()
        try:
            self.config_uri = self.args.popleft()
        except IndexError:
            log.error("Must provide a config file as first argument")
            exit(1)
        if not os.path.exists(self.config_uri):
            log.error("First argument must be a valid config file")
            exit(1)
        try:
            self.command = self.args.popleft()
        except IndexError:
            log.error("No command provided")
            exit(1)
        try:
            self.outdir = self.args.popleft()
        except IndexError:
            log.error("No output directory provided")
            exit(1)
        self.args = list(self.args)

def client_from_config(config):
    url, username, password = config.pop('url'), config.pop('username'), config.pop('password')
    return Client(url=url, username=username, password=password)

def main(argv=sys.argv):
    """
    Command line script
    Args are parsed and given to the edinet thing.
    """
    args = ArgParser(argv)
    with open(args.config_uri) as f:
        config = json.load(f)
    client = client_from_config(config)
    if args.command == "meters":
        log.info("attempting to get meters list")
        outfile = os.path.join(args.outdir, "meters.json")
        with open(outfile, 'w') as f:
            json.dump(client.meters(), f, indent=2, sort_keys=True)
    elif args.command == "meter_data":
        for meter in config['meters']:
            outfile = os.path.join(args.outdir, "meter_{}.json".format(meter))
            with open(outfile, 'w') as f:
                data = client.meter_data(meter, now - one_year, now).decode('utf-8')
                json.dump(data, f, indent=2, sort_keys=True)
    else:
        print("Command '{}' not recognised, use one of [meters, meter_data]".format(args.command))

if __name__ == "__main__":
    main()
