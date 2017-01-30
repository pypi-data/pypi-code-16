import logging
from Products.Archetypes import atapi
from Products.CMFCore import utils
from ftw.contentpage import config
from zope.i18nmessageid import MessageFactory


_ = MessageFactory('ftw.contentpage')

logger = logging.getLogger('ftw.contentpage')

# The following patch is a workaround for a bug in Products.TinyMCE < 1.4.0:
# https://github.com/plone/Products.TinyMCE/commit/ccbe5ec5744680f73e4f64fa5d5bd00d37d51a80#comments
logger.info('Patching TinyMCE anchor search pattern.')
from Products.TinyMCE.browser import atanchors
atanchors.SEARCHPATTERN = './/a'


def initialize(context):
    """Initializer called when used as a Zope 2 product.

    This is referenced from configure.zcml. Regstrations as a "Zope 2 product"
    is necessary for GenericSetup profiles to work, for example.

    Here, we call the Archetypes machinery to register our content types
    with Zope and the CMF.
    """

    content_types, constructors, _ftis = atapi.process_types(
        atapi.listTypes(config.PROJECTNAME),
        config.PROJECTNAME)

    for atype, constructor in zip(content_types, constructors):
        utils.ContentInit('%s: %s' % (config.PROJECTNAME, atype.portal_type),
                          content_types=(atype,),
                          permission=config.ADD_PERMISSIONS[atype.portal_type],
                          extra_constructors=(constructor,),
                          ).initialize(context)
