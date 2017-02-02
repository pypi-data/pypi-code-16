"""
Topological sort.

"""
from collections import defaultdict


TEMPORARY = object()
VISITED = object()


def visit(nodes, edges, visited, results, resource):
    """
    DFS visit function.

    """
    if visited.get(resource.uri) == VISITED:
        return

    if visited.get(resource.uri) == TEMPORARY:
        raise Exception("Found cycle at {}".format(resource.uri))

    visited[resource.uri] = TEMPORARY
    for child_uri in edges[resource.uri]:
        child = nodes[child_uri]
        visit(nodes, edges, visited, results, child)
    visited[resource.uri] = VISITED

    results.append(resource)


def toposorted(resources):
    """
    Perform a topological sort on the input resources.

    Uses a DFS.

    """
    # sort resources first so we have a deterministic order of nodes with the same partial order
    resources = sorted(
        resources,
        key=lambda resource: (resource.type, resource.id),
    )

    # build graph
    nodes, edges = dict(), defaultdict(list)
    for resource in resources:
        nodes[resource.uri] = resource
        for parent_uri in resource.parents:
            edges[parent_uri].append(resource.uri)

    # DFS
    results, visited = [], {}
    for resource in resources:
        visit(nodes, edges, visited, results, resource)
    return reversed(results)
