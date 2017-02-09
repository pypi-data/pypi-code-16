from datetime import datetime

from django.contrib.auth import get_user_model
from django.db.models import Count, Q

from portfolio.models import PortfolioPost, PortfolioCategory
from mezzanine.generic.models import Keyword
from mezzanine import template

User = get_user_model()

register = template.Library()


@register.as_tag
def portfolio_months(*args):
    """
    Put a list of dates for portfolio posts into the template context.
    """
    dates = PortfolioPost.objects.published().values_list("publish_date", flat=True)
    date_dicts = [{"date": datetime(d.year, d.month, 1)} for d in dates]
    month_dicts = []
    for date_dict in date_dicts:
        if date_dict not in month_dicts:
            month_dicts.append(date_dict)
    for i, date_dict in enumerate(month_dicts):
        month_dicts[i]["post_count"] = date_dicts.count(date_dict)
    return month_dicts


@register.as_tag
def portfolio_categories(*args):
    """
    Put a list of categories for portfolio posts into the template context.
    """
    posts = PortfolioPost.objects.published()
    categories = PortfolioCategory.objects.filter(portfolioposts__in=posts)
    return list(categories.annotate(post_count=Count("portfolioposts")))


@register.as_tag
def portfolio_authors(*args):
    """
    Put a list of authors (users) for portfolio posts into the template context.
    """
    portfolio_posts = PortfolioPost.objects.published()
    authors = User.objects.filter(portfolioposts__in=portfolio_posts)
    return list(authors.annotate(post_count=Count("portfolioposts")))


@register.as_tag
def portfolio_recent_posts(limit=5, tag=None, username=None, category=None):
    """
    Put a list of recently published portfolio posts into the template
    context. A tag title or slug, category title or slug or author's
    username can also be specified to filter the recent posts returned.
    Usage::
        {% portfolio_recent_posts 5 as recent_posts %}
        {% portfolio_recent_posts limit=5 tag="django" as recent_posts %}
        {% portfolio_recent_posts limit=5 category="python" as recent_posts %}
        {% portfolio_recent_posts 5 username=admin as recent_posts %}
    """
    portfolio_posts = PortfolioPost.objects.published().select_related("user")
    title_or_slug = lambda s: Q(title=s) | Q(slug=s)
    if tag is not None:
        try:
            tag = Keyword.objects.get(title_or_slug(tag))
            portfolio_posts = portfolio_posts.filter(keywords__keyword=tag)
        except Keyword.DoesNotExist:
            return []
    if category is not None:
        try:
            category = PortfolioCategory.objects.get(title_or_slug(category))
            portfolio_posts = portfolio_posts.filter(categories=category)
        except PortfolioCategory.DoesNotExist:
            return []
    if username is not None:
        try:
            author = User.objects.get(username=username)
            portfolio_posts = portfolio_posts.filter(user=author)
        except User.DoesNotExist:
            return []
    return list(portfolio_posts[:limit])
