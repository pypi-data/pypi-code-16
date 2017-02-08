from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName

from AccessControl import ClassSecurityInfo
from zope.interface import implements
from Products.CMFCore import permissions   

from Products.CMFPlone.utils import getFSVersionTuple
from zope.component import adapter, getUtility, getAdapters, getMultiAdapter, getSiteManager
from Products.GenericSetup.interfaces import IProfileImportedEvent

try:
    from z3c.relationfield.schema import RelationChoice, RelationList
    from plone.app.vocabularies.catalog import CatalogSource
    from plone.app.widgets.dx_bbb import RelatedItemsFieldWidget
    has_rel = True
except:
    has_rel = False

def setupRichMenu(context):
    if context.readDataFile('solgema_richmenu.txt') is None:
        return
    portal = context.getSite()
    catalog = getToolByName(portal, 'portal_catalog')
    catalog.manage_reindexIndex()
    setup = getToolByName(portal, 'portal_setup')
    portal_quickinstaller = getToolByName(portal, 'portal_quickinstaller')
    if getFSVersionTuple()[0] == 4:
        setup.runAllImportStepsFromProfile('profile-Solgema.RichMenu:plone4')
    else:
        setup.runAllImportStepsFromProfile('profile-Solgema.RichMenu:plone5')
    if not portal_quickinstaller.isProductInstalled('plone.app.widgets') and not portal_quickinstaller.isProductInstalled('plone.formwidget.contenttree'):
        try:
            setup.runAllImportStepsFromProfile('profile-plone.formwidget.contenttree:default')
        except:
            pass

def uninstallRichMenu(context):
    if context.readDataFile('uninstall_solgema_richmenu.txt') is None:
        return
    portal = context.getSite()
    catalog = getToolByName(portal, 'portal_catalog')
    catalog.manage_reindexIndex()
    setup = getToolByName(portal, 'portal_setup')
    if getFSVersionTuple()[0] == 4:
        setup.runAllImportStepsFromProfile('profile-Solgema.RichMenu:uninstallplone4')
    else:
        setup.runAllImportStepsFromProfile('profile-Solgema.RichMenu:uninstallplone5')
    

@adapter(IProfileImportedEvent)
def handleProfileImportedEvent(event):
    context = event.tool
    portal_quickinstaller = getToolByName(context, 'portal_quickinstaller')
    if portal_quickinstaller.isProductInstalled('Solgema.RichMenu'):
        if portal_quickinstaller.isProductInstalled('plone.app.contenttypes') and 'to500' in event.profile_id and event.full_import:
            portal_setup = getToolByName(context, 'portal_setup')
            portal_setup.runAllImportStepsFromProfile('profile-Solgema.RichMenu:uninstallplone4')
            portal_setup.runAllImportStepsFromProfile('profile-Solgema.RichMenu:plone5')
        elif 'plone.app.contenttypes' in event.profile_id and event.full_import:
            portal_setup = getToolByName(context, 'portal_setup')
            portal_setup.runAllImportStepsFromProfile('profile-Solgema.RichMenu:uninstallplone4')
            portal_setup.runAllImportStepsFromProfile('profile-Solgema.RichMenu:plone5')
