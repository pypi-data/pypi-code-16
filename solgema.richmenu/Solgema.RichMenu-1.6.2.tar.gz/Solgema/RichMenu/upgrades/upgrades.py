from Products.CMFCore.utils import getToolByName

def upgradeRichMenu11(context):
    portal_setup = getToolByName(context, 'portal_setup')
    portal_setup.runAllImportStepsFromProfile('profile-Solgema.RichMenu.upgrades:richmenu_upgrade11')
