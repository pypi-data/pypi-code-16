from argparse import ArgumentParser

# from kore.parsers.actions.components import ListComponentsAction
# from kore.parsers.actions.shell import ShellAction


class AppParser(ArgumentParser):

    def __init__(self, *args, **kwargs):
        super(AppParser, self).__init__(*args, **kwargs)
        self.add_argument('--config-type', default='ini')
        self.add_argument(
            '--config-opt',
            type=lambda kv: kv.split("=", 1), action='append')
        # self.add_argument(
        #     '-l',
        #     '--list',
        #     action=ListComponentsAction,
        #     help='list components',
        # )
        # self.add_argument(
        #     '-s',
        #     '--shell',
        #     action=ShellAction,
        #     help='Run shell',
        # )
