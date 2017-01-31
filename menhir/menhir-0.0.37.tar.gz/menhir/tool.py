"""Tool interface for tool implementations.

A tool is implemented as an opaque class.

"""


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

    def is_using_tool(tool, path, info):
        """Predicate to test if the path contains a project using the tool."""
        missing_impl(tool, Tool.is_using_tool.__name__)

    def dependencies(tool, path):
        """Return a list of dependency prefixes for the project at path."""
        missing_impl(tool, Tool.dependencies.__name__)

    def execute_build_phase(tool, path, info, args):
        """Execute a build phase."""
        missing_impl(tool, Tool.execute_build_phase.__name__)

    def add_arg_parser(tool, parsers):
        """Add an arg parser for the tool to parsers."""
        missing_impl(tool, Tool.add_arg_parser.__name__)
