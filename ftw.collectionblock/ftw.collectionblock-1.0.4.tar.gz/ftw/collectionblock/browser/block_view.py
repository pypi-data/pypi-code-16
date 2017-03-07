from ftw.collectionblock import _
from ftw.collectionblock import utils
from ftw.simplelayout.browser.blocks.base import BaseBlock
from Products.CMFPlone.interfaces.syndication import IFeedSettings
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter
from zope.i18n import translate


class CollectionBlockView(BaseBlock):
    """Collection block view, which provides several features from the
    plone.app.contenttypes.browser.folder.FolderView"""

    template = ViewPageTemplateFile('templates/block_view.pt')

    def __init__(self, context, request):
        super(CollectionBlockView, self).__init__(context, request)

        self.plone_view = getMultiAdapter((context, request), name=u"plone")
        self.portal_state = getMultiAdapter(
            (context, request), name=u"plone_portal_state")

    def toLocalizedTime(self, time, long_format=None, time_only=None):
        return self.plone_view.toLocalizedTime(time, long_format, time_only)

    def block_results(self):
        if self.context.block_amount > 0:
            return self.context.results(b_size=self.context.block_amount)
        return self.context.results()

    def get_author(self, item):
        author = ''
        if utils.can_view_about():
            author = utils.get_creator(item)
        return author

    def get_block_info(self):
        """
        This method returns a dict containing information to be used in
        the block's template.
        """

        rss_link_url = ''
        if self.context.show_rss_link and self.rss_enabled:
            rss_link_url = '/'.join([self.context.absolute_url(), 'RSS'])

        more_link_url = '/'.join([self.context.absolute_url(), 'listing_view'])

        more_link_label = (
            self.context.more_link_label or
            translate(_('more_link_label', default=u'More'),
                      context=self.request)
        )

        info = {
            'title': self.context.title,
            'show_title': self.context.show_title,
            'more_link_url': more_link_url,
            'more_link_label': more_link_label,
            'rss_link_url': rss_link_url or '',
        }

        return info

    @property
    def rss_enabled(self):
        rss_settings = IFeedSettings(self.context)
        return rss_settings.enabled
