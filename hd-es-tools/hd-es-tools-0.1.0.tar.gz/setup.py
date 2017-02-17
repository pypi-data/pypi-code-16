try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools

    use_setuptools()
    from setuptools import setup
import os
import sys

# To test against an Elasticsearch 5.x server we need to use the 5.x
# Python Elasticsearch client, see .travis.yml.
PYTHON_ELASTIC_VERSION = os.environ.get("PYTHON_ELASTIC_VERSION",
                                        ">=2.0.0,<3.0.0")

test_suite = "tests"
tests_require = ["mongo-orchestration>=0.6.7,<1.0",
                 "requests>=2.5.1",
                 "elasticsearch" + PYTHON_ELASTIC_VERSION]

if sys.version_info[:2] == (2, 6):
    # Need unittest2 to run unittests in Python 2.6
    tests_require.append("unittest2")
    test_suite = "unittest2.collector"

try:
    with open("README.rst", "r") as fd:
        long_description = fd.read()
except IOError:
    long_description = None  # Install without README.rst

setup(name='hd-es-tools',
      version='0.1.0',
      author='HaoDou, Inc.',
      description='haodou elasticsearch tools',
      author_email='huangyue@haodou.com',
      long_description=long_description,
      platforms=['any'],
      keywords=['mongo-connector', "mongodb", "elastic", "elasticsearch", "haodou"],
      url='https://github.com/mongodb-labs/elastic2-doc-manager',
      install_requires=['mongo-connector>=2.5.0', 'elasticsearch>=5.0.0,<6.0.0'],
      packages=["hd_es_tools",
                "hd_es_tools.mongo_connector_doc_managers",
                "hd_es_tools.mongo_connector_doc_managers.formatters",
                "hd_es_tools.es_sync",
                "hd_es_tools.es_sync.fav_title_favdir",
                "hd_es_tools.es_sync.fav_title_recipe",
                "hd_es_tools.es_sync.fav_title_sync"],
      package_data={
          'hd_es_tools.mongo_connector_doc_managers': ['config_fav.json'],
          'hd_es_tools.mongo_connector_doc_managers': ['config_favdir.json'],
      },
      license="http://www.apache.org/licenses/LICENSE-2.0.html",
      classifiers=[
          "Development Status :: 4 - Beta",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3.3",
          "Programming Language :: Python :: 3.4",
          "Programming Language :: Python :: 3.5",
          "Topic :: Database",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Operating System :: Unix",
          "Operating System :: MacOS :: MacOS X",
          "Operating System :: Microsoft :: Windows",
          "Operating System :: POSIX"
      ],
      test_suite=test_suite,
      tests_require=tests_require
      )
