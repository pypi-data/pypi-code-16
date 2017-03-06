# encoding: utf-8
# Copyright 2009 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''Dataset folder.'''
from eea.facetednavigation.interfaces import IPossibleFacetedNavigable
from eke.ecas import ProjectMessageFactory as _
from eke.ecas.config import PROJECTNAME
from eke.ecas.interfaces import IDatasetFolder
from Products.Archetypes import atapi
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.CMFCore.utils import getToolByName
from eke.ecas.utils import setFacetedNavigation
from zope.interface import implements, directlyProvides
from eke.knowledge.content import knowledgefolder
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary

DatasetFolderSchema = knowledgefolder.KnowledgeFolderSchema.copy() + atapi.Schema((
    atapi.StringField(
        'dsSumDataSource',
        required=False,
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u'ECAS Data Summary Statistics Data Source'),
            description=_(u'URL to a source of summary statistics json that describes biomarker data.'),
            size=60,
        ),
    ),
    atapi.StringField(
        'dataSummary',
        required=False,
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u'ECAS Data Summary Statistics Data'),            description=_(u'Summary statistics json that describes biomarker data.'),
            size=10000,
        ),
    ),
))

finalizeATCTSchema(DatasetFolderSchema, folderish=True, moveDiscussion=False)

class DatasetFolder(knowledgefolder.KnowledgeFolder):
    '''Dataset Folder which contains Datasets.'''
    implements(IDatasetFolder, IPossibleFacetedNavigable)
    portal_type               = 'Dataset Folder'
    _at_rename_after_creation = True
    schema                    = DatasetFolderSchema
    dsSumDataSource           = atapi.ATFieldProperty('dsSumDataSource')
    dataSummary               = atapi.ATFieldProperty('dataSummary')

atapi.registerType(DatasetFolder, PROJECTNAME)

def addFacetedNavigation(obj, event):
    '''Set up faceted navigation on all newly created Dataset Folders.'''
    if not IDatasetFolder.providedBy(obj): return
    factory = getToolByName(obj, 'portal_factory')
    if factory.isTemporary(obj): return
    request = obj.REQUEST
    setFacetedNavigation(obj, request)

def IndicatedOrgansVocabularyFactory(context):
    '''Get a vocab for indicated organs'''
    catalog = getToolByName(context, 'portal_catalog')
    results = catalog.uniqueValuesFor('bodySystemName')
    vocabs = []
    for i in results:
        if i:
            vocabs.append((i, i))
    return SimpleVocabulary.fromItems(vocabs)
directlyProvides(IndicatedOrgansVocabularyFactory, IVocabularyFactory)
