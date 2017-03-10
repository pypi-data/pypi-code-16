import sys

from setuptools import setup, find_packages


with open('README.rst') as f_:
    long_description = f_.read()


def main():
    setup(name='feedcommas',
          description='CommaFeed commandline client',
          long_description=long_description,
          use_scm_version={'write_to': 'src/feedcommas/_version.py'},
          license='GPLv3+',
          author='Michał Góral',
          author_email='dev@mgoral.org',
          url='https://gitlab.com/mgoral/feed-commas',
          platforms=['linux'],
          setup_requires=['setuptools_scm'],
          install_requires=['urwid==1.3.1',
                            'requests==2.13.0',
                            'beautifulsoup4>=4.5.3',
                            'mgcomm>=0.1.0'],

          # https://pypi.python.org/pypi?%3Aaction=list_classifiers
          classifiers=['Development Status :: 4 - Beta',
                       'Environment :: Console',
                       'Environment :: Console :: Curses',
                       'Intended Audience :: End Users/Desktop',
                       'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
                       'Natural Language :: English',
                       'Operating System :: POSIX',
                       'Programming Language :: Python :: 3 :: Only',
                       'Programming Language :: Python :: 3.4',
                       'Programming Language :: Python :: 3.5',
                       'Programming Language :: Python :: 3.6',
                       'Topic :: Software Development :: Libraries',
                       'Topic :: Utilities',
                       ],

          packages=find_packages('src'),
          package_dir={'': 'src'},
          entry_points={
              'console_scripts': ['feed-commas=feedcommas.app:main'],
          },
          )

if __name__ == '__main__':
    assert sys.version_info >= (3, 3)
    main()
