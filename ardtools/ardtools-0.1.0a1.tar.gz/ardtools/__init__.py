"""
__init__.py
    package __init__ for the ardtools package.
"""

# standard library imports

# package specific imports
from .version import get_package_version_str


########################################################################
# Atributes
########################################################################

__author__ = "Alan Staniforth <devops@erehwon.xyz>"
__copyright__ = "Copyright (c) 2004-2010 Alan Staniforth"
__license__ = "New-style BSD"
__version__ = get_package_version_str()


########################################################################
# Interface
########################################################################

__all__ = [
            # Modules
            'tools', 'util', 'version', 'cli'
            ]
