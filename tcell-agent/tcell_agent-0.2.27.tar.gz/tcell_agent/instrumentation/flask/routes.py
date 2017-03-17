from flask import Flask

from tcell_agent.agent import TCellAgent
from tcell_agent.instrumentation import safe_wrap_function


def calculate_route_id(method, uri):
    return str(hash(method + "|" + uri))


def get_methods(options, view_func):
    route_methods = options.get('methods', None)
    if route_methods is None:
        route_methods = getattr(view_func, 'methods', None) or ('GET',)
    return [item.upper() for item in route_methods]


def discover_route(rule, view_func, options):
    for method in get_methods(options, view_func):
        TCellAgent.discover_route(
            rule,
            method,
            view_func.__module__ + "." + view_func.__name__,
            calculate_route_id(method, rule)
        )


def instrument_routes():
    old_flask_add_url_rule = Flask.add_url_rule

    def add_url_rule(self, rule, endpoint=None, view_func=None, **options):
        safe_wrap_function("Discover Flask Route", discover_route, rule, view_func, options)
        return old_flask_add_url_rule(self, rule, endpoint, view_func, **options)

    Flask.add_url_rule = add_url_rule
