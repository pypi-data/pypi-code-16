# encoding: utf-8
# Copyright 2012–2016 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

u'''EDRN Site: vanity pages.
'''

from datetime import timedelta
from zope.i18nmessageid import MessageFactory
from zope.component import getUtility
from plone.registry.interfaces import IRegistry

PACKAGE_NAME    = __name__
DEFAULT_PROFILE = u'profile-' + PACKAGE_NAME + ':default'

# Session update key, and possible values
VANITY_UPDATE_KEY = PACKAGE_NAME + '.vanityUpdate'
BESPOKE_OLD       = 'bespoke-old'
BESPOKE_WELCOME   = 'bespoke-welcome'

# How long to wait (in days) before nagging the user
NAG_LIMIT         = timedelta(360)

# i18n
MESSAGE_FACTORY   = MessageFactory(PACKAGE_NAME)


def vanityPagesEnabled():
    return getUtility(IRegistry).get('edrnsite.vanity.enable', False)
