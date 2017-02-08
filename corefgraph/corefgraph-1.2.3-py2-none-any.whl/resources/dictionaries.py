# coding=utf-8

from corefgraph.properties import lang, default_lang
from logging import getLogger
from importlib import import_module

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'

logger = getLogger(__name__)

try:
    pronouns = import_module("corefgraph.resources.languages.{0}.pronouns".format(lang), __name__)
except ImportError:
    logger.exception("Resource fail (pronouns) loading default")
    pronouns = import_module("corefgraph.resources.languages.{0}.pronouns".format(default_lang), __name__)

try:
    stopwords = import_module("corefgraph.resources.languages.{0}.stopwords".format(lang), __name__)
except ImportError:
    logger.exception("Resource fail (stopwords) loading default")
    stopwords = import_module("corefgraph.resources.languages.{0}.stopwords".format(default_lang), __name__)

try:
    verbs = import_module("corefgraph.resources.languages.{0}.verbs".format(lang), __name__)
except ImportError:
    logger.exception("Resource fail (verbs) loading default")
    verbs = import_module("corefgraph.resources.languages.{0}.verbs".format(default_lang), __name__)

try:
    determiners = import_module("corefgraph.resources.languages.{0}.determiners".format(lang), __name__)
except ImportError:
    logger.exception("Resource fail (determiners) loading default")
    determiners = import_module("corefgraph.resources.languages.{0}.determiners".format(default_lang), __name__)

try:
    temporals = import_module("corefgraph.resources.languages.{0}.temporals".format(lang), __name__)
except ImportError:
    logger.exception("Resource fail (temporals) loading default")
    temporals = import_module("corefgraph.resources.languages.{0}.temporals".format(default_lang), __name__)


