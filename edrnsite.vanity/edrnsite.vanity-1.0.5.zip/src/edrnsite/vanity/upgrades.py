# encoding: utf-8
# Copyright 2012–2016 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

u'''EDRN Site Vanity Pages: upgrades.'''

from Products.CMFCore.WorkflowCore import WorkflowException
from edrnsite.vanity import DEFAULT_PROFILE
import plone.api


def removeContributorRoleFromSites(context):
    u'''Remove the "Can Add" (Contributor) permission from Site objects.  We're putting bespokepages
    under a top level /member-pages folder now.'''
    catalog = plone.api.portal.get_tool('portal_catalog')
    results = catalog(portal_type='Site')
    for site in [i.getObject() for i in results]:
        localRoles = site.get_local_roles()
        found = False
        for principle, roles in localRoles:
            if principle == 'AuthenticatedUsers':
                if u'Contributor' in roles:
                    found = True
                    break
        if found:
            site.manage_setLocalRoles('AuthenticatedUsers', [])


def addMembersFolder(context):
    u'''Add the top-level /member-pages folder so that we have a place for member pages.'''
    portal = plone.api.portal.get()
    if not 'member-pages' in portal.keys():
        folder = portal[portal.invokeFactory('Folder', 'member-pages')]
        folder.setTitle(u'Member Pages')
        folder.setDescription(u'Pages highlighting individual members of the Early Detection Research Network')
        folder.setExcludeFromNav(True)
        wfTool = plone.api.portal.get_tool('portal_workflow')
        state = wfTool.getInfoFor(folder, 'review_state')
        if state != 'published':
            try:
                wfTool.doActionFor(folder, 'publish')
            except WorkflowException:
                pass
        localRoles = folder.get_local_roles()
        found = False
        for principal, roles in localRoles:
            if principal == 'AuthenticatedUsers':
                if u'Contributor' in roles:
                    found = True
                    break
        if not found:
            folder.manage_setLocalRoles('AuthenticatedUsers', ['Contributor'])
        folder.reindexObject()


def enableVanityPages(context):
    u'''Enable vanity pages in the configuration registry.'''
    context.runImportStepFromProfile(DEFAULT_PROFILE, 'plone.app.registry')
    context.runImportStepFromProfile(DEFAULT_PROFILE, 'typeinfo')
    # While we're here, let's create a page for a demo user
    portal = plone.api.portal.get()
    bwh = portal.unrestrictedTraverse('sites/70-brigham-and-womens-hospital')
    piUID = bwh['cramer-daniel'].piUID
    seeyan = bwh[bwh.invokeFactory('Person', 'kelly-seeyan')]
    seeyan.accountName = 'seeyan'
    seeyan.degrees = [u'BS CS', u'BS Tech Comm']
    seeyan.edrnTitle = u'Technologist'
    seeyan.givenName = u'Seeyan'
    seeyan.investigatorStatus = u'Peon'
    seeyan.mailingAddress = u'PO Box 169-429'
    seeyan.mbox = u'sean.kelly@jpl.nasa.gov'
    seeyan.memberType = u'Informatics Center'
    seeyan.phone = u'+1 469 555 5419'
    seeyan.physicalAddress = u'1213 San Saba Court'
    seeyan.piUID = piUID
    seeyan.salutation = u'Mr'
    seeyan.shippingAddress = u'1213 San Saba Court'
    seeyan.specialty = u'Informatics'
    seeyan.secureSiteRole = u'Antagonist'
    seeyan.surname = 'Kelly'
    plone.api.content.transition(obj=seeyan, transition='publish')
    seeyan.reindexObject()
    haether = bwh[bwh.invokeFactory('Person', 'kincaid-haether')]
    haether.accountName = 'haether'
    haether.degrees = [u'BS Biology', u'MS Bioinformatics']
    haether.edrnTitle = u'Operations Lead'
    haether.givenName = u'Haether'
    haether.investigatorStatus = u'Peon'
    haether.mailingAddress = u'PO Box 429-169'
    haether.mbox = u'heather.kincaid@jpl.nasa.gov'
    haether.memberType = u'Informatics Center'
    haether.phone = u'+1 469 555 3129'
    haether.physicalAddress = u'1610 5th St'
    haether.piUID = piUID
    haether.salutation = u'Mr'
    haether.shippingAddress = u'1610 5th St'
    haether.specialty = u'Informatics'
    haether.secureSiteRole = u'Antagonist'
    haether.surname = 'Kincaid'
    plone.api.content.transition(obj=haether, transition='publish')
    haether.reindexObject()
