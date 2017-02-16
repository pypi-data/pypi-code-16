# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from plone import api
from plone.app.layout.viewlets import ViewletBase
from Products.CMFCore.interfaces import ISiteRoot
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from sc.blog.config import BLOG_BLACKLISTED_TYPES
from sc.blog.content import IBlog


class View(BrowserView):

    """Default view. Looks like a standard Folder Full View."""

    index = ViewPageTemplateFile('templates/folder_full_view.pt')

    def get_blog_friendly_types(self):
        """Return the portal types than should be displayed as post entries
        inside a Blog. Some content types (like Blog, File, Folder and Image)
        are excluded by default.

        :returns: a tuple with the names of the portal types
        """
        plone_utils = api.portal.get_tool(name='plone_utils')
        friendly_types = plone_utils.getUserFriendlyTypes()
        blog_types = set(friendly_types) - set(BLOG_BLACKLISTED_TYPES)
        return tuple(blog_types)

    def __call__(self):
        return self.index()


class BlogSummaryView(View):

    """Looks like a standard Folder Summary View."""

    index = ViewPageTemplateFile('templates/folder_summary_view.pt')

    def __call__(self):
        return self.index()


class BlogHeader(ViewletBase):

    """A viewlet to include a header in the container (Blog) and contained
    (News Article) elements.
    """

    def update(self):
        """ check if we are inside a Blog, if its true
            set it into self.blog
        """
        self.context = aq_inner(self.context)
        self.blog = None
        # is context a Blog or inside a Blog?
        for ob in self.context.aq_chain:
            if ISiteRoot.providedBy(ob):
                break
            if IBlog.providedBy(ob):
                self.blog = ob
                break

    def available(self):
        """Check if we're inside a Blog."""
        return bool(self.blog)

    def blog_url(self):
        """Return the blog URL."""
        return self.blog.absolute_url()
