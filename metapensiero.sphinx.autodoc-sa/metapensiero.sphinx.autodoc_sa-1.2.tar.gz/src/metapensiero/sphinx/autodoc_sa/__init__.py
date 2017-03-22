# -*- coding: utf-8 -*-
# :Project:   metapensiero.sphinx.autodoc_sa -- Pretty print canned SQLAlchemy statements
# :Created:   mar 11 ago 2015 11:44:44 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2015, 2016, 2017 Lele Gaifax
#

from sphinx.ext import autodoc
from sqlalchemy.sql import ClauseElement
from sqlalchemy.orm import Query

try:
    from sqlparse import format as sqlformat
except ImportError:
    sqlformat = None


dialect = None

def select_sa_dialect(app):
    global dialect
    classname = app.config.autodoc_sa_dialect
    if classname:
        modulename, classname = classname.rsplit('.', 1)
        module = __import__(modulename, fromlist=[classname])
        dialect = getattr(module, classname)()
    else:
        dialect = None


def stringify(stmt):
    if isinstance(stmt, Query):
        stmt = stmt.statement
    if dialect is not None:
        stmt = stmt.compile(dialect=dialect)
    sql = str(stmt)
    if sqlformat is not None:
        sql = sqlformat(sql, reindent=True)
    return sql


class AttributeDocumenter(autodoc.AttributeDocumenter):
    """
    Customized AttributeDocumenter that knows about SA Select
    """

    def add_directive_header(self, sig):
        if not isinstance(self.object, (ClauseElement, Query)):
            autodoc.AttributeDocumenter.add_directive_header(self, sig)
        else:
            autodoc.ClassLevelDocumenter.add_directive_header(self, sig)

    def add_content(self, more_content, no_docstring=False):
        autodoc.AttributeDocumenter.add_content(self, more_content, no_docstring)
        if isinstance(self.object, (ClauseElement, Query)):
            sql = stringify(self.object)
            self.add_line("", "")
            self.add_line(".. code-block:: sql", "")
            self.add_line("", "")
            for line in sql.splitlines():
                self.add_line("   " + line, "")


class DataDocumenter(autodoc.DataDocumenter):
    """
    Customized DataDocumenter that knows about SA Select
    """

    def add_directive_header(self, sig):
        if not isinstance(self.object, (ClauseElement, Query)):
            autodoc.DataDocumenter.add_directive_header(self, sig)
        else:
            autodoc.ModuleLevelDocumenter.add_directive_header(self, sig)

    def add_content(self, more_content, no_docstring=False):
        autodoc.DataDocumenter.add_content(self, more_content, no_docstring)
        if isinstance(self.object, (ClauseElement, Query)):
            sql = stringify(self.object)
            self.add_line("", "")
            self.add_line(".. code-block:: sql", "")
            self.add_line("", "")
            for line in sql.splitlines():
                self.add_line("   " + line, "")


def setup(app):
    "Setup the Sphinx environment."

    autodoc.add_documenter(AttributeDocumenter)
    autodoc.add_documenter(DataDocumenter)
    app.add_config_value('autodoc_sa_dialect', None, False)
    app.connect('builder-inited', select_sa_dialect)
