

from ast import parse
import os
from setuptools import setup
from sys import version_info


def version():
    """Return version string from pattern/__init__.py."""
    with open(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                           'pattern',
                           '__init__.py')) as input_file:
        for line in input_file:
            if line.startswith('__version__'):
                return parse(line).body[0].value.s

install_requires = ["beautifulsoup4",
                    "cherrypy",
                    "docx",
                    "feedparser",
                    "pdfminer" if version_info[0] == 2 else "pdfminer3k",
                    "pdfminer3k",
                    "simplejson", 'pdfminer.six']

setup(
    name="pattern3",
    version="3.0.0",
    description="Web mining module for Python.",
    license="BSD",
    author="Tom De Smedt",
    author_email="tom@organisms.be",
    url="http://www.clips.ua.ac.be/pages/pattern",
    packages=["pattern3",
              "pattern3.web",
              "pattern3.web.cache",
              "pattern3.web.imap",
              "pattern3.web.locale",
              "pattern3.web.oauth",
              "pattern3.db",
              "pattern3.text",
              "pattern3.text.de",
              "pattern3.text.en",
              "pattern3.text.en.wordlist",
              "pattern3.text.en.wordnet",
              "pattern3.text.en.wordnet.pywordnet",
              "pattern3.text.es",
              "pattern3.text.fr",
              "pattern3.text.it",
              "pattern3.text.nl",
              "pattern3.vector",
              "pattern3.vector.svm",
              "pattern3.graph",
              "pattern3.server"
    ],
    package_data={"pattern3": ["*.js"],
                  "pattern3.web.cache": ["tmp/*"],
                  "pattern3.web.locale": ["__init__.py"],
                  "pattern3.text.de": ["*.txt", "*.xml"],
                  "pattern3.text.en": ["*.txt", "*.xml", "*.slp"],
                  "pattern3.text.en.wordlist": ["*.txt"],
                  "pattern3.text.en.wordnet": ["*.txt", "dict/*"],
                  "pattern3.text.en.wordnet.pywordnet": ["*.py"],
                  "pattern3.text.es": ["*.txt", "*.xml"],
                  "pattern3.text.fr": ["*.txt", "*.xml"],
                  "pattern3.text.it": ["*.txt", "*.xml"],
                  "pattern3.text.nl": ["*.txt", "*.xml"],
                  "pattern3.vector": ["*.txt"],
                  "pattern3.vector.svm": ["*.txt", "libsvm-3.11/*", "libsvm-3.17/*", "liblinear-1.93/*"],
                  "pattern3.graph": ["*.js", "*.csv"],
                  "pattern3.server": ["static/*"],
    },
    py_modules=["pattern3.metrics",
                "pattern3.text.search",
                "pattern3.text.tree"
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: Dutch",
        "Natural Language :: English",
        "Natural Language :: French",
        "Natural Language :: German",
        "Natural Language :: Italian",
        "Natural Language :: Spanish",
        "Operating System :: OS Independent",
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        "Programming Language :: JavaScript",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Text Processing :: Markup :: HTML"
    ],
    zip_safe=True,
    install_requires=install_requires
)
