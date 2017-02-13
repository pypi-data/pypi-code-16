import sys
import argparse


def ask(message, options):
    """Ask the message interactively, with the given possible responses"""
    while True:
        response = input(message)
        response = response.strip().lower()
        if response not in options:
            print(f'Your response ({response}) was not one of the expected responses: {", ".join(options)}')
        else:
            return response


class StoreKeyValuePair(argparse.Action):
    """Store variables of form FOO=bar in a dict"""
    def __call__(self, parser, namespace, values, option_string=None):
        variables = dict()
        for pair in values:
            try:
                key, value = pair.split('=')
            except ValueError as e:
                print(f'~ {pair} is invalid. Must be in the format FOO=bar.')
                sys.exit(1)
            variables[key] = value
        setattr(namespace, self.dest, variables)
