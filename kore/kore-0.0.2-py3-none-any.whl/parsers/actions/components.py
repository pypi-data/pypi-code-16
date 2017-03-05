import argparse
from itertools import groupby

from kore import container_factory


class ListComponentsAction(argparse.Action):

    def __init__(self, option_strings, dest=argparse.SUPPRESS,
                 default=argparse.SUPPRESS, help=None, required=False):
        super(ListComponentsAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            default=default,
            nargs=0,
            help=help,
            required=required,
        )

    def __call__(self, parser, namespace, values, option_string=None):
        container = container_factory.create(namespace.config)

        config = container.pop('config')

        container_list = list(container.values())
        grouped_components = groupby(container_list, lambda x: x.__module__)

        print("List of components for", config)

        for module_name, grouper in grouped_components:
            print("")
            print(" From module", module_name)
            for component in grouper:
                print(" -", component.__name__)
