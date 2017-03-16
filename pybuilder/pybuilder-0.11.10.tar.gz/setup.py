#!/usr/bin/env python

from setuptools import setup
from setuptools.command.install import install as _install

class install(_install):
    def pre_install_script(self):
        pass

    def post_install_script(self):
        pass

    def run(self):
        self.pre_install_script()

        _install.run(self)

        self.post_install_script()

if __name__ == '__main__':
    setup(
        name = 'pybuilder',
        version = '0.11.10',
        description = 'PyBuilder',
        long_description = 'PyBuilder\n=========\n\n`PyBuilder <http://pybuilder.github.io>`_\n\n`|Build Status| <http://travis-ci.org/pybuilder/pybuilder>`_ `|Windows\nbuild status| <https://ci.appveyor.com/project/mriehl/pybuilder>`_\n`|PyPI version| <https://warehouse.python.org/project/pybuilder/>`_\n`|Coverage\nStatus| <https://coveralls.io/r/pybuilder/pybuilder?branch=master>`_\n`|Ready in backlog| <https://waffle.io/pybuilder/pybuilder>`_ `|Open\nbugs| <https://waffle.io/pybuilder/pybuilder>`_\n\nPyBuilder is a software build tool written in 100% pure Python, mainly\ntargeting Python applications.\n\nPyBuilder is based on the concept of dependency based programming, but\nit also comes with a powerful plugin mechanism, allowing the\nconstruction of build life cycles similar to those known from other\nfamous (Java) build tools.\n\nPyBuilder is running on the following versions of Python: 2.6, 2.7, 3.3,\n3.4, 3.5 and PyPy.\n\nSee the `Travis Build <https://travis-ci.org/pybuilder/pybuilder>`_ for\nversion specific output.\n\nInstalling\n----------\n\nPyBuilder is available using pip:\n\n::\n\n    $ pip install pybuilder\n\nFor development builds use:\n\n::\n\n    $ pip install --pre pybuilder \n\nSee the `Cheeseshop\npage <https://warehouse.python.org/project/pybuilder/>`_ for more\ninformation.\n\nGetting started\n---------------\n\nPyBuilder emphasizes simplicity. If you want to build a pure Python\nproject and use the recommended directory layout, all you have to do is\ncreate a file build.py with the following content:\n\n::\n\n    from pybuilder.core import use_plugin\n\n    use_plugin("python.core")\n    use_plugin("python.unittest")\n    use_plugin("python.coverage")\n    use_plugin("python.distutils")\n\n    default_task = "publish"\n\nSee the `PyBuilder homepage <http://pybuilder.github.com/>`_ for more\ndetails.\n\nPlugins\n-------\n\nPyBuilder provides a lot of plugins out of the box that utilize tools\nand libraries commonly used in Python projects:\n\n-  `python.coverage <http://pybuilder.github.com/documentation/plugins.html#Measuringunittestcoverage>`_\n   - Uses the standard\n   `coverage <https://warehouse.python.org/project/coverage/>`_ module\n   to calculate unit test line coverage.\n-  `python.distutils <http://pybuilder.github.com/documentation/plugins.html#BuildingaPythonpackage>`_\n   - Provides support to generate and use\n   `setup.py <https://warehouse.python.org/project/setuptools/>`_ files.\n-  **python.django** - Provides support for developing\n   `Django <https://www.djangoproject.com/>`_ applications.\n-  `python.frosted <http://pybuilder.github.io/documentation/plugins.html#Frostedplugin>`_\n   - Lint source files with\n   `frosted <https://github.com/timothycrosley/frosted>`_\n-  `python.flake8 <http://pybuilder.github.io/documentation/plugins.html#Flake8plugin>`_\n   - Provides support for\n   `flake8 <https://warehouse.python.org/project/flake8/>`_\n-  `python.pep8 <http://pybuilder.github.io/documentation/plugins.html#Pep8plugin>`_\n   - Provides support for\n   `pep8 <https://warehouse.python.org/project/pep8/>`_\n-  `python.install\\_dependencies <http://pybuilder.github.io/documentation/plugins.html#Installingdependencies>`_\n   - Installs the projects build and runtime dependencies using ``pip``\n-  `python.pychecker <http://pybuilder.github.io/documentation/plugins.html#Pycheckerplugin>`_\n   - Provides support for\n   `pychecker <http://pychecker.sourceforge.net/>`_\n-  `python.Pydev <http://pybuilder.github.io/documentation/plugins.html#ProjectfilesforEclipsePyDev>`_\n   - Generates project files to import projects into `Eclipse\n   PyDev <http://pydev.org/>`_\n-  `python.PyCharm <http://pybuilder.github.io/documentation/plugins.html#ProjectfilesforJetbrainsPyCharm>`_\n   - Generates project files to import projects into `Jetbrains\n   PyCharm <http://www.jetbrains.com/pycharm/>`_\n-  `python.pylint <http://pybuilder.github.io/documentation/plugins.html#Pylintplugin>`_\n   - Executes `pylint <https://bitbucket.org/logilab/pylint/>`_ on your\n   sources.\n-  `python.pymetrics <http://pybuilder.github.io/documentation/plugins.html#Pymetricsplugin>`_\n   - Calculates several metrics using\n   `pymetrics <http://sourceforge.net/projects/pymetrics/>`_\n-  `python.unittest <http://pybuilder.github.com/documentation/plugins.html#RunningPythonUnittests>`_\n   - Executes `unittest <http://docs.python.org/library/unittest.html>`_\n   test cases\n-  `python.integrationtest <http://pybuilder.github.com/documentation/plugins.html#RunningPythonIntegrationTests>`_\n   - Executes python scripts as integrations tests\n-  `python.pytddmon <http://pybuilder.github.io/documentation/plugins.html#Visualfeedbackfortests>`_\n   - Provides visual feedback about unit tests through\n   `pytddmon <http://pytddmon.org/>`_\n-  `python.cram <http://pybuilder.github.io/documentation/plugins.html#RunningCramtests>`_\n   - Runs `cram <https://warehouse.python.org/project/cram/>`_ tests\n-  `python.sphinx <http://pybuilder.github.io/documentation/plugins.html#Creatingdocumentationwithsphinx>`_\n   - Build your documentation with `sphinx <http://sphinx-doc.org/>`_\n-  `python.sonarqube <http://pybuilder.github.io/documentation/plugins.html#SonarQubeintegration>`_\n   - Analyze your project with `SonarQube <http://www.sonarqube.org/>`_.\n-  python.snakefood - Analyze your code dependencies with\n   `snakefood <https://bitbucket.org/blais/snakefood>`_.\n\nIn addition, a few common plugins are provided:\n\n-  `copy\\_resources <http://pybuilder.github.io/documentation/plugins.html#Copyingresourcesintoadistribution>`_\n   - Copies files.\n-  `filter\\_resources <http://pybuilder.github.io/documentation/plugins.html#Filteringfiles>`_\n   - Filters files by replacing tokens with configuration values.\n-  `source\\_distribution <http://pybuilder.github.io/documentation/plugins.html#Creatingasourcedistribution>`_\n   - Bundles a source distribution for shipping.\n\nExternal plugins: \\*\n`pybuilder\\_aws\\_plugin <https://github.com/immobilienscout24/pybuilder_aws_plugin>`_\n- handle AWS functionality\n\nRelease Notes\n-------------\n\nThe release notes can be found\n`here <http://pybuilder.github.com/releasenotes/>`_. There will also be\na git tag with each release. Please note that we do not currently\npromote tags to GitHub "releases".\n\nDevelopment\n-----------\n\nSee `developing\nPyBuilder <http://pybuilder.github.io/documentation/developing_pybuilder.html>`_\n\n.. |Build\nStatus| image:: https://secure.travis-ci.org/pybuilder/pybuilder.png?branch=master\n.. |Windows build\nstatus| image:: https://ci.appveyor.com/api/projects/status/e8fbgcyc7bdqbko3?svg=true\n.. |PyPI version| image:: https://badge.fury.io/py/pybuilder.png\n.. |Coverage\nStatus| image:: https://coveralls.io/repos/pybuilder/pybuilder/badge.png?branch=master\n.. |Ready in\nbacklog| image:: https://badge.waffle.io/pybuilder/pybuilder.png?label=ready&title=Ready\n.. |Open\nbugs| image:: https://badge.waffle.io/pybuilder/pybuilder.png?label=bug&title=Open%20Bugs\n',
        author = 'Alexander Metzner, Maximilien Riehl, Michael Gruber, Udo Juettner, Marcel Wolf, Arcadiy Ivanov, Valentin Haenel',
        author_email = 'alexander.metzner@gmail.com, max@riehl.io, aelgru@gmail.com, udo.juettner@gmail.com, marcel.wolf@me.com, arcadiy@ivanov.biz, valentin@haenel.co',
        license = 'Apache License',
        url = 'http://pybuilder.github.io',
        scripts = ['scripts/pyb'],
        packages = [
            'pybuilder',
            'pybuilder.pluginhelper',
            'pybuilder.plugins',
            'pybuilder.plugins.python'
        ],
        namespace_packages = [],
        py_modules = [],
        classifiers = [
            'Programming Language :: Python',
            'Programming Language :: Python :: Implementation :: CPython',
            'Programming Language :: Python :: Implementation :: PyPy',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: Apache Software License',
            'Topic :: Software Development :: Build Tools',
            'Topic :: Software Development :: Quality Assurance',
            'Topic :: Software Development :: Testing'
        ],
        entry_points = {
            'console_scripts': ['pyb_ = pybuilder.cli:main']
        },
        data_files = [],
        package_data = {
            'pybuilder': ['LICENSE']
        },
        install_requires = [
            'pip>=7.1',
            'setuptools~=32.0',
            'tblib',
            'wheel'
        ],
        dependency_links = [],
        zip_safe = True,
        cmdclass = {'install': install},
        keywords = '',
        python_requires = '!=3.0,!=3.1,!=3.2,<3.7,>=2.6',
        obsoletes = [],
    )
