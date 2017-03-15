try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

dependencies = ['pyyaml==3.11', 'requests==2.9.1', 'lxml==3.6.0']
test_dependencies = ['nose']

setup(name='xrunner',
      version='0.1',
      description='Python RESTful API Testing & Microbenchmarking Tool for xml',
      author='Ujjwal Kanth',
      author_email='ujjwal.kanth@unbxd.com',
      keywords=['rest', 'web', 'http', 'testing', 'xml'],
      classifiers=[
          'Environment :: Console',
          'Natural Language :: English',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Topic :: Software Development :: Testing',
          'Topic :: Software Development :: Quality Assurance',
          'Topic :: Utilities'
      ],
      packages=['xrunner'],
      install_requires=dependencies,
      tests_require=test_dependencies,
      # Make this executable from command line when installed
      scripts=['util/xrunner']
      )
