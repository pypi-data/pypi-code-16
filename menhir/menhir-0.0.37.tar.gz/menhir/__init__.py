"""
Menhir is a project automation tool that is designed to work with
a monrepo. It is extensible using python packages.
"""
import logging

from menhir.config import describe_repository, root_config
from menhir.tool_utils import OK, NOTHING_TO_DO

__version__ = "0.0.37"

log = logging.getLogger(__name__)


def apply_tool(dependencies, dirs, roots, tool, args):
    """Apply phase_name to each project.

    Projects are visited in dependency order.  A full traversal is
    made.  It is up to each tool to decide whether to run, based on
    the changed state in the project info.
    """
    from functools import reduce
    from menhir.graph import dfs_visit

    def pre_f(state, path):
        return state

    def merge_state(x, y):
        log.debug('merge_state: %s %s', x, y)
        x['failed'] = x.get('failed') or y.get('failed')
        x['seen'] = x['seen'].union(y['seen'])
        return x

    def post_f(state, path, child_states):
        log.debug('apply_tool post_f %s %s', path, state)
        info = dirs[path]
        if not state.get('failed') and path not in state['seen']:
            res = apply_tool_to_path(path, info, tool, args)
            if res['status'] == 'fail':
                log.warning('%s failed in %s', tool, path)
                state['failed'] = True

        seen = state['seen']
        seen.add(path)
        state['seen'] = seen
        return state

    state = {'seen': set()}
    child_states = [
        dfs_visit(
            dependencies,
            root,
            state,
            pre_f,
            post_f,
            child_state_f=lambda x: x  # shared state
        )
        for root in roots
    ]

    log.debug('child_states: %s', child_states)
    return reduce(merge_state, child_states, state)


def apply_tool_to_path(path, info, tool, args):
    if tool not in set(info['tools']):
        log.debug('Tool %s not used in %s', tool, path)
        return NOTHING_TO_DO
    res = tool.execute_build_phase(path, info, args)
    log.debug('Execute tool %s in %s returns %s', tool.name(), path, res)
    if res['status'] == 'fail':
        log.debug('Tool %s in %s failed %s', tool.name(), path, res)
        res['tool'] = tool.name()
        res['args'] = args
        res['path'] = path
        return res
    return OK


def update_for_changed_files(
        dependencies, project_infos, root_projects, prefix, files
):
    """Update project infos with changed status, given changed files.

    Updates project_infos with `changed`, `changed_dependees` and
    `changed_dependents` fields, based on the list of changed files.

    `prefix` allows the specification of a path prefix, to add to each
    of the project dirs, before determining if they contain any of the
    files.

    Returns a list of changed projects.

    """
    changed_projects = projects_with_files(project_infos, files, prefix)
    mark_changed(project_infos, changed_projects)
    propagate_changed(dependencies, project_infos, root_projects)
    return changed_projects


def projects_with_files(roots, files, root_prefix):
    """Filter roots that contain any of files paths.

    The roots are each prefixed with root_prefix, before comparison.
    """
    from os.path import join, normpath
    log.debug('projects_with_files:')
    log.debug(' roots: %s', roots)
    log.debug(' files: %s', files)
    roots = set(roots)
    changed_roots = set()

    for path in files:
        if len(roots):
            for root in roots.copy():
                prefix = normpath(join(root_prefix, root)) if root_prefix \
                         else root
                log.debug('prefix: %s, path: %s', prefix, path)
                if path.startswith(prefix) or (
                        prefix == '.' and not path.startswith('..')
                ):
                    changed_roots.add(root)
                    roots.remove(root)
        else:
            break
    return changed_roots


CHANGED = 'changed'
CHANGED_DEPENDENTS = 'changed_dependents'
CHANGED_DEPENDEES = 'changed_dependees'


def mark_changed(projects, changed_projects):
    for project in changed_projects:
        projects[project][CHANGED] = True


def propagate_changed(dependencies, infos, root_projects):
    """Propagate changed info to dependees and dependents.

    `changed` nodes propagate `changed_dependees` down the graph.
    `changed` nodes propagate `changed_dependents` up the graph.
    """
    from menhir.graph import dfs_visit

    def pre_f(state, node):
        info = infos[node]
        if state.get(CHANGED_DEPENDEES):
            info[CHANGED_DEPENDEES] = True
        if info.get(CHANGED):
            state[CHANGED_DEPENDEES] = True
        log.debug('info pre: %s', info)
        return state

    def post_f(state, node, child_states):
        from copy import copy
        info = infos[node]
        for child_state in child_states:
            if (
                    child_state.get(CHANGED_DEPENDENTS) or
                    child_state.get(CHANGED)
            ):
                info[CHANGED_DEPENDENTS] = True
        log.debug('info post: %s', info)
        return copy(info)

    for root in root_projects:
        dfs_visit(dependencies, root, {}, pre_f, post_f)


__all__ = [
    'describe_repository',
    'root_config',
    'apply_tool',
    'projects_with_files',
    'mark_changed',
    'propagate_changed'
]
