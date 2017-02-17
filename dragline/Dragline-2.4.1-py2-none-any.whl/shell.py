from dragline.http import Request
from dragline.parser import HtmlParser
from dragline import runtime
import argparse
from lxml.html import open_in_browser
from collections import defaultdict
from dragline.settings import Settings
import traceback
import os
from .utils import load_module
from functools import wraps
from collections import OrderedDict

def _embed_ipython_shell(namespace={}, banner=''):
    """Start an IPython Shell"""
    try:
        from IPython.terminal.embed import InteractiveShellEmbed
        from IPython.terminal.ipapp import load_default_config
    except ImportError:
        from IPython.frontend.terminal.embed import InteractiveShellEmbed
        from IPython.frontend.terminal.ipapp import load_default_config

    @wraps(_embed_ipython_shell)
    def wrapper(namespace=namespace, banner=''):
        config = load_default_config()
        shell = InteractiveShellEmbed(
            banner1=banner, user_ns=namespace, config=config)
        shell()
    return wrapper

def _embed_bpython_shell(namespace={}, banner=''):
    """Start a bpython shell"""
    import bpython
    @wraps(_embed_bpython_shell)
    def wrapper(namespace=namespace, banner=''):
        bpython.embed(locals_=namespace, banner=banner)
    return wrapper

def _embed_standard_shell(namespace={}, banner=''):
    """Start a standard python shell"""
    import code
    try: # readline module is only available on unix systems
        import readline
    except ImportError:
        pass
    else:
        import rlcompleter
        readline.parse_and_bind("tab:complete")
    @wraps(_embed_standard_shell)
    def wrapper(namespace=namespace, banner=''):
        code.interact(banner=banner, local=namespace)
    return wrapper

DEFAULT_PYTHON_SHELLS = OrderedDict([
    ('ipython', _embed_ipython_shell),
    ('bpython', _embed_bpython_shell),
    ( 'python', _embed_standard_shell),
])

def get_shell_embed_func(shells=None, known_shells=None):
    """Return the first acceptable shell-embed function
    from a given list of shell names.
    """
    if shells is None: # list, preference order of shells
        shells = DEFAULT_PYTHON_SHELLS.keys()
    if known_shells is None: # available embeddable shells
        known_shells = DEFAULT_PYTHON_SHELLS.copy()
    for shell in shells:
        if shell in known_shells:
            try:
                # function test: run all setup code (imports),
                # but dont fall into the shell
                return known_shells[shell]()
            except ImportError:
                continue

def start_python_console(namespace=None, banner='', shells=None):
    """Start Python console bound to the given namespace.
    Readline support and tab completion will be used on Unix, if available.
    """
    if namespace is None:
        namespace = {}

    try:
        shell = get_shell_embed_func(shells)
        if shell is not None:
            shell(namespace=namespace, banner=banner)
    except SystemExit: # raised when using exit() in python code.interact
        pass


def help():
    repr_data = defaultdict(lambda: None, {k: repr(v) for k, v in data.items()})
    intro = """\n[d] Available Dragline objects:
    [d]   parser                 %(parser)s
    [d]   request                %(request)s
    [d]   response               %(response)s
    [d] Useful shortcuts: ## Override methods in Cmd object ##
    [d]   shelp()                Shell help (print this help)
    [d]   fetch(req_or_url)      Fetch request (or URL) and update local objects
    [d]   view(response=None)    View response in a browser\n\n""" % repr_data
    return intro


def process(req_or_url):
    global data
    if not req_or_url:
        return help()
    if isinstance(req_or_url, Request):
        data["request"] = req_or_url
    else:
        data["request"] = Request(req_or_url)
    try:
        data["response"] = data["request"].send()
    except:
        data["response"] = None
        print(traceback.format_exc())
        print("Failed to fetch")
    try:
        data["parser"] = HtmlParser(data["response"])
    except:
        data["parser"] = None
        print("Failed to parse response")
    return help()


def fetch(req_or_url):
    result = process(req_or_url)
    print(result)


def view(response=None):
    if response is None:
        global data
        response = data["response"]
    open_in_browser(HtmlParser(response), response.encoding)

data = {"fetch": fetch, "view": view, "shelp": help,
        "Request": Request, 'parser': None, 'response': None,
        'request': None}


def execute():
    try:
        settings = load_module(os.getcwd(), 'settings')
        runtime.settings = Settings(settings)
    except:
        print("No settings file found")
    parser = argparse.ArgumentParser()
    parser.add_argument('url', action='store', default='', help='url', nargs='?')
    url = (parser.parse_args()).url
    result = process(url)
    start_python_console(data, banner=result)


if __name__ == "__main__":
    execute()
