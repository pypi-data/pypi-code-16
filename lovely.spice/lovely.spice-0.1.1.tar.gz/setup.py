import os
import re
import ConfigParser

from setuptools import setup, find_packages


VERSION = "?"
execfile(os.path.join(os.path.dirname(__file__),
                      'src/lovely/spice/__init__.py'))


def get_versions():
    """picks the versions from version.cfg and returns them as dict"""
    versions_cfg = os.path.join(os.path.dirname(__file__), 'versions.cfg')
    config = ConfigParser.ConfigParser()
    config.optionxform = str
    config.readfp(open(versions_cfg))
    return dict(config.items('versions'))


def nailed_requires(requirements, pat=re.compile(r'^(.+)(\[.+\])?$')):
    """returns the requirements list with nailed versions"""
    versions = get_versions()
    res = []
    for req in requirements:
        if '[' in req:
            name = req.split('[', 1)[0]
        else:
            name = req
        if name in versions:
            res.append('%s==%s' % (req, versions[name]))
        else:
            res.append(req)
    return res

requires = [
    'jinja2',
]

setup(name='lovely.spice',
      version=VERSION,
      author='lovely',
      author_email='hello@lovelysystems.com',
      packages=find_packages('src'),
      include_package_data=True,
      package_dir={'': 'src'},
      extras_require=dict(
          test=nailed_requires([
              'collective.xmltestreport',
          ]),
          documentation=nailed_requires([
          ]),
      ),
      zip_safe=False,
      install_requires=nailed_requires(requires),
      test_suite="lovely.spice",
      entry_points={
          'console_scripts': [
            'render=lovely.spice.render:main',
          ],
      },
)
