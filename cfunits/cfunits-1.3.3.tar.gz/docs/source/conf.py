# -*- coding: utf-8 -*-
#
# Python cfunits muodule documentation build configuration file, created by
# sphinx-quickstart on Wed Aug 3 16:28:25 2011.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented
# out serve to show the default.

import sys
import os

# If extensions (or modules to document with autodoc) are in another
# directory, add these directories to sys.path here. If the directory
# is relative to the documentation root, use os.path.abspath to make
# it absolute, like shown here.  sys.path.insert(0,os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('../..'))

# -- General configuration ----------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.autosummary',
              'sphinx.ext.viewcode',
              'sphinx.ext.linkcode',
              'sphinx.ext.pngmath',
              'sphinx.ext.mathjax',
              'sphinx.ext.graphviz',
              'sphinx.ext.inheritance_diagram',
              'sphinx.ext.intersphinx',
              'sphinx.ext.doctest',
              ]

# Boolean indicating whether to scan all found documents for
# autosummary directives, and to generate stub pages for each
# (http://sphinx-doc.org/latest/ext/autosummary.html)
autosummary_generate = True

# Both the class’ and the __init__ method’s docstring are concatenated
# and inserted.
autoclass_content = 'both'

inheritance_graph_attrs = {'rankdir': "TB",
                           'clusterrank': 'local'}
inheritance_node_attrs  = {'style': 'filled'}

# This value selects how automatically documented members are sorted
# (http://sphinx-doc.org/latest/ext/autodoc.html)
autodoc_member_order = 'groupwise'

# This value is a list of autodoc directive flags that should be
# automatically applied to all autodoc
# directives. (http://sphinx-doc.org/latest/ext/autodoc.html)
autodoc_default_flags = ['members', 'inherited-members', 'show-inheritance']

intersphinx_cache_limit = 10     # days to keep the cached inventories
intersphinx_mapping = {
    'sphinx':     ('http://sphinx.pocoo.org',  None),
    'python':     ('http://docs.python.org/2.7', None),
    'numpy':      ('http://docs.scipy.org/doc/numpy', None),
    }

# The name of the default domain. Can also be None to disable a
# default domain. The default is 'py'.
#primary_domain = 'cfunits'

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates', '../_templates', '../../_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The encoding of source files.
#source_encoding = 'utf-8-sig'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'Python cfunits package'
copyright = u'2015, David Hassell'

# The version info for the project you're documenting, acts as
# replacement for |version| and |release|, also used in various other
# places throughout the built documents.
#
# The short X.Y version.
version = '1.1'
# The full version, including alpha/beta/rc tags.
release = '1.1.4'

# The language for content autogenerated by Sphinx. Refer to
# documentation for a list of supported languages.
#language = None

# There are two options for replacing |today|: either, you set today
# to some non-false value, then it is used:
#today = ''
#Else, today_fmt is used as the format for a strftime call.
#today_fmt = '%B %d, %Y'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = []

# The reST default role (used for this markup: `text`) to use for all
#documents.
#default_role = None

# If true, '()' will be appended to :func: etc. cross-reference text.
add_function_parentheses = False

# If true, the current module name will be prepended to all
# description unit titles (such as .. function::).
add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in
# the output. They are ignored by default.
#show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
#pygments_style = 'sphinx'

# The default language to highlight source code
highlight_language = 'python'

# A list of ignored prefixes for module index sorting.
#modindex_common_prefix = []


# -- Options for HTML output --------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the
# documentation for a list of builtin themes.
html_theme = 'default'

#/home/opt-user/Enthought/Canopy_64bit/User/lib/python2.7/site-packages/Sphinx-1.2.2-py2.7.egg/sphinx/themes

# Theme options are theme-specific and customize the look and feel of
# a theme further.  For a list of options available for each theme,
# see the documentation.
html_theme_options = {"stickysidebar"   : "true",
                      "externalrefs"    : "false",
                      'sidebarbgcolor'  : '#F2F2F2',
                      'sidebartextcolor': '#777777',
                      'sidebarbgcolor'  : '#F2F2F2',
                      'sidebartextcolor': '#777777',
                      'sidebarlinkcolor': '#003469',
                      'relbarbgcolor'   : '#5682AD',
                      'relbartextcolor' : '#ffffff',
                      'relbarlinkcolor' : '#ffffff',
                      'headbgcolor'     : '#FFFFFF',
                      'headtextcolor'   : '#000000',
                      'codebgcolor'     : '#F2F2F2', #'#F5F5F5',
                      }

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
html_title = "Documentation"

# A shorter title for the navigation bar.  Default is the same as
# html_title.
#html_short_title = None

# The name of an image file (relative to this directory) to place at
# the top of the sidebar.
#html_logo = None

# The name of an image file (within the static path) to use as favicon
# of the docs.  This file should be a Windows icon file (.ico) being
# 16x16 or 32x32 pixels large.
#html_favicon = None

# Add any paths that contain custom static files (such as style
# sheets) here, relative to this directory. They are copied after the
# builtin static files, so a file named "default.css" will overwrite
# the builtin "default.css".
html_static_path = ['_static']

# If not '', a 'Last updated on:' timestamp is inserted at every page
# bottom, using the given strftime format.
html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
#html_sidebars = {'**': ['my_con.html', 'globaltoc.html', 'sourcelink.html']}

# Additional templates that should be rendered to pages, maps page
# names to template names.
#html_additional_pages = {}

# If false, no module index is generated.
#html_domain_indices = True

# If false, no index is generated.
#html_use_index = True

# If true, the index is split into individual pages for each letter.
html_split_index = True #False

# If true, links to the reST sources are added to the pages.
#html_show_sourcelink = True

# If true, "Created using Sphinx" is shown in the HTML footer. Default
# is True.
#html_show_sphinx = True

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is
# True.
#html_show_copyright = True

# If true, an OpenSearch description file will be output, and all
# pages will contain a <link> tag referring to it.  The value of this
# option must be the base URL from which the finished HTML is served.
#html_use_opensearch = ''

# This is the file name suffix for HTML files (e.g. ".xhtml").
#html_file_suffix = None

# Output file base name for HTML help builder.
htmlhelp_basename = 'cfunitsdoc'


# -- Options for LaTeX output -------------------------------------------------

## The paper size ('letter' or 'a4').
#latex_paper_size = 'a4'

# The font size ('10pt', '11pt' or '12pt').
#latex_font_size = '10pt'

# Grouping the document tree into LaTeX files. List of tuples (source
# start file, target name, title, author, documentclass
# [howto/manual]).
latex_documents = [
    ('index', 'cfunits-python.tex', 'cfunits-python Documentation',
     'David Hassell', 'manual'),
    ]

# The name of an image file (relative to this directory) to place at
# the top of the title page.
#latex_logo = None

# For "manual" documents, if this is true, then toplevel headings are
# parts, not chapters.
latex_use_parts = True

# If true, show page references after internal links.
latex_show_pagerefs = False

# If true, show URL addresses after external links.
latex_show_urls = 'footnote'

# Additional stuff for the LaTeX preamble.
#latex_preamble = ''

# Documents to append as an appendix to all manuals.
#latex_appendices = []

# If false, no module index is generated.
latex_domain_indices = True

# A dictionary that contains LaTeX snippets that override those Sphinx
# usually puts into the generated .tex files.
latex_elements = {'papersize': 'a4paper'}

# -- Options for manual page output -------------------------------------------

# One entry per manual page. List of tuples (source start file, name,
# description, authors, manual section).
man_pages = [
    ('index', 'cfunits-python', 'cfunits-python Documentation',
     'David Hassell', 1)
    ]

# Set up copybutton
def setup(app):
    app.add_javascript('copybutton.js')

# This is a function which should return the URL to source code
# corresponding to the object in given domain with given information.

import inspect , cfunits
from os.path import relpath, dirname

def linkcode_resolve(domain, info):
    
    #=================================================================
    # Must delete all .doctrees directories in build for changes to be
    # picked up. E.g.:
    #
    # >> rm -fr build/.doctrees build/*/.doctrees build/*/*/.doctrees
    #=================================================================

    online_source_code = True
#    online_source_code = False

    if domain != 'py':
        return None
    if not info['module']:
        return None
    
    modname = info['module']
    fullname = info['fullname']
    
    submod = sys.modules.get(modname, None)
    if submod is None:
        return None
    
    obj = submod
    for part in fullname.split('.'):
        try:
            obj = getattr(obj, part)
        except:
            return None
    
    try:
        fn = inspect.getsourcefile(obj)
    except:
        fn = None
    if not fn:
        return None
    
    try:
        source, lineno = inspect.findsource(obj)
    except:
        lineno = None
    
    if lineno:
#        linespec = "#cl-%d" % (lineno + 1)
        linespec = "#{0}-{1}".format(fn, lineno+1)
    else:
        linespec = ""
    
    fn = relpath(fn, start=dirname(cfunits.__file__))
    
    # ----------------------------------------------------------------
    # NOTE: You need to touch the .rst files to get the change in
    # ----------------------------------------------------------------
    if online_source_code:
#        commit = '11dddff56c31c24d86c3b83995e503989f90911b'
#        commit = 'master'
        commit = 'v'+release
        return "https://bitbucket.org/cfpython/cfunits-python/src/%s/cfunits/%s%s" % \
            (commit, fn, linespec)
    else:
        # Point to local source code relative to this directory
        return "../../../cfunits/%s%s" % (fn, linespec)
