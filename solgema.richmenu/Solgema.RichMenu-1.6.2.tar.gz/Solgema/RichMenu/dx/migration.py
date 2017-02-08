import logging
from zope import schema
from zope.interface import Interface
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.interfaces.referenceable import IReferenceable
from Products.CMFCore.utils import getToolByName
from plone.app.uuid.utils import uuidToObject
from zope.annotation.interfaces import IAnnotations
from plone.uuid.interfaces import IUUID
from zope.component import getUtility
try:
    from plone.app.contenttypes.migration.migration import ICustomMigrator
    from plone.app.contenttypes.migration.field_migrators import migrate_filefield, migrate_simplefield
    from plone.app.contenttypes.migration.utils import link_items
    from z3c.relationfield.relation import RelationValue
except:
    class ICustomMigrator(Interface):
        """""" 
try:
    from zope.intid.interfaces import IIntIds
except ImportError:
    from zope.app.intid.interfaces import IIntIds
from Products.ATContentTypes.interfaces.interfaces import IATContentType
from zope.component import adapter
from Products.Five.utilities import marker
from zope.component import getAdapters
from zope.component import getMultiAdapter
from zope.component.hooks import getSite
from zope.interface import implementer
from zope.schema.interfaces import IBool
from zope.component import getAllUtilitiesRegisteredFor
from plone.dexterity.interfaces import IDexterityFTI, IDexterityContent
from Solgema.RichMenu.interfaces import ISolgemaRichMenuMarker, ISolgemaRichMenuAttributes
_logger = logging.getLogger(__name__)

@implementer(ICustomMigrator)
@adapter(ISolgemaRichMenuMarker)
class RichMenuMigator(object):

    def __init__(self, context):
        self.context = context
    
    def migrate(self, old, new):
        marker.mark(new, ISolgemaRichMenuMarker)
            
        for name, field in schema.getFieldsInOrder(ISolgemaRichMenuAttributes):
            migrate_simplefield(old, ISolgemaRichMenuAttributes(new), name, name)

        _logger.info(
            "Migrating RichMenu Settings for %s" % new.absolute_url())
