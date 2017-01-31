# menhir configuration
import logging

log = logging.getLogger(__name__)
ROOT_FILE = 'menhir-root.yaml'


def find_root():
    """Based on the current directory, look for a .menhir_root.yaml file."""
    from .fileutils import find_file_in_parents
    root = find_file_in_parents(ROOT_FILE)
    if root is None:
        raise FileNotFoundError(
            'No root file found in parent directories',
            ROOT_FILE
        )
    return root


def root_config(root_file=ROOT_FILE):
    """Return the root menhir configuration."""
    from os.path import exists
    import yaml

    config = default_root_config()
    if exists(root_file):
        with open(root_file, 'r') as stream:
            config.update(yaml.load(stream))
    return parse_root_config(config)


def parse_root_config(config):
    tools = config.get('tools')
    config['tools'] = {tool: load_tool(tool) for tool in tools}
    return config


def default_root_config():
    return {
        'tools': default_tools(),
        'ignore': [],
    }


def default_tools():
    from menhir.tools import all_tools
    return all_tools


def describe_repository(config):
    """Parse the root menhir configuration."""
    import os
    from os.path import relpath
    from menhir import gitutils
    from menhir.fileutils import directory_graph
    from menhir.graph import root_nodes

    git_root = gitutils.find_root()
    rel_git_root = relpath(git_root)

    tool_impls = config['tools'].values()

    # build the dependency graph
    fs_graph = directory_graph(rel_git_root, config['ignore'])
    infos = project_infos(fs_graph, rel_git_root, tool_impls)
    graph = project_graph(infos)
    roots = root_nodes(graph, infos)

    def is_child(x, y):
        from os.path import abspath, normpath
        return normpath(abspath(y)).startswith(normpath(abspath(x)))

    roots = set(filter(lambda x: is_child('.', x), roots))

    cwd = os.getcwd()
    git_prefix = cwd[len(git_root)+1:]

    config['tool_impls'] = tool_impls
    config['project_infos'] = infos
    config['dependencies'] = graph
    config['root_projects'] = roots
    config['git_root'] = git_root
    config['git_prefix'] = git_prefix
    return config


def defaults_config(dir_path):
    """Return the defaults configuration in dir_path."""
    from os.path import join
    from menhir.fileutils import load_yaml
    return load_yaml(join(dir_path, 'menhir-defaults.yaml')) or {}


def project_config(dir_path):
    """Return the project configuration in dir_path."""
    from os.path import join
    from menhir.fileutils import load_yaml
    return load_yaml(join(dir_path, 'menhir-config.yaml')) or {}


def load_tool(tool_name):
    """Load the tool implementation for the given tool name."""
    tool = \
        require_tool(tool_name) or \
        require_tool('menhir.tools.%s' % tool_name)
    if not tool:
        raise Exception('configuration_error', 'Tool not found %s', tool_name)
    return tool


def require_tool(tool_path):
    from importlib import import_module
    try:
        m = import_module(tool_path)
        return m.tool()
    except Exception as e:
        log.debug('Failed to import: %s, "%s"', tool_path, e)


def project_infos(graph, root, tools):
    """Return a map of project root path to project info dict."""
    from os.path import abspath, basename
    from menhir.graph import dfs_visit

    infos = {}

    def calc_config(defaults, path):
        from copy import deepcopy
        from menhir.utils import deep_merge
        defaults = deep_merge(defaults, defaults_config(path))
        config = deepcopy(defaults)
        config = deep_merge(config, project_config(path))
        return defaults, config

    def pre_f(defaults, path):
        defaults, config = calc_config(defaults, path)
        used = list(filter(lambda t: t.is_using_tool(path, config), tools))

        if len(used):
            infos[path] = infos.get(path, {})
            infos[path]['tools'] = used
            infos[path]['config'] = config
            infos[path]['project-name'] = (
                config.get('project-name') or
                basename(abspath(path))
            )

        return defaults

    def post_f(defaults, path, child_defaults):
        return defaults

    defaults = {}
    dfs_visit(graph, root, defaults, pre_f, post_f,)

    return infos


def project_graph(roots):
    """Return a project dependency graph."""
    from functools import reduce

    return {
        root: reduce(
            lambda x, y: x.union(y or set()),
            [
                set(tool.dependencies(root))
                for tool in info['tools']
            ],
            set()
        )
        for root, info in roots.items()
        }
