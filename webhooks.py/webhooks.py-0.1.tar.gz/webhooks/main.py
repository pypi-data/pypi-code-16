import argparse
import os
import sys
from .loaders import YamlLoader


def main():
    parser = argparse.ArgumentParser(description='Start a webhook service.')
    parser.add_argument('config', help='Configuration file')
    parser.add_argument('-p', '--port', type=int, default=3000, help='the port to listen on')
    parser.add_argument('-i', '--interface', default="0.0.0.0", help='the interface to listen on')

    args = parser.parse_args()
    config_path = os.path.abspath(args.config)

    if not os.path.exists(config_path):
        sys.stderr.write(f'Config path {args.config} does not exists\n')
        exit(1)

    loader = YamlLoader(config_path)
    print(loader.rules())