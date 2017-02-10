
# coding: utf-8

from .base import Badge


class BadgeCache(object):
    """
    This is responsible for storing all badges that have been registered, as
    well as providing the pulic API for awarding badges.

    This class should not be instantiated multiple times, if you do it's your
    fault when things break, and you get to pick up all the pieces.
    """
    def __init__(self):
        self._event_registry = {}
        self._registry = {}

    def register(self, badge_cls):
        # We should probably duck-type this, but for now it's a decent sanity
        # check.
        assert issubclass(badge_cls, Badge)
        badge = badge_cls()
        if badge.slug in self._registry:
            raise ValueError("{} is already registered.".format(badge_cls))
        self._registry[badge.slug] = badge
        for event in badge.events:
            self._event_registry.setdefault(event, []).append(badge)
        return badge_cls

    def possibly_award_badge(self, event, callback=None, **state):
        for badge in self._event_registry[event]:
            awarded = badge.possibly_award(**state)
            if awarded and callback:
                callback(awarded)


badges = BadgeCache()
