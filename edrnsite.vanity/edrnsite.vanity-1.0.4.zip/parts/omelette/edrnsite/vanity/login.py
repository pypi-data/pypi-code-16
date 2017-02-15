# encoding: utf-8
# Copyright 2013–2017 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

u'''Loging event handling — create a vanity page or remind people to visit theirs.'''

# Caveman
from five import grok

# Users
from AccessControl import Unauthorized
from Products.PlonePAS.plugins.ufactory import PloneUser
from Products.PluggableAuthService.interfaces.events import IUserLoggedInEvent

# Vanity
from edrnsite.vanity import VANITY_UPDATE_KEY, BESPOKE_WELCOME, BESPOKE_OLD, NAG_LIMIT, vanityPagesEnabled
from eke.site.interfaces import IPerson

# Zope component arch
from zope.component import getUtility

# Content
from plone.dexterity.utils import createContentInContainer

# Utilities
from datetime import date, datetime
from DateTime import DateTime
from plone.i18n.normalizer.interfaces import IIDNormalizer
from Products.CMFCore.utils import getToolByName
import logging, plone.api

# Logging
_logger = logging.getLogger(__name__)


@grok.subscribe(IUserLoggedInEvent)
def checkVanityPage(event):
    '''Upon logging in, check to see if the user has a vanity page.  If not, make one.
    If so, see if the user has visited it recently.  If not, nag the user.
    '''
    if not vanityPagesEnabled(): return
    portal = plone.api.portal.get()

    # Now check the user
    user = event.object
    if not isinstance(user, PloneUser):
        # We make member pages only for Plone accounts. Zope admin & others: shoo.
        return

    # Find the user's page
    try:
        memberFolder = portal.restrictedTraverse('member-pages')
    except (KeyError, Unauthorized):
        # member-pages folder is either missing or private, so don't bother
        _logger.exception('No accessible member-pages folder in the portal; no bespoke pages')
        return
    normalizer = getUtility(IIDNormalizer)
    memberPageID = normalizer.normalize(user.getUserId())
    sdm = getToolByName(portal, 'session_data_manager')
    session = sdm.getSessionData(create=True)
    if not memberPageID in memberFolder:
        try:
            _logger.info("Finding user %s's Person page", user.getUserId())
            catalog = plone.api.portal.get_tool('portal_catalog')
            results = catalog(object_provides=IPerson.__identifier__, accountName=user.getUserId())
            if not results:
                _logger.info("User %s doesn't have a Person page, so no bespoke page either", user.getUserId())
                return
            elif len(results) > 1:
                _logger.info("User %s has multiple Person pages, which is weird.  We'll use the first one")
            personObject = results[0].getObject()
            _logger.info("User %s doesn't have a bespoke page; creating one", memberPageID)
            memberPage = createContentInContainer(
                memberFolder,
                'edrnsite.vanity.bespokepage',
                id=memberPageID,
                title=unicode(user.getProperty('fullname', u'UNKNOWN')),  # FIXME: not i18n
                piUID=personObject.piUID,
                showMbox=False,
                edrnTitle=personObject.edrnTitle,
                specialty=personObject.specialty,
                memberType=personObject.memberType,
                person=personObject
            )
            memberPage.reindexObject()
            session.set(VANITY_UPDATE_KEY, BESPOKE_WELCOME)
        except Unauthorized:
            _logger.exception("member-pages folder isn't writeable")
            return
    else:
        lastNotification = user.getProperty('vanityPageUpdateDate', None)
        if isinstance(lastNotification, DateTime):
            lastNotification = lastNotification.asdatetime()
        lastNotification = date(lastNotification.year, lastNotification.month, lastNotification.day)
        interval = date.today() - lastNotification
        if interval > NAG_LIMIT:
            _logger.info("User %s hasn't been nagged in a long time (%d days); nagging", memberPageID, interval.days)
            session.set(VANITY_UPDATE_KEY, BESPOKE_OLD)
        _logger.info('User logged in: %s, last notified %r', user.getId(), user.getProperty('vanityPageUpdateDate'))
    user.setProperties(vanityPageUpdateDate=datetime.now())
