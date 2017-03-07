
from zope import schema
from zope.interface import Interface
from zope.interface import implements
# from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

from c2.patch.contentpaste import ContentPasteMessageFactory as _



class IContentPasteControlPanel(Interface):
    """IContentPasteControlPanel ControlPanel setting interface
    """

    annotation_ids = schema.List(
        required=False,
        unique=True,
        title=_(u"ANNOTATION_IDs"),
        default=[],
        value_type = schema.TextLine(title=(u"Annotation ID"))
        )
