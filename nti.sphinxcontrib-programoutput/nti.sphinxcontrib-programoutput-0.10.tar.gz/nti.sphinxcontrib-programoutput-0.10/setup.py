from __future__ import print_function

import sys

from setuptools import setup


print("WARNING: This fork is no longer needed. Please just install sphinxcontrib-programoutput.",
	  file=sys.stderr)

long_desc = """
===============================
nti.sphinxcontrib-programoutput
===============================

.. warning::
     This fork of sphinxcontrib-programoutput is no longer needed.
     Just install sphinxcontrib-programoutput >= 0.9 directly.

"""

setup(
	name="nti.sphinxcontrib-programoutput",
	description="Install sphinxcontrib-programoutput instead.",
	long_description=long_desc,
	version="0.10",
	install_requires=[
		'sphinxcontrib-programoutput',
	]
)
