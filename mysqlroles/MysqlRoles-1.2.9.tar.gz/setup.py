from distutils.core import setup

setup(name='MysqlRoles',
      version='1.2.9',
      description='Role Based Access Control (RBAC) for mysql',
      author='Ryan Birmingham',
      author_email='birm@rbirm.us',
      url='http://rbirm.us',
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Programming Language :: Python :: 3.3',
                   'Topic :: Database',
                   'Intended Audience :: Information Technology',
                   'Programming Language :: SQL',
                   'Programming Language :: Python :: 2.7',
                   'Topic :: Security',
                   'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'],
      long_description=open('README.md', 'r').read(),
      packages=['MysqlRoles'],
      )
