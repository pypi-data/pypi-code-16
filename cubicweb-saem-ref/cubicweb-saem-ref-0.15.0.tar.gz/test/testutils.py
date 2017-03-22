# copyright 2015 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.
"""cubicweb-saem_ref common test tools"""

from __future__ import print_function

from contextlib import contextmanager
from os.path import join, dirname, exists
import sys

from doctest import Example

from lxml import etree
from lxml.doctestcompare import LXMLOutputChecker

from logilab.common.decorators import monkeypatch

from cubicweb import NoResultError, ValidationError, Unauthorized, devtools
from cubicweb.devtools import testlib


@contextmanager
def assertValidationError(self, cnx):
    with self.assertRaises(ValidationError) as cm:
        yield cm
        cnx.commit()
    cnx.rollback()


@contextmanager
def assertUnauthorized(self, cnx):
    with self.assertRaises(Unauthorized) as cm:
        yield cm
        cnx.commit()
    cnx.rollback()


def _authority(func):
    """Decorator binding an Organization with an NAA configured in
    kwargs['authority'].
    """
    def wrapper(cnx, *args, **kwargs):
        authority = kwargs.get('authority')
        if authority is None:
            kwargs['authority'] = authority_with_naa(cnx)
        else:
            if isinstance(authority, int):
                authority = cnx.entity_from_eid(authority)
            if not authority.ark_naa:
                with cnx.security_enabled(False, False):
                    authority.cw_set(ark_naa=naa(cnx))
        return func(cnx, *args, **kwargs)
    return wrapper


@_authority
def agent(cnx, name, **kwargs):
    """Return an Agent with specified name."""
    return cnx.create_entity('Agent', name=name, **kwargs)


@_authority
def organization_unit(cnx, name, archival_roles=(), **kwargs):
    """Return an OrganizationUnit with specified name and archival roles."""
    roles_eid = [cnx.find('ArchivalRole', name=role)[0][0] for role in archival_roles]
    return cnx.create_entity('OrganizationUnit', name=name,
                             archival_role=roles_eid, **kwargs)


def authority_record(cnx, name, kind=u'person', **kwargs):
    """Return an AuthorityRecord with specified kind and name."""
    kind_eid = cnx.find('AgentKind', name=kind)[0][0]
    if 'ark_naa' not in kwargs:
        authority = authority_with_naa(cnx)
        authority.cw_clear_all_caches()
        kwargs['ark_naa'] = authority.ark_naa
    record = cnx.create_entity('AuthorityRecord',
                               agent_kind=kind_eid, **kwargs)
    cnx.create_entity('NameEntry', parts=name, form_variant=u'authorized',
                      name_entry_for=record)
    return record


def seda_transfer(cnx, **kwargs):
    """Return a 2.0, 1.0, 0.2 compatible SEDATransfer."""
    transfer = setup_profile(cnx)
    cnx.create_entity('SEDAAccessRule',  # mandatory for seda 1.0
                      seda_access_rule=transfer,
                      seda_seq_access_rule_rule=cnx.create_entity(
                          'SEDASeqAccessRuleRule',
                          reverse_seda_start_date=cnx.create_entity('SEDAStartDate')))
    return transfer


def naa(cnx):
    try:
        return cnx.find('ArkNameAssigningAuthority').one()
    except NoResultError:
        return cnx.create_entity('ArkNameAssigningAuthority', who=u'TEST', what=0)


def authority_with_naa(cnx, name=u'Default authority'):
    try:
        authority = cnx.find('Organization', name=name).one()
    except NoResultError:
        return cnx.create_entity('Organization', name=name, ark_naa=naa(cnx))
    if not authority.ark_naa:
        with cnx.security_enabled(False, False):
            authority.cw_set(ark_naa=naa(cnx))
    return authority


def setup_scheme(cnx, title, *labels):
    """Return info new concept scheme"""
    scheme = cnx.create_entity('ConceptScheme', title=title, ark_naa=naa(cnx))
    for label in labels:
        scheme.add_concept(label)
    return scheme


def setup_profile(cnx, **kwargs):
    """Return a minimal SEDA profile."""
    kwargs.setdefault('title', u'Test profile')
    return cnx.create_entity('SEDAArchiveTransfer', ark_naa=naa(cnx), **kwargs)


def create_archive_unit(parent, title=None, **kwargs):
    cnx = kwargs.pop('cnx', getattr(parent, '_cw', None))
    kwargs.setdefault('user_annotation', u'au1')
    au = cnx.create_entity('SEDAArchiveUnit', seda_archive_unit=parent, **kwargs)
    alt = cnx.create_entity('SEDAAltArchiveUnitArchiveUnitRefId',
                            reverse_seda_alt_archive_unit_archive_unit_ref_id=au)
    alt_seq = cnx.create_entity(
        'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement',
        reverse_seda_seq_alt_archive_unit_archive_unit_ref_id_management=alt)
    cnx.create_entity('SEDATitle', seda_title=alt_seq, title=title)
    return au, alt, alt_seq


def create_data_object(transfer, **kwargs):
    cnx = kwargs.pop('cnx', getattr(transfer, '_cw', None))
    create = cnx.create_entity
    kwargs.setdefault('user_annotation', u'bdo1')
    bdo = create('SEDABinaryDataObject', seda_binary_data_object=transfer, **kwargs)
    choice = create('SEDAAltBinaryDataObjectAttachment',
                    reverse_seda_alt_binary_data_object_attachment=bdo)
    create('SEDAAttachment', seda_attachment=choice)  # Choice cannot be empty
    return bdo


def concept(cnx, label):
    """Return concept entity with the given preferred label (expected to be unique)."""
    return cnx.execute('Concept X WHERE X preferred_label L, L label %(label)s',
                       {'label': label}).one()


def map_cs_to_type(scheme, rtype, etype=None):
    cnx = scheme._cw
    cnx.execute('SET CS scheme_relation_type RT WHERE CS eid %(cs)s, RT name %(rt)s',
                {'cs': scheme.eid, 'rt': rtype})
    if etype is not None:
        cnx.execute('SET CS scheme_entity_type ET WHERE CS eid %(cs)s, ET name %(et)s',
                    {'cs': scheme.eid, 'et': etype})


def scheme_for_type(cnx, rtype, etype, *concept_labels):
    scheme = cnx.create_entity('ConceptScheme', title=u'{0}/{1} vocabulary'.format(rtype, etype),
                               ark_naa=naa(cnx))
    map_cs_to_type(scheme, rtype, etype)
    for label in concept_labels:
        scheme.add_concept(label)
    return scheme


class XmlTestMixin(object):
    """Mixin class provinding additional assertion methods for checking XML data."""

    def assertXmlEqual(self, actual, expected):
        """Check that both XML strings represent the same XML tree."""
        checker = LXMLOutputChecker()
        if not checker.check_output(expected, actual, 0):
            message = checker.output_difference(Example("", expected), actual, 0)
            self.fail(message)

    def assertXmlValid(self, xml_data, xsd_filename, debug=False):
        """Validate an XML file (.xml) according to an XML schema (.xsd)."""
        with open(xsd_filename) as xsd:
            xmlschema = etree.XMLSchema(etree.parse(xsd))
        # Pretty-print xml_data to get meaningful line information.
        xml_data = etree.tostring(etree.fromstring(xml_data), pretty_print=True)
        xml_data = etree.fromstring(xml_data)
        if debug and not xmlschema.validate(xml_data):
            print(etree.tostring(xml_data, pretty_print=True))
        xmlschema.assertValid(xml_data)


# speed up tests by using a global configuration ###################################################
_CONFIGS = {}


orig_setup_class = testlib.CubicWebTC.setUpClass


@monkeypatch(testlib.CubicWebTC, methodname='setUpClass')
@classmethod
def setUpClass(cls):
    try:
        config = _CONFIGS[cls.configcls]
    except KeyError:
        # can't use original implementation, else apphome is not correctly
        # detected
        test_module = sys.modules[cls.__module__]
        test_dir = dirname(test_module.__file__)
        config = cls.configcls('data', join(test_dir, 'data'))
        config.mode = 'test'
        assert exists(config._apphome), config._apphome
        _CONFIGS[cls.configcls] = config
    # force call to init_config which may define a particular setup for the fixture
    cls.init_config(config)
    cls.config = config


def startpgcluster(pyfile):
    if devtools.DEFAULT_PSQL_SOURCES['system']['db-host'] == 'REPLACEME':
        devtools.startpgcluster(pyfile)
        import atexit
        atexit.register(devtools.stoppgcluster, pyfile)


class _HCache(dict):
    """Original devtools handler cache prevent caching of several configurations, but that's
    what we're trying to achieve.
    """
    def set(self, config, handler):
        self[config] = handler


devtools.HCACHE = _HCache()
