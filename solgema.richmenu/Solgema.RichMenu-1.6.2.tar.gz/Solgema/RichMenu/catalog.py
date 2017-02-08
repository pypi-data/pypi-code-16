import logging
LOG = logging.getLogger('Solgema.RichMenu')
from plone.indexer.decorator import indexer
from zope.component.hooks import getSite
from zope.interface import Interface
from AccessControl.PermissionRole import rolesForPermissionOn
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.CatalogTool import _mergedLocalRoles
from Products.ATContentTypes.interface.folder import IATFolder
from Products.ATContentTypes.interface.image import IATImage
from Products.ATContentTypes.interface.topic import IATTopic
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Solgema.RichMenu.interfaces import ISolgemaRichMenuAttributes, ISolgemaRichMenuMarker
from Acquisition import aq_inner
from Acquisition import aq_parent
from zope.component import getMultiAdapter
try:
    from z3c.relationfield.interfaces import IRelationValue
    has_relation = True
except:
    has_relation = False


@indexer(ISolgemaRichMenuMarker)
def getGlobalSectionItem(object):
    adapted = ISolgemaRichMenuAttributes(object, None)
    if getattr(adapted, 'section_menu_item', None):
        portal = getSite()
        context_state = getMultiAdapter((object, object.REQUEST), name=u'plone_context_state')
        folder = context_state.folder()
        folder_path = '/'.join(folder.getPhysicalPath())
        section_menu_item = adapted.section_menu_item
        if has_relation and IRelationValue.providedBy(section_menu_item):
            return section_menu_item.to_object.UID()
        try:
            return portal.restrictedTraverse(folder_path+adapted.section_menu_item).UID()
        except:
            return section_menu_item
    return None

@indexer(ISolgemaRichMenuMarker)
def getGlobalSectionMenuItemContent(object):
    adapted = ISolgemaRichMenuAttributes(object, None)
    return getattr(adapted, 'menu_item_content', None)

@indexer(ISolgemaRichMenuMarker)
def getGlobalSectionShowMenu(object):
    adapted = ISolgemaRichMenuAttributes(object, None)
    return getattr(adapted, 'show_menu', None)

@indexer(ISolgemaRichMenuMarker)
def getGlobalSectionMenuWidth(object):
    adapted = ISolgemaRichMenuAttributes(object, None)
    return getattr(adapted, 'menu_width', None)

@indexer(ISolgemaRichMenuMarker)
def getGlobalSectionMenuPosition(object):
    adapted = ISolgemaRichMenuAttributes(object, None)
    return getattr(adapted, 'menu_position', None)

@indexer(ISolgemaRichMenuMarker)
def getGlobalSectionMenuContent(object):
    adapted = ISolgemaRichMenuAttributes(object, None)
    return getattr(adapted, 'menu_content', None)

@indexer(ISolgemaRichMenuMarker)
def getGlobalSectionMenuImageSize(object):
    adapted = ISolgemaRichMenuAttributes(object, None)
    return getattr(adapted, 'menu_image_size', None)

@indexer(ISolgemaRichMenuMarker)
def getGlobalSectionMenuColumns(object):
    adapted = ISolgemaRichMenuAttributes(object, None)
    return getattr(adapted, 'menu_columns', None)

@indexer(ISolgemaRichMenuMarker)
def getGlobalSectionMenuSectionsDepth(object):
    adapted = ISolgemaRichMenuAttributes(object, None)
    return getattr(adapted, 'menu_sections_depth', None)

@indexer(ISolgemaRichMenuMarker)
def getGlobalSectionMenuDirection(object):
    adapted = ISolgemaRichMenuAttributes(object, None)
    return getattr(adapted, 'menu_direction', None)

@indexer(ISolgemaRichMenuMarker)
def getGlobalSectionSubMenuDisplay(object):
    adapted = ISolgemaRichMenuAttributes(object, None)
    return getattr(adapted, 'submenu_display', None)

@indexer(ISolgemaRichMenuMarker)
def getGlobalSectionSubMenuWidth(object):
    adapted = ISolgemaRichMenuAttributes(object, None)
    return getattr(adapted, 'submenu_width', None)


