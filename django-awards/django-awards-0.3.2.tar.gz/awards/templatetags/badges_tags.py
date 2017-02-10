# coding: utf-8
from __future__ import unicode_literals

from django import template
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.db.models import Count
from django.utils.functional import SimpleLazyObject
from django.contrib.auth import get_user_model

from ..models import BadgeAward
from ..internals import badges

User = get_user_model()
register = template.Library()


@register.assignment_tag
def badges_for_user(user):
    """
    Usage:

        {% load badges_tags %}

        {% badges_for_user user as badges %}

        {% for badge in badges %}
            Name: {{badge.name}}
            ...
        {% endfor%}
    """

    return BadgeAward.objects \
        .filter(user=user) \
        .order_by("-awarded_on")


class MostAwardedBadge(object):

    def __init__(self, detail, count, slug=None, users_count=None):
        self.detail = detail
        self.slug = getattr(detail, 'slug', slug)
        self.count = count
        self.users_count = users_count
        self.pct = (count / float(users_count) * 100) if users_count else 100

    def __getattr__(self, attr):
        return getattr(self.detail, attr)

    def __repr__(self):
        return "MostAwardedBadge(detail={detail!r}, count={count})".format(
            detail=self.detail,
            count=self.count,
        )

    @property
    def image_url(self):
        slug = getattr(self, 'slug', None)
        if not slug:
            return 'http://placehold.it/55x55'
        return static(
            'icons/icons_achievements/{slug}.png'.format(slug=slug.replace('-', '_')))


@register.assignment_tag
def most_awarded_badges(client_id=None, limit=5):
    """
    Usage:

        {% load badges_tags %}

        {% most_awarded_badges client_id=user.client_id limit=5 as badges %}

        {% for badge in badges %}
            Name: {{badge.name}}
            ...
        {% endfor%}
    """

    qs = BadgeAward.objects
    user_qs = User.objects
    if client_id:
        qs = qs.filter(user__client_id=client_id)
        user_qs = user_qs.filter(client_id=client_id)

    users_count = user_qs.aggregate(count=Count('*'))['count']

    qs = qs \
        .values_list('slug', 'level') \
        .annotate(count=Count('id')) \
        .order_by('-count', 'level', 'slug')[:limit]

    def lazy():
        return [
            MostAwardedBadge(
                detail=badges._registry[slug].levels[level],
                count=count,
                slug=slug,
                users_count=users_count
            )
            for slug, level, count in qs
        ]

    return SimpleLazyObject(lazy)
