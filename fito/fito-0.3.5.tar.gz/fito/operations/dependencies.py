import inspect
import os

import networkx as nx

here = os.path.dirname(__file__)


def depends_on(thing):
    """
    Main decorator to tie things together
    :param thing: What you wanna tie with
    see pipeline.py or english_proficiency.py for examples
    """

    def decorator(cls):
        DependencyGraph.add_dependency(cls, thing)
        return cls

    return decorator


class DependencyGraph(object):
    """
    Main class to both manipulate the graph and inherit to get cool graph powers
    """
    dependency_graph = {}

    @staticmethod
    def add_dependency(source, target):
        """
        Source depends on target
        :return:
        """
        if source not in DependencyGraph.dependency_graph:
            DependencyGraph.dependency_graph[source] = []
        DependencyGraph.dependency_graph[source].append(target)
        return DependencyGraph

    @staticmethod
    def has_dependencies(klass):
        return len(DependencyGraph.dependency_graph.get(klass, [])) == 0

    @staticmethod
    def get_dependency_graph():
        """
        Converts this guy to a networkx graph to easily perform crazy computations with this graph
        :return:
        """
        g = nx.DiGraph()
        for cls in get_subclasses(DependencyGraph):
            g.add_node(cls)

        for src_obj, dst_objs in DependencyGraph.dependency_graph.iteritems():
            src_objs = [src_obj]
            if inspect.isclass(src_obj): src_objs.extend(get_subclasses(src_obj))

            for sub_src_obj in src_objs:
                for dst_obj in dst_objs:
                    g.add_edge(sub_src_obj, dst_obj)
        return g

    @staticmethod
    def get_direct_dependencies(klass):
        return DependencyGraph.dependency_graph[klass][:]

    @staticmethod
    def get_dependency_clausure(*classes_or_instances, **kwargs):
        classes = []
        for i, e in enumerate(classes_or_instances):
            if not inspect.isclass(e) and not inspect.isfunction(e):
                # instance object are turned into their corresponding types
                e = type(e)
            classes.append(e)

        g = DependencyGraph.get_dependency_graph()
        res = nx.topological_sort(g, classes, reverse=True)
        include_requested = kwargs.get('include_requested', False)
        if not include_requested: res = res[:-1]
        return res


def get_subclasses(cls):
    stack = [cls]
    res = []
    while len(stack) > 0:
        direct_subclasses = stack.pop().__subclasses__()
        res.extend(direct_subclasses)
        stack.extend(direct_subclasses)
    return res