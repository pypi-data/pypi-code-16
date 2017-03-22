# coding: utf-8
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
"""cubicweb-saem-ref site customizations"""

import pytz

from logilab.common.date import ustrftime
from logilab.common.decorators import monkeypatch

from cubicweb import cwvreg, _
from cubicweb.cwconfig import register_persistent_options
from cubicweb.uilib import PRINTERS
from cubicweb.entity import Entity
from cubicweb.web import request

from cubes.skos import rdfio
from cubes.skos.ccplugin import ImportSkosData
from cubicweb_seda import dataimport as seda

from . import permanent_url, _massive_store_factory, _nohook_store_factory

# this import is needed to take account of pg_trgm monkeypatches
# while executing cubicweb-ctl commands (db-rebuild-fti)
from . import pg_trgm  # noqa pylint: disable=unused-import


# override Entity.rest_path to use ark for entities which have one

_orig_rest_path = Entity.rest_path


@monkeypatch(Entity)
def rest_path(self, *args, **kwargs):
    """Return ark:/<ARK> is entity has an ark attribute."""
    if getattr(self, 'ark', None) is None:
        return _orig_rest_path(self, *args, **kwargs)
    return u'ark:/' + self.ark


# configure RDF generator to use ark based uri as canonical uris, and deactivating implicit
# 'same_as_urls' in this case

orig_same_as_uris = rdfio.RDFGraphGenerator.same_as_uris


@monkeypatch(rdfio.RDFGraphGenerator, methodname='same_as_uris')
@staticmethod
def same_as_uris(entity):
    if entity.cwuri.startswith('ark:'):
        return ()
    return orig_same_as_uris(entity)


@monkeypatch(rdfio.RDFGraphGenerator, methodname='canonical_uri')
@staticmethod
def canonical_uri(entity):
    return permanent_url(entity)


# deactivate date-format and datetime-format cw properties. This is because we do some advanced date
# manipulation such as allowing partial date and this is not generic enough to allow arbitrary
# setting of date and time formats

base_user_property_keys = cwvreg.CWRegistryStore.user_property_keys


@monkeypatch(cwvreg.CWRegistryStore)
def user_property_keys(self, withsitewide=False):
    props = base_user_property_keys(self, withsitewide)
    return [prop for prop in props if prop not in ('ui.date-format', 'ui.datetime-format')]


# customize display of TZDatetime

register_persistent_options((
    ('timezone',
     {'type': 'choice',
      'choices': pytz.common_timezones,
      'default': 'Europe/Paris',
      'help': _('timezone in which time should be displayed'),
      'group': 'ui', 'sitewide': True,
      }),
))


def print_tzdatetime_local(value, req, *args, **kwargs):
    tz = pytz.timezone(req.property_value('ui.timezone'))
    value = value.replace(tzinfo=pytz.utc).astimezone(tz)
    return ustrftime(value, req.property_value('ui.datetime-format'))


PRINTERS['TZDatetime'] = print_tzdatetime_local


# configure c-c skos-import command's factories to use with proper metadata generator ##############

ImportSkosData.cw_store_factories['massive'] = _massive_store_factory
ImportSkosData.cw_store_factories['nohook'] = _nohook_store_factory


# override seda's scheme initialization to set ark on each scheme, and to use an ark enabled store

@monkeypatch(seda)
def init_seda_scheme(cnx, title, _count=[0]):
    description = u'edition 2009' if title.startswith('SEDA :') else None
    # 25651 = Archives départementales de la Gironde (ADGIRONDE)
    # XXX ensure that:
    # * NAA for those vocabulary is 25651
    # * generated ark are identical from one instance to another (for scheme and concepts, see
    #   below)
    _count[0] += 1
    ark = u'25651/v%s' % _count[0]
    if cnx.vreg.config.repairing:  # XXX seda 0.8 migration
        ark_hack = {
            u'SEDA 2 : Status légaux': 20,
            u'SEDA : Règles de diffusion': 21,
            u"Algorithmes d'empreinte": 22,
        }
        try:
            ark = u'25651/v%s' % ark_hack[title]
        except KeyError:
            pass
    scheme = cnx.create_entity('ConceptScheme', title=title, description=description, ark=ark)
    seda.EXTID2EID_CACHE['ark:/' + ark] = scheme.eid
    return scheme


@monkeypatch(seda)
def get_store(cnx):
    from .sobjects import SAEMMetadataGenerator
    metagen = SAEMMetadataGenerator(cnx, naa_what='25651')
    if cnx.repo.system_source.dbdriver == 'postgres':
        from cubicweb.dataimport.massive_store import MassiveObjectStore
        return MassiveObjectStore(cnx, metagen=metagen, eids_seq_range=1000)
    else:
        from cubicweb.dataimport.stores import NoHookRQLObjectStore
        return NoHookRQLObjectStore(cnx, metagen=metagen)


####################################################################################################
# temporary monkey-patches #########################################################################
####################################################################################################

from yams.constraints import Attribute, BoundaryConstraint, cstr_json_loads  # noqa


@monkeypatch(BoundaryConstraint, methodname='deserialize')
@classmethod
def deserialize(cls, value):
    """simple text deserialization"""
    try:
        values = cstr_json_loads(value)
        return cls(**values)
    except ValueError:
        try:
            value, msg = value.split('\n', 1)
        except ValueError:
            msg = None
        op, boundary = value.split(' ', 1)
        return cls(op, eval(boundary), msg or None)


# proper behaviour of hooks control cm (https://www.cubicweb.org/ticket/17049333)

from cubicweb.server import session  # noqa


@monkeypatch(session)
class _hooks_control(object):
    def __init__(self, cnx, mode, *categories):
        assert mode in (session.HOOKS_ALLOW_ALL, session.HOOKS_DENY_ALL)
        self.cnx = cnx
        self.mode = mode
        self.categories = set(categories)
        self.old_mode = None
        self.old_categories = None

    def __enter__(self):
        self.old_mode = self.cnx._hooks_mode
        self.old_categories = self.cnx._hooks_categories
        self.cnx._hooks_mode = self.mode
        self.cnx._hooks_categories = self.categories

    def __exit__(self, exctype, exc, traceback):
        self.cnx._hooks_mode = self.old_mode
        self.cnx._hooks_categories = self.old_categories


orig_connection_init = session.Connection.__init__


@monkeypatch(session.Connection)
def __init__(self, *args, **kwargs):
    orig_connection_init(self, *args, **kwargs)
    self._hooks_mode = session.HOOKS_ALLOW_ALL
    self._hooks_categories = set()


@monkeypatch(session.Connection)
def is_hook_category_activated(self, category):
    if self._hooks_mode is session.HOOKS_DENY_ALL:
        return category in self._hooks_categories
    return category not in self._hooks_categories


@monkeypatch(request._CubicWebRequestBase)
def negotiated_language(self):
    # Force language to fr since in http-negociation mode there is no way to
    # force french language with a browser configured in english.
    # This is currently the easiest way to force the language of an instance.
    return 'fr'
