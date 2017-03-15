try:
    from IPython.terminal.embed import InteractiveShellEmbed
except ImportError:
    exit("Install IPython")


class KoreInteractiveShellEmbed(InteractiveShellEmbed):

    usage = "Kore shell usage"
    banner1 = """Kore shell"""
    banner2 = """
Environment:
  config            -> Application config.
  config_factory    -> Default config factory used to create `config`.
  container         -> Application container.
  container_factory -> Default container factory used to create `container`.
    """
    display_banner = True

    def __call__(self, config, config_factory, container, container_factory):
        local_ns = {
            'config': config,
            'config_factory': config_factory,
            'container': container,
            'container_factory': container_factory,
        }
        return super(KoreInteractiveShellEmbed, self).__call__(
            local_ns=local_ns,
        )
