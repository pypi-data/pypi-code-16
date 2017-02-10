"""Tool interface for tool implementations.

A tool is implemented as an opaque class.

"""
import logging

log = logging.getLogger(__name__)


def missing_impl(tool, f):
    raise Exception(
        'incorrect tool implementation',
        'Tool implementation %s is missing a "%s" implementation' % (
            type(tool),
            f,
        )
    )


class Tool(object):
    def __str__(self):
        return "<%s>" % type(self).__name__

    def __repr__(self):
        return "<%s>" % type(self).__name__

    def name(self):
        return type(self).__name__.lower()

    def is_higher_order(self):
        return False

    def dir_info(tool, path, info):
        """Return info about using the tool in the specified path."""
        missing_impl(tool, Tool.dir_info.__name__)

    def dependencies(tool, path):
        """Return a list of dependency prefixes for the project at path."""
        missing_impl(tool, Tool.dependencies.__name__)

    def configure_parser(tool, parser):
        """Configure arg parser for the tool options and arguments."""
        missing_impl(tool, Tool.add_arg_parser.__name__)

    def execute_tool(tool, path, info, args):
        """Execute a build phase."""
        missing_impl(tool, Tool.execute_tool.__name__)


def load_tool(tool_name):
    """Load the tool implementation for the given tool name."""
    tool = \
        require_tool(tool_name) or \
        require_tool('menhir.tools.%s' % tool_name)
    if not tool:
        raise Exception(
            'configuration_error',
            'Tool not found: "%s"' % tool_name)
    return tool


def require_tool(tool_path):
    from importlib import import_module
    try:
        m = import_module(tool_path)
        return m.tool()
    except Exception as e:
        log.debug('Failed to import: %s, "%s"', tool_path, e)


def default_tools():
    """Return a list of the default tool names."""
    from menhir.tools import all_tools
    return all_tools
