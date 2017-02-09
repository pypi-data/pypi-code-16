from logging import getLogger
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces import ITinyMCESchema
from Products.CMFPlone.patterns import TinyMCESettingsGenerator
from Products.CMFPlone.patterns.utils import get_portal_url
from zope.component.hooks import getSite
from zope.component import getUtility


def __new__init__(self, context, request):
    self.context = context
    self.request = request
    self.portal = getSite()
    registry = getUtility(IRegistry)
    self.settings = registry.forInterface(
        ITinyMCESchema, prefix="plone", check=False)
    self.portal_url = get_portal_url(self.context)


TinyMCESettingsGenerator.__init__ = __new__init__


log = getLogger('cs.plone5.tinymcepatch')
log.info("TinyMCE patching done")
