from pybuilder.core import init
import setuptools_scm


@init
def initialize_my_plugin(project):
    project.version = setuptools_scm.get_version()
