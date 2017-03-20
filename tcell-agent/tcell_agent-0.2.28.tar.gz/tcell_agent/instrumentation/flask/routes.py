from flask import Flask

from tcell_agent.agent import TCellAgent
from tcell_agent.instrumentation import safe_wrap_function

import logging
LOGGER = logging.getLogger('tcell_agent').getChild(__name__)

def calculate_route_id(method, uri):
    return str(hash(method + "|" + uri))


def get_methods(options, view_func):
    route_methods = options.get('methods', None)
    if route_methods is None:
        route_methods = getattr(view_func, 'methods', None) or ('GET',)
    return [item.upper() for item in route_methods]


def discover_route(rule, view_func, options):
    for method in get_methods(options, view_func):
        try:
            route_controller = ""
            if view_func is not None:
                if hasattr(view_func, '__module__') and view_func.__module__:
                    route_controller += view_func.__module__
                if hasattr(view_func, '__name__') and view_func.__name__:
                    if route_controller == "":
                        route_controller = view_func.__name__
                    else:
                        route_controller += "." + view_func.__name__
            if route_controller == "":
                route_controller = "(dynamic)"
            TCellAgent.discover_route(
                rule,
                method,
                route_controller,
                calculate_route_id(method, rule)
            )
        except Exception as e:
            LOGGER.debug("Could not obtain route information: {e}".format(e=e))
            LOGGER.debug(e, exc_info=True)



def instrument_routes():
    old_flask_add_url_rule = Flask.add_url_rule

    def add_url_rule(self, rule, endpoint=None, view_func=None, **options):
        safe_wrap_function("Discover Flask Route", discover_route, rule, view_func, options)
        return old_flask_add_url_rule(self, rule, endpoint, view_func, **options)

    Flask.add_url_rule = add_url_rule
