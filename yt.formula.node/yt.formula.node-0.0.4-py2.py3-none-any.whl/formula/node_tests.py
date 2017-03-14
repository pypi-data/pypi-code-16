"""
Tests for the node formula
"""
from __future__ import unicode_literals
import os
import tempfile
import shutil

from sprinter.testtools import FormulaTest

source_config = """
[update]
formula = yt.formula.node
version = 0.10.16
packages =
  grunt-cli@0.3.1
"""

target_config = """
[install]
formula = yt.formula.node
version = 0.10.16
packages =
  grunt-cli

[update]
formula = yt.formula.node
version = 0.10.16
"""


class TestNodeFormula(FormulaTest):
    """
    Run node.js formula tests
    """
    def setup(self):
        super(TestNodeFormula, self).setup(source_config=source_config,
                                           target_config=target_config)

    def test_install(self):
        self.environment.run_feature('install', 'sync')
        assert os.path.exists(self.environment.directory.install_directory('install'))
        assert os.path.exists(os.path.join(self.environment.directory.install_directory('install'), 'bin', 'node'))
        assert os.path.exists(os.path.join(self.environment.directory.install_directory('install'), 'bin', 'npm'))
        assert os.path.exists(os.path.join(self.environment.directory.install_directory('install'), 'bin', 'grunt'))

    def skip_update(self):
        self.environment.run_feature('update', 'install')
        self.environment.run_feature('update', 'sync')
        assert os.path.exists(self.environment.directory.install_directory('update'))
        assert not os.path.exists(os.path.join(self.environment.directory.install_directory('update'), 'bin', 'grunt'))
