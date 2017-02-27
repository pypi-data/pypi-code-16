#!/usr/bin/env python3

import openlinter

def main():
    print('invoking command_line.main()')

    # Set up parser and CLI
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
#    group.add_argument('-u', '--url',
#        help='The URL to the GitHub repository to check. Defaults to None.')
    group.add_argument('-d', '--directory', help="The local path to your repository's base directory. Defaults to the current working directory.",
       default=os.getcwd()
    )
    parser.add_argument('-r', '--rules', help='The path to the rules configuration file, a YAML file containing the rules you would like to check for. Defaults to current-working-directory/openlinter/rules.yml.',
        default=os.path.join(os.getcwd(), 'openlinter/rules.yml')
    )
    parser.add_argument('-v', '--version', action='version', version='0.1dev')
    args = parser.parse_args()

    openlinter.main(args.directory, args.rules)
