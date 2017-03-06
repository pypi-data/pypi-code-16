# encoding: utf-8
# Copyright 2011 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

from eke.ecas.interfaces import IDatasetFolder
from Products.CMFCore.utils import getToolByName
from utils import setFacetedNavigation

def _getPortal(context):
    return getToolByName(context, 'portal_url').getPortalObject()

def nullUpgradeStep(setupTool):
    '''A null step for when a profile upgrade requires no custom activity.'''

def upgradeDatasetFolders(setupTool):
    '''Set up faceted navigation and add disclaimers on all Biomarker Folders.'''
    portal = _getPortal(setupTool)
    request = portal.REQUEST
    catalog = getToolByName(portal, 'portal_catalog')
    results = [i.getObject() for i in catalog(object_provides=IDatasetFolder.__identifier__)]
    if len(results) == 0:
        # wtf? catalog must be out of date, because the common situation is that our EDRN
        # public portal does indeed have at least one Science Data Folder
        if 'science-data' in portal.keys():
            results = [portal['science-data']]
    for folder in results:
        setFacetedNavigation(folder, request, force=True)
