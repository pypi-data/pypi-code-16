# -*- coding: utf-8 -*-
#
# Copyright (c) The PyAMF Project.
# See LICENSE.txt for details.
#
# Documentation build configuration file.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# file.
#
# All configuration values have a default value; values that are
# commented out serve to show the default value.

import sys, os, time
from shutil import copyfile

from docutils.core import publish_parts


# If extensions (or modules to document with autodoc) are in another
# directory, add these directories to sys.path here. If the directory
# is relative to the documentation root, use os.path.abspath to make
# it absolute.
sys.path.insert(0, os.path.abspath('..'))


# When ReadTheDocs.org builds your project, it sets the READTHEDOCS
# environment variable to the string True.
on_rtd = os.environ.get('READTHEDOCS', None) == 'True'

# -- General configuration -----------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be extensions
# coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
#
# Make sure to install the following Sphinx extension module as well:
# - http://packages.python.org/sphinxcontrib-epydoc
extensions = [
    'sphinx.ext.intersphinx',
    'sphinx.ext.autodoc'
]

templates_path = ['html']

# The suffix of source filenames.
source_suffix = '.rst'

# The encoding of source files.
#source_encoding = 'utf-8'

# create content template for the homepage
changelog = copyfile('../CHANGES.rst', 'changelog.rst')

# General substitutions.
project = 'Mini-AMF'
url = 'http://miniamf.github.io'
description = 'AMF Encoding and Decoding for Python'
copyright = "2007-2015 The PyAMF Project"

# We look for the __init__.py file in the current Mini-AMF source tree
# and replace the values accordingly.
import miniamf

# The full version, including alpha/beta/rc tags.
version = str(miniamf.version)

# The short X.Y version.
release = version[:3]

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
#today = ''
# Else, today_fmt is used as the format for a strftime call.
today_fmt = '%B %d, %Y'

# List of documents that shouldn't be included in the build.
#unused_docs = []

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['build', 'tutorials/examples']

# If true, '()' will be appended to :func: etc. cross-reference text.
add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
#show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
#pygments_style = 'pygments'

# A list of ignored prefixes for module index sorting.
#modindex_common_prefix = []

# Warnings to suppress
# The badges in README.rst are excluded from the Sphinx build,
# but produce warnings anyway; no other external images are involved
suppress_warnings = ['image.nonlocal_uri']

# -- Options for HTML output ---------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'default'

# Additional templates that should be rendered to pages, maps page names to
# template names.
#html_additional_pages = {
#    'index': 'defindex.html',
#}

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#html_theme_options = {}

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
html_title = '%s - %s' % (project, description)

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['html/static']

# The name of an image file (.ico) that is the favicon of the docs.
html_favicon = 'html/static/pyamf.ico'

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
#html_use_smartypants = True

# If false, no module index is generated.
html_use_modindex = True

# If true, the reST sources are included in the HTML build as _sources/<name>.
html_copy_source = False

# Output an OpenSearch description file.
html_use_opensearch = 'https://miniamf.readthedocs.io'

# Output file base name for HTML help builder.
htmlhelp_basename = 'pyamf' + release.replace('.', '')

# Split the index
html_split_index = True


# -- Options for LaTeX output --------------------------------------------------

# The paper size ('letter' or 'a4').
#latex_paper_size = 'letter'

# The font size ('10pt', '11pt' or '12pt').
#latex_font_size = '10pt'

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto/manual]).
latex_documents = [
  ('index', 'PyAMF.tex', html_title,
   copyright, 'manual'),
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
latex_logo = 'html/static/logo.png'

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
#latex_use_parts = False

# Additional stuff for the LaTeX preamble.
#latex_preamble = ''

# Documents to append as an appendix to all manuals.
#latex_appendices = []

# If false, no module index is generated.
#latex_use_modindex = True


# -- Options for external links ----------------------------------------------

# refer to the Python standard library.
intersphinx_mapping = {'python': ('http://docs.python.org', None)}

# A list of regular expressions that match URIs that should
# not be checked when doing a 'make linkcheck' build (since Sphinx 1.1)
linkcheck_ignore = [r'http://localhost:\d+/']
