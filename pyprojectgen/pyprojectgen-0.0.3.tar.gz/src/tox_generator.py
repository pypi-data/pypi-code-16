"""Tox.ini file generator module."""

TOX_INI_TEMPLATE = """
[tox]
envlist = py35
[testenv]
deps=
    nose>=1.0
    coverage>=4.0.3    
commands=
    nosetests --with-coverage --cover-package=src

[testenv:travis]
passenv = TRAVIS TRAVIS_JOB_ID TRAVIS_BRANCH
deps=
    nose>=1.0
    coverage>=4.0.3        
commands=
    nosetests --with-coverage --cover-package=src
"""

class ToxGenerator(object):
    """Tox.ini file generator class."""

    @staticmethod
    def generate(file_path):
        """Generates the tox.ini file for the project."""
        with open(file_path, 'w') as stream:
            stream.write(TOX_INI_TEMPLATE)
