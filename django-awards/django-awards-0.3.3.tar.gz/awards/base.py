
from .signals import badge_awarded


class BadgeAwarded(object):
    def __init__(self, level=None, user=None):
        self.level = level
        self.user = user


class BadgeDetail(object):
    def __init__(self, name=None, description=None, **kwargs):
        self.name = name
        self.description = description
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self):
        return unicode(self.name)


class Badge(object):
    async = False
    multiple = False

    def __init__(self):
        assert not (self.multiple and len(self.levels) > 1)
        for i, level in enumerate(self.levels):
            if not isinstance(level, BadgeDetail):
                self.levels[i] = BadgeDetail(level)

    def possibly_award(self, **state):
        """
        Will see if the user should be awarded a badge.  If this badge is
        asynchronous it just queues up the badge awarding.
        """
        assert "user" in state

        try:
            user_id = state['user'].pk
        except AttributeError:
            user_id = state['user']

        state['user_id'] = user_id

        if self.async:
            from .tasks import AsyncBadgeAward
            if 'user' in state:
                del state['user']
            state = self.freeze(**state)
            extra = {
                "countdown": getattr(self, 'countdown', None),
            }
            AsyncBadgeAward.apply_async((self, state), **extra)
            return
        return self.actually_possibly_award(**state)

    def actually_possibly_award(self, **state):
        """
        Does the actual work of possibly awarding a badge.
        """
        from .models import BadgeAward
        from .notification import notify_awarded

        user_id = state["user_id"]
        force_timestamp = state.pop("force_timestamp", None)
        awarded = self.award(**state)
        if awarded is None:
            return
        if awarded.user is not None:
            user_id = awarded.user.pk
        if awarded.level is None:
            assert len(self.levels) == 1
            awarded.level = 0
        awarded = awarded.level
        assert awarded < len(self.levels)
        if (not self.multiple and
                BadgeAward.objects.filter(user_id=user_id, slug=self.slug, level=awarded)):
            return
        extra_kwargs = {
            'points': getattr(self.levels[awarded], 'points', 0)
        }
        if force_timestamp is not None:
            extra_kwargs["awarded_at"] = force_timestamp
        badge = BadgeAward.objects.create(
            user_id=user_id, slug=self.slug,
            level=awarded, **extra_kwargs)
        if 'user' in state:
            badge.user = state['user']
        badge_awarded.send(sender=self, badge_award=badge)
        notify_awarded(badge)
        return badge

    def freeze(self, **state):
        return state
