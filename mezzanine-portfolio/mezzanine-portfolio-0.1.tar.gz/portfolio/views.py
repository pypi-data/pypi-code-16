from future.builtins import str, int

from calendar import month_name

from django.contrib.auth import get_user_model
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _

from portfolio.models import PortfolioPost, PortfolioCategory
from mezzanine.conf import settings
from mezzanine.generic.models import Keyword
from mezzanine.utils.views import paginate

User = get_user_model()


def portfolio_post_list(request, tag=None, year=None, month=None, username=None,
                   category=None, template="portfolio/portfolio_post_list.html",
                   extra_context=None):
    """
    Display a list of portfolio posts that are filtered by tag, year, month,
    author or category. Custom templates are checked for using the name
    ``portfolio/portfolio_post_list_XXX.html`` where ``XXX`` is either the
    category slug or author's username if given.
    """
    templates = []
    portfolio_posts = PortfolioPost.objects.published(for_user=request.user)
    if tag is not None:
        tag = get_object_or_404(Keyword, slug=tag)
        portfolio_posts = portfolio_posts.filter(keywords__keyword=tag)
    if year is not None:
        portfolio_posts = portfolio_posts.filter(publish_date__year=year)
        if month is not None:
            portfolio_posts = portfolio_posts.filter(publish_date__month=month)
            try:
                month = _(month_name[int(month)])
            except IndexError:
                raise Http404()
    if category is not None:
        category = get_object_or_404(PortfolioCategory, slug=category)
        portfolio_posts = portfolio_posts.filter(categories=category)
        templates.append(u"portfolio/portfolio_post_list_%s.html" %
                          str(category.slug))
    author = None
    if username is not None:
        author = get_object_or_404(User, username=username)
        portfolio_posts = portfolio_posts.filter(user=author)
        templates.append(u"portfolio/portfolio_post_list_%s.html" % username)

    prefetch = ("categories", "keywords__keyword")
    portfolio_posts = portfolio_posts.select_related("user").prefetch_related(*prefetch)
    portfolio_posts = paginate(portfolio_posts, request.GET.get("page", 1),
                          settings.BLOG_POST_PER_PAGE,
                          settings.MAX_PAGING_LINKS)
    context = {"portfolio_posts": portfolio_posts, "year": year, "month": month,
               "tag": tag, "category": category, "author": author}
    context.update(extra_context or {})
    templates.append(template)
    return TemplateResponse(request, templates, context)


def portfolio_post_detail(request, slug, year=None, month=None, day=None,
                     template="portfolio/portfolio_post_detail.html",
                     extra_context=None):
    """. Custom templates are checked for using the name
    ``portfolio/portfolio_post_detail_XXX.html`` where ``XXX`` is the portfolio
    posts's slug.
    """
    portfolio_posts = PortfolioPost.objects.published(
                                     for_user=request.user).select_related()
    portfolio_post = get_object_or_404(portfolio_posts, slug=slug)
    context = {"portfolio_post": portfolio_post, "editable_obj": portfolio_post}
    context.update(extra_context or {})
    templates = [u"portfolio/portfolio_post_detail_%s.html" % str(slug), template]
    return TemplateResponse(request, templates, context)
