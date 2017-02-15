# encoding: utf-8 # Copyright 2009 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''
EKE Biomarkers: RDF ingest for biomarkers.
'''

from Acquisition import aq_inner, aq_parent
from eke.biomarker.interfaces import IBiomarker
from eke.biomarker.utils import ORGAN_NAME_TO_COLLABORATIVE_GROUP_NAME
from eke.biomarker.cancerdataexpo_client import getBiomarkerLinks
from eke.knowledge import ProjectMessageFactory as _
from eke.knowledge.browser.rdf import KnowledgeFolderIngestor, CreatedObject, RDFIngestException
from eke.knowledge.browser.utils import updateObject
from eke.knowledge.interfaces import IBodySystem
from eke.study.interfaces import IProtocol
from plone.i18n.normalizer.interfaces import IIDNormalizer
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from rdflib import URIRef, ConjunctiveGraph, URLInputSource
from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.publisher.browser import TestRequest
from zExceptions import BadRequest
import uuid, logging
from urllib2 import urlopen

_logger = logging.getLogger(__name__)

EDRNRDFPREFIX                            = "http://edrn.nci.nih.gov/xml/rdf/edrn.rdf#"

# Well-known URI refs
_accessPredicateURI                      = URIRef('http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#AccessGrantedTo')
_biomarkerPredicateURI                   = URIRef('http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#Biomarker')
_biomarkerTypeURI                        = URIRef('http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#Biomarker')
_bmRefResourceURI                        = URIRef('http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#referencesResource')
_bmOrganDataTypeURI                      = URIRef('http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#BiomarkerOrganData')
_bmTitlePredicateURI                     = URIRef('http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#Title')
_certificationPredicateURI               = URIRef('http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#certification')
_hasBiomarkerStudyDatasPredicateURI      = URIRef('http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#hasBiomarkerStudyDatas')
_hasBiomarkerOrganStudyDatasPredicateURI = URIRef('http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#hasBiomarkerOrganStudyDatas')
_hgncPredicateURI                        = URIRef('http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#HgncName')
_typePredicateURI                        = URIRef('http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#Type')
_isPanelPredicateURI                     = URIRef('http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#IsPanel')
_memberOfPanelPredicateURI               = URIRef('http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#memberOfPanel')
_organPredicateURI                       = URIRef('http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#Organ')
_referencesStudyPredicateURI             = URIRef('http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#referencesStudy')
_sensitivityDatasPredicateURI            = URIRef('http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#SensitivityDatas')
_typeURI                                 = URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')
_visibilityPredicateURI                  = URIRef('http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#QAState')

# Certification URIs
_cliaCertificationURI = URIRef('http://www.cms.gov/Regulations-and-Guidance/Legislation/CLIA/index.html')
_fdaCeritificationURI = URIRef('http://www.fda.gov/regulatoryinformation/guidances/ucm125335.htm')

# How many biomarkers we'll tolerate with the same ID before we balk
MAX_NON_UNIQUE_BIOMARKER_IDS = 100

# Interface identifier for EDRN Collaborative Group, from edrnsite.collaborations
_collabGroup = 'edrnsite.collaborations.interfaces.collaborativegroupindex.ICollaborativeGroupIndex'

# Biomuta Subject URI Prefix. Used to locate which biomuta gene name belongs to which objectID in biomarkers
_biomutaSubjectPrefix = 'http://edrn.nci.nih.gov/data/biomuta/'


def flatten(l):
    '''Flatten a list.'''
    for i in l:
        if isinstance(i, list):
            for j in flatten(i):
                yield j
        else:
            yield i


class BiomarkerFolderIngestor(KnowledgeFolderIngestor):
    '''RDF ingestion for biomarkers.'''
    def _pushWorkflow(self, item, wfTool, action='publish'):
        try:
            wfTool.doActionFor(item, action=action)
            item.reindexObject()
        except WorkflowException:
            pass
        for i in item.objectIds():
            subItem = item[i]
            self._pushWorkflow(subItem, wfTool, action)
    def publishBiomarker(self, context, biomarker, predicates):
        wfTool = getToolByName(context, 'portal_workflow')
        if wfTool.getInfoFor(biomarker, 'review_state') != 'published':
            self._pushWorkflow(biomarker, wfTool)
    def retractBiomarker(self, context, biomarker, predicates):
        wfTool = getToolByName(context, 'portal_workflow')
        if wfTool.getInfoFor(biomarker, 'review_state') != 'private':
            self._pushWorkflow(biomarker, wfTool, 'hide')
    def findObjectsByIdentifiers(self, catalog, identifiers):
        '''Use the given catalog to find the given identifiers.  Return a list
        of the matching objects rather than a sequence of brains.'''
        results = catalog(identifier=[unicode(i) for i in identifiers])
        return [i.getObject() for i in results]

    def updateBiomarker(self, obj, uri, predicates, context, statements):
        '''Update a biomarker. Sets various attributes and then adjusts workflow & security.'''
        updateObject(obj, uri, predicates, context)
        if _accessPredicateURI in predicates:
            groupIDs = [unicode(i) for i in predicates[_accessPredicateURI]]
            obj.accessGroups = groupIDs
            settings = [dict(type='group', roles=[u'Reader'], id=i) for i in groupIDs]
            sharing = getMultiAdapter((obj, TestRequest()), name=u'sharing')
            sharing.update_role_settings(settings)
        if _hasBiomarkerStudyDatasPredicateURI in predicates:
            catalog = getToolByName(context, 'portal_catalog')
            protocolUIDs, piUIDs = [], []
            bag = statements[predicates[_hasBiomarkerStudyDatasPredicateURI][0]]
            for subjectURI, objects in bag.iteritems():
                if subjectURI == _typeURI: continue
                # Assume anything else is a list item pointing to BiomarkerStudyData objects
                for bmsd in [statements[i] for i in objects]:
                    # Right now, we use just the "referencesStudy" predicate, if it's present
                    if _referencesStudyPredicateURI not in bmsd: continue
                    results = catalog(
                        identifier=unicode(bmsd[_referencesStudyPredicateURI][0]),
                        object_provides=IProtocol.__identifier__
                    )
                    protocolUIDs.extend([j.UID for j in results])
                    piUIDs.extend([j.piUID for j in results])
                    for k in [j.getObject() for j in results]:
                        self._addBiomarkerToProtocol(obj, k)
            obj.setProtocols(protocolUIDs)
            obj.setPiUIDs(piUIDs)
    def addStatistics(self, bodySystemStudy, bags, statements, normalizer, catalog):
        '''Add study statistics to a body system study.  The bags are
        RDF-style collections of URIRefs to statistics found in the
        statements.'''
        # Gather all the URIs
        sensitivityURIs = []
        for bag in bags:
            preds = statements[bag]
            del preds[_typeURI]
            sensitivityURIs.extend(flatten(preds.values()))
        # For each set of statistics...
        for sensitivityURI in sensitivityURIs:
            predicates = statements[sensitivityURI]
            stats = bodySystemStudy[bodySystemStudy.invokeFactory('Study Statistics', uuid.uuid1())]
            updateObject(stats, sensitivityURI, predicates, catalog)
            stats.title = sensitivityURI
            stats.reindexObject()
    def _addBiomarkerToProtocol(self, biomarker, protocol):
        uid = biomarker.UID()
        current = [i.UID() for i in protocol.biomarkers]
        if uid not in current:
            current.append(uid)
            protocol.setBiomarkers(current)
    def addStudiesToOrgan(self, biomarkerBodySystem, bags, statements, normalizer, catalog):
        '''Add protocol/study-specific information to a biomarker body system.'''
        # Gather all the URIs
        bmStudyDataURIs = []
        # The RDF may contain an empty <hasBiomarkerStudyDatas/>, which means that
        # there will be just an empty Literal '' in the bags list (which will be a
        # one item list). In that case, don't bother adding studies.
        if len(bags) == 1 and unicode(bags[0]) == u'':
            return
        for bag in bags:
            preds = statements[bag]
            del preds[_typeURI]
            bmStudyDataURIs.extend(flatten(preds.values()))
        for studyURI in bmStudyDataURIs:
            bmStudyDataPredicates = statements[studyURI]
            if _referencesStudyPredicateURI not in bmStudyDataPredicates:
                continue
            studies = self.findObjectsByIdentifiers(catalog,
                [unicode(i) for i in bmStudyDataPredicates[_referencesStudyPredicateURI]])
            if len(studies) < 1:
                _logger.warn('Study "%s" not found for biomarker body system "%r"',
                    bmStudyDataPredicates[_referencesStudyPredicateURI][0],
                    biomarkerBodySystem.identifier
                )
                continue
            identifier = normalizer(studies[0].title)
            bodySystemStudy = biomarkerBodySystem[biomarkerBodySystem.invokeFactory('Body System Study', identifier)]
            updateObject(bodySystemStudy, studyURI, bmStudyDataPredicates, catalog)
            bodySystemStudy.title = studies[0].title
            bodySystemStudy.description = studies[0].description
            bodySystemStudy.setProtocol(studies[0].UID())
            self._addBiomarkerToProtocol(aq_parent(aq_inner(aq_parent(aq_inner(bodySystemStudy)))), studies[0])
            if _sensitivityDatasPredicateURI in bmStudyDataPredicates:
                bags = bmStudyDataPredicates[_sensitivityDatasPredicateURI]
                self.addStatistics(bodySystemStudy, bags, statements, normalizer, catalog)
            bodySystemStudy.reindexObject()
    def addMutationSpecificInformation(self, bmId, predicates, biomutastatements):
        '''Populate biomarkers with biomuta (aka "mutation") details.'''
        biomutalookup = URIRef(_biomutaSubjectPrefix + bmId)
        #look for gene name in biomuta list, if exists, then add biomuta predicates to biomarker's
        if biomutalookup in biomutastatements.keys():
            predicates.update(biomutastatements[biomutalookup])
    def addExternaResourcesInformation(self, bmId, predicates, idDataSource):
        #This function is a temporary workaround until we generate the knowledge rdfs for these external resources
        extres = {}
        remove = []
        sum_remove = ["pubmed"] #remove pubmed links, they should be in publications page
        idsummary = None
        if idDataSource:    #skip cancerdataexpo query if idDataSource was not defined in the plone interaface
            if idDataSource.strip() != "":
                idsummary = getBiomarkerLinks(bmId, idDataSource) #get biomarker links generated by CancerDataExpo

        for res in predicates.get(_bmRefResourceURI, []):
            if "genenames" in str(res) and "hgnc_id" in str(res):
                extres[URIRef('http://edrn.nci.nih.gov/xml/rdf/edrn.rdf#reshgnc')] = [res]
                remove.append(res)
                sum_remove.append("resgenename")
            elif "http://www.genome.jp/dbget-bin/www_bget" in str(res):
                extres[URIRef('http://edrn.nci.nih.gov/xml/rdf/edrn.rdf#reskegg')] = [res]
                remove.append(res)
            elif "uniprot" in str(res):
                extres[URIRef('http://edrn.nci.nih.gov/xml/rdf/edrn.rdf#resuniprot')] = [res]
                remove.append(res)
                sum_remove.append("uniprot")
                sum_remove.append("trembl")
            elif "ncbi" in str(res) and "gene" in str(res):
                extres[URIRef('http://edrn.nci.nih.gov/xml/rdf/edrn.rdf#resentrezgene')] = [res]
                remove.append(res)
                sum_remove.append("resentrezgene")
            elif "http://www.ncbi.nlm.nih.gov/protein" in str(res):
                extres[URIRef('http://edrn.nci.nih.gov/xml/rdf/edrn.rdf#proteinref')] = [res]
                remove.append(res)
            elif "http://www.fda.gov" in str(res):
                extres[URIRef('http://edrn.nci.nih.gov/xml/rdf/edrn.rdf#resfda')] = [res]
                remove.append(res)
            elif "http://www.genecards.org/cgi-bin/" in str(res):
                extres[URIRef('http://edrn.nci.nih.gov/xml/rdf/edrn.rdf#resgenecard')] = [res]
                remove.append(res)
                sum_remove.append("symbol")

        for res in remove:
            predicates[_bmRefResourceURI].remove(res)

        if idsummary:
            for summary in sum_remove:
                del idsummary[summary]  #remove summary that have already been populated

            if "genecard" in idsummary:
                if len(idsummary["genecard"]['Items']) > 0:
                    extres[URIRef(EDRNRDFPREFIX+"resgenecard")] = idsummary["genecard"]['Items']
            if "probe_id" in idsummary:
                if len(idsummary["probe_id"]['Items']) > 0:
                    extres[URIRef(EDRNRDFPREFIX+"resprobeid")] = [",".join(idsummary["probe_id"]['Items'])]
            if "uniprot" in idsummary:
                if len(idsummary["uniprot"]['Items']) > 0:
                    extres[URIRef(EDRNRDFPREFIX+"resuniprot")] = idsummary["uniprot"]['Items']
            if "ensembl" in idsummary:
                if len(idsummary["ensembl"]['Items']) > 0:
                    extres[URIRef(EDRNRDFPREFIX+"resensembl")] = idsummary["ensembl"]['Items']
            if "pdb" in idsummary:
                if len(idsummary["pdb"]['Items']) > 0:
                    extres[URIRef(EDRNRDFPREFIX+"respdb")] = idsummary["pdb"]['Items']
            if "pfam" in idsummary:
                if len(idsummary["pfam"]['Items']) > 0:
                    extres[URIRef(EDRNRDFPREFIX+"respfam")] = idsummary["pfam"]['Items']
            if "keggpathwayid" in idsummary:
                if len(idsummary["keggpathwayid"]['Items']) > 0:
                    extres[URIRef(EDRNRDFPREFIX+"reskeggpathway")] = idsummary["keggpathwayid"]['Items']
            if "keggpathwayname" in idsummary:
                if len(idsummary["keggpathwayname"]['Items']) > 0:
                    extres[URIRef(EDRNRDFPREFIX+"reskeggpathwayname")] = idsummary["keggpathwayname"]['Items']
            if "type_of_gene" in idsummary:
                if len(idsummary["type_of_gene"]['Items']) > 0:
                    extres[URIRef(EDRNRDFPREFIX+"resgenetype")] = idsummary["type_of_gene"]['Items']
            if "hgncid" in idsummary:
                if len(idsummary["hgncid"]['Items']) > 0:
                    extres[URIRef(EDRNRDFPREFIX+"resgenename")] = idsummary["hgncid"]['Items']
            if "refseqprotein" in idsummary:
                if len(idsummary["refseqprotein"]['Items']) > 0:
                    extres[URIRef(EDRNRDFPREFIX+"proteinref")] = idsummary["refseqprotein"]['Items']
            if "refseqrna" in idsummary:
                if len(idsummary["refseqrna"]['Items']) > 0:
                    extres[URIRef(EDRNRDFPREFIX+"resrnaseq")] = idsummary["refseqrna"]['Items']
            if "entrezgene" in idsummary:
                if len(idsummary["entrezgene"]['Items']) > 0:
                    extres[URIRef(EDRNRDFPREFIX+"resentrezgene")] = idsummary["entrezgene"]['Items']
            if "trembl" in idsummary:
                if len(idsummary["trembl"]['Items']) > 0:
                    extres[URIRef(EDRNRDFPREFIX+"restrembl")] = idsummary["trembl"]['Items']
            if "summary" in idsummary:
                if len(idsummary["summary"]['Items']) > 0:
                    extres[URIRef(EDRNRDFPREFIX+"resbiosummary")] = idsummary["summary"]['Items']
            if "gwas" in idsummary:
                if len(idsummary["gwas"]['Items']) > 0:
                    extres[URIRef(EDRNRDFPREFIX+"gwasref")] = idsummary["gwas"]['Items']
            if "keggid" in idsummary:
                if len(idsummary["keggid"]['Items']) > 0:
                    extres[URIRef(EDRNRDFPREFIX+"reskegg")] = idsummary["keggid"]['Items']

        extres[URIRef('http://edrn.nci.nih.gov/xml/rdf/edrn.rdf#resentrez')] = [u'http://www.ncbi.nlm.nih.gov/gquery/?term={}{}+{}{}'.format(bmId,"[Gene Symbol]", "Homo Sapiens", "[Organism]")]
        extres[URIRef('http://edrn.nci.nih.gov/xml/rdf/edrn.rdf#ressnp')] = [u'http://www.ncbi.nlm.nih.gov/snp/?term={}{}+{}{}'.format(bmId,"[Gene Symbol]", "Homo Sapiens", "[Organism]")]

        predicates.update(extres)
    def addBiomarkerToOrganGroup(self, biomarker, namedOrgan, catalog):
        u'''Add the given ``biomarker`` to the collaborative group that studies
        the ``namedOrgan``, using the ``catalog`` to find it.
        '''
        groupName = ORGAN_NAME_TO_COLLABORATIVE_GROUP_NAME.get(namedOrgan)
        if not groupName: return
        results = [i.getObject() for i in catalog(object_provides=_collabGroup, Title=groupName)]
        for collabGroup in results:
            currentBiomarkers = collabGroup.getBiomarkers()
            if biomarker not in currentBiomarkers:
                currentBiomarkers.append(biomarker)
                collabGroup.setBiomarkers(currentBiomarkers)
    def addOrganSpecificInformation(self, biomarkers, statements, normalizer, catalog):
        '''Populate biomarkers with body system (aka "organ") details.'''
        for uri, predicates in statements.items():
            try:
                if predicates[_typeURI][0] != _bmOrganDataTypeURI:
                    continue
                biomarker = biomarkers[predicates[_biomarkerPredicateURI][0]]
            except KeyError:
                continue

            organName = unicode(predicates[_organPredicateURI][0])
            results = catalog(Title=organName, object_provides=IBodySystem.__identifier__)
            if len(results) < 1:
                _logger.warn('Unknown organ %s for biomarker %s', organName, biomarker.title)
                continue
            organObjID = normalizer(organName)
            biomarkerBodySystem = biomarker[biomarker.invokeFactory('Biomarker Body System', organObjID)]
            biomarkerBodySystem.setTitle(results[0].Title)
            biomarkerBodySystem.setBodySystem(results[0].UID)
            updateObject(biomarkerBodySystem, uri, predicates, catalog)
            self.addBiomarkerToOrganGroup(biomarker, organName, catalog)
            if _hasBiomarkerOrganStudyDatasPredicateURI in predicates:
                bags = predicates[_hasBiomarkerOrganStudyDatasPredicateURI]
                self.addStudiesToOrgan(biomarkerBodySystem, bags, statements, normalizer, catalog)
            certificationURIs = predicates.get(_certificationPredicateURI, [])
            # TODO: make a separate Certification type so we don't rely on these fixed values.
            # Although we'll likely never have ohter certifications.
            for certificationURI in certificationURIs:
                if certificationURI == _cliaCertificationURI:
                    biomarkerBodySystem.cliaCertification = True
                elif certificationURI == _fdaCeritificationURI:
                    biomarkerBodySystem.fdaCertification = True
            biomarkerBodySystem.reindexObject()
    def getSummaryData(self, source):
        try:
            jsonlines = urlopen(source)
            json = ""
            for line in jsonlines:
                json += line
            return json
        except IOError:
            _logger.warning('HTTP Error when trying to access biomarker summary data source. Skipping summarization...')

    def __call__(self):
        '''Ingest and render a results page.'''
        context = aq_inner(self.context)
        rdfDataSource, bmoDataSource, bmuDataSource, bmSumDataSource, idDataSource = context.rdfDataSource, context.bmoDataSource, context.bmuDataSource, context.bmSumDataSource, context.idDataSource
        if bmSumDataSource:
            context.dataSummary = self.getSummaryData(bmSumDataSource)

        if not rdfDataSource or not bmoDataSource or not bmuDataSource:
            raise RDFIngestException(_(u'This biomarker folder lacks one or both of its RDF source URLs.'))
        # Weapons at ready
        catalog = getToolByName(context, 'portal_catalog')
        normalizerFunction = queryUtility(IIDNormalizer).normalize
        graph = ConjunctiveGraph()
        graph.parse(URLInputSource(rdfDataSource))
        statements = self._parseRDF(graph)

        # Add mutation-specific information
        graph = ConjunctiveGraph()
        graph.parse(URLInputSource(bmuDataSource))
        mutationStatements = self._parseRDF(graph)

        # Clean the slate (but not the subfolders)
        results = catalog(path=dict(query='/'.join(context.getPhysicalPath()), depth=1),
            object_provides=IBiomarker.__identifier__)
        context.manage_delObjects([i.id for i in results])
        newBiomarkers = {}
        # Make all the biomarker objects
        for uri, predicates in statements.items():
            try:
                typeURI = predicates[_typeURI][0]
                if typeURI != _biomarkerTypeURI:
                    continue
                isPanel = bool(int(predicates[_isPanelPredicateURI][0]))
                title = unicode(predicates[_bmTitlePredicateURI][0])
                hgnc = predicates[_hgncPredicateURI][0] if _hgncPredicateURI in predicates else None

                if hgnc is not None:
                    hgnc = hgnc.strip()
                objID = hgnc if hgnc else normalizerFunction(title)
                objType = isPanel and 'Biomarker Panel' or 'Elemental Biomarker'
                try:
                    obj = context[context.invokeFactory(objType, objID)]
                except BadRequest:
                    obj = None
                    for appendedNumber in xrange(1, MAX_NON_UNIQUE_BIOMARKER_IDS+1):
                        try:
                            obj = context[context.invokeFactory(objType, "%s-%d" % (objID, appendedNumber))]
                            break
                        except BadRequest:
                            pass
                    if obj is None:
                        raise BadRequest("Something's wrong. Got more than %d biomarkers with the same ID '%s'!" %
                            (MAX_NON_UNIQUE_BIOMARKER_IDS, objID))
                if not isPanel:
                    #Append biomuta's predicates if gene symbol exists in biomuta's list as well
                    self.addMutationSpecificInformation(objID, predicates, mutationStatements)
                    # Disabled because it causes the ingest to take multiple hours instead of just 1 hour
                    # See CA-1434 (kelly 2016-12-06)
                    # self.addExternaResourcesInformation(objID, predicates, idDataSource)
                    #Add frequencies for biomarker associated with biomarker type (Gene, Protein, etc...)
                #Update biomarker, if biomuta was added, biomuta predicates will be updated as well
                self.updateBiomarker(obj, uri, predicates, context, statements)
                newBiomarkers[uri] = obj
                obj.reindexObject()
            except KeyError:
                pass
        # Connect elementals to their panels
        for uri, predicates in statements.items():
            try:
                typeURI = predicates[_typeURI][0]
                if typeURI != _biomarkerTypeURI:
                    continue
                biomarkerUID = newBiomarkers[uri].UID()
                panelURIs = predicates[_memberOfPanelPredicateURI]
                panels = self.findObjectsByIdentifiers(catalog, panelURIs)
                for panel in panels:
                    current = [i.UID() for i in panel.members]
                    current.append(biomarkerUID)
                    panel.setMembers(current)

            except KeyError:
                pass
        # Add organ-specific information
        graph = ConjunctiveGraph()
        graph.parse(URLInputSource(bmoDataSource))
        organStatements = self._parseRDF(graph)
        self.addOrganSpecificInformation(newBiomarkers, organStatements, normalizerFunction, catalog)

        # Update indicated organs:
        for biomarker in newBiomarkers.values():
            biomarker.updatedIndicatedBodySystems()
            biomarker.reindexObject()
        # Publish as necessary
        for uri, predicates in statements.items():
            if uri in newBiomarkers:
                biomarker = newBiomarkers[uri]
                if biomarker.qaState == 'Private':
                    self.retractBiomarker(context, biomarker, predicates)
                else:
                    self.publishBiomarker(context, biomarker, predicates)
        self.objects = [CreatedObject(i) for i in newBiomarkers.values()]
        return self.render and self.template() or len(self.objects)
