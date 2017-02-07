import sys

from setuptools import setup, find_packages


with open('README.adoc') as f_:
    long_description = f_.read()


def main():
    setup(name='awh',
          description='Webhook creator and deployer',
          long_description=long_description,
          use_scm_version={'write_to': 'src/awh/_version.py'},
          license='MIT',
          author='Michał Góral',
          author_email='dev@mgoral.org',
          url='https://gitlab.com/mgoral/awh',
          platforms=['linux'],
          setup_requires=['setuptools_scm'],
          install_requires=['werkzeug==0.11',
                            'jsonpath-rw==1.4.0'],

          # https://pypi.python.org/pypi?%3Aaction=list_classifiers
          classifiers=['Development Status :: 2 - Pre-Alpha',
                       'Environment :: Console',
                       'Intended Audience :: Developers',
                       'License :: OSI Approved :: MIT License',
                       'Natural Language :: English',
                       'Operating System :: POSIX',
                       'Programming Language :: Python :: 3 :: Only',
                       'Topic :: Software Development :: Libraries',
                       'Topic :: System :: Networking',
                       'Topic :: System :: Networking :: Monitoring',
                       'Topic :: System :: Systems Administration',
                       ],

          packages=find_packages('src'),
          package_dir={'': 'src'},
          entry_points={
              'console_scripts': ['awh-validate=awh.validator:main'],
          },
          )

if __name__ == '__main__':
    assert sys.version_info >= (3, 3)
    main()
