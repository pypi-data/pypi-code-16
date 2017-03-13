# coding: utf-8
# pylint: disable=W0622
"""cubicweb-saem-ref application packaging information"""

modname = 'saem_ref'
distname = 'cubicweb-saem-ref'

numversion = (0, 14, 3)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
author = 'LOGILAB S.A. (Paris, FRANCE)'
author_email = 'contact@logilab.fr'
description = "Référenciel de Système d'Archivage Électronique Mutualisé"
web = 'http://www.cubicweb.org/project/%s' % distname

__depends__ = {
    'cubicweb[pyramid]': '>= 3.24.0',
    'cubicweb-squareui': None,
    'cubicweb-eac': '< 0.4.0',
    'cubicweb-seda': '>= 0.5.1, < 0.7.0',
    'cubicweb-compound': '>= 0.3.0, < 0.5.0',
    'cubicweb-oaipmh': '>= 0.3.0',
    'cubicweb-relationwidget': '>= 0.3.3',
    'cubicweb-skos': '>= 1.0.0',
    'cubicweb-prov': '< 0.4.0',
    'cubicweb-vtimeline': None,
    'cubicweb-signedrequest': None,
    'python-dateutil': None,
    'pytz': None,
    'psycopg2': None,
    'rdflib': '>= 4.1',
}
__recommends__ = {}

classifiers = [
    'Environment :: Web Environment',
    'Framework :: CubicWeb',
    'Programming Language :: Python',
    'Programming Language :: JavaScript',
]
