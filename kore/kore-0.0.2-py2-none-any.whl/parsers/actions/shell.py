import argparse

from kore.configuration import container_factory


class ShellAction(argparse.Action):

    usage = "Wiapp shell usage"
    banner1 = """Wiapp shell"""
    banner2 = """
Environment:
  container         -> Application container.
  container_factory -> Default container factory used to create `container`.
    """
    display_banner = True

    def __init__(self, option_strings, dest=argparse.SUPPRESS,
                 default=argparse.SUPPRESS, help=None, required=False):
        super(ShellAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            default=default,
            nargs=0,
            help=help,
            required=required,
        )

    def __call__(self, parser, namespace, values, option_string=None):
        try:
            from IPython.terminal.embed import InteractiveShellEmbed
        except ImportError:
            print("Install IPython")
            return

        container = container_factory.create(namespace.config)

        local_ns = {
            'container': container,
            'container_factory': container_factory,
        }

        shell = InteractiveShellEmbed(
            usage=self.usage,
            banner1=self.banner1,
            banner2=self.banner2,
            display_banner=self.display_banner,
        )
        return shell(local_ns=local_ns)
