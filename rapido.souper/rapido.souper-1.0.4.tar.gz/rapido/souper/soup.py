from zope.interface import implements, alsoProvides, Interface
from zope.component import getMultiAdapter, provideUtility, provideAdapter
from souper.interfaces import ICatalogFactory
from souper.soup import get_soup, Record, NodeAttributeIndexer
from repoze.catalog.indexes.field import CatalogFieldIndex
from repoze.catalog.indexes.text import CatalogTextIndex
from repoze.catalog.indexes.keyword import CatalogKeywordIndex
try:
    from souper.plone.interfaces import ISoupRoot
    from souper.plone.locator import StorageLocator
except ImportError:
    from .interfaces import ISoupRoot
    from .locator import StorageLocator
    provideAdapter(StorageLocator, adapts=[Interface])

from rapido.core.interfaces import IStorage, IRapidoApplication

from .catalog import CatalogFactory
from .interfaces import IRecord


class SoupStorage(object):
    implements(IStorage)

    def __init__(self, context):
        self.context = context
        self.id = context.id
        self.root = self.context.root
        provideUtility(CatalogFactory(), ICatalogFactory, name=self.id)
        self._soup = get_soup(self.id, self.root)

    def initialize(self):
        """ setup the storage
        """
        alsoProvides(self.root, ISoupRoot)
        locator = StorageLocator(self.root)
        locator.storage(self.id)
        self._soup = get_soup(self.id, self.root)

    @property
    def soup(self):
        return self._soup

    def create(self):
        """ return a new record
        """
        record = Record()
        rid = self.soup.add(record)
        return getMultiAdapter(
            (self.soup.get(rid), IRapidoApplication(self.context)),
            IRecord)

    def get(self, uid=None):
        """ return an existing record
        """
        try:
            record = self.soup.get(uid)
        except KeyError:
            return None
        return getMultiAdapter(
            (record, IRapidoApplication(self.context)),
            IRecord)

    def delete(self, record):
        """ delete a record
        """
        del self.soup[record.context]

    def search(self, query, sort_index=None, limit=None, sort_type=None,
            reverse=False, names=None, with_size=False):
        """ search for records
        """
        records = self.soup.lazy(query, sort_index=sort_index, limit=limit,
            sort_type=sort_type, reverse=reverse, names=names,
            with_size=with_size)
        app = IRapidoApplication(self.context)
        for record in records:
            yield getMultiAdapter((record(), app), IRecord)

    def records(self):
        for key in self.soup.data.keys():
            yield self.get(key)

    def rebuild(self):
        self.soup.rebuild()

    def clear(self):
        self.soup.clear()

    def reindex(self, record=None):
        if record:
            self.soup.reindex(records=[record.context])
        else:
            self.soup.reindex()

    @property
    def indexes(self):
        return self.soup.catalog.keys()

    def create_index(self, fieldname, indextype):
        catalog = self.soup.catalog
        field_indexer = NodeAttributeIndexer(fieldname)
        if indextype == 'field':
            catalog[fieldname] = CatalogFieldIndex(field_indexer)
        elif indextype == 'keyword':
            catalog[fieldname] = CatalogKeywordIndex(field_indexer)
        elif indextype == 'text':
            catalog[fieldname] = CatalogTextIndex(field_indexer)
