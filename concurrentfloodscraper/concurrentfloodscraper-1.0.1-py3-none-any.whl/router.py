import re

from concurrentfloodscraper.exceptions import RoutingException


# resposible for registering and routing urls
class RouteManager:
    paths = {}

    # register a scraper child class with a particular url route
    @staticmethod
    def register(cls, regex):
        RouteManager.paths[re.compile(regex)] = cls

    # return the scraper class responsible for a given url
    @staticmethod
    def route(url):
        for regex, cls in RouteManager.paths.items():
            if regex.match(url):
                return cls

        raise RoutingException('No route found for "%s"\n.' % url)


# Used as an annotation to a Scraper child class
class Route:
    def __init__(self, regex):
        self.regex = regex

    def __call__(self, cls):
        RouteManager.register(cls, self.regex)
        return cls
