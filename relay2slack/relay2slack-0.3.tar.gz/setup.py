from setuptools import setup


def readme():
    with open('README.rst', 'r') as f:
        return f.read()


setup(name='relay2slack',
      version='0.3',
      description='relay2slack is a tool for capturing and forwarding incoming Slack webhook events',
      long_description=readme(),
      classifiers=['Intended Audience :: Developers',
                   'Intended Audience :: Information Technology',
                   'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
                   'Natural Language :: English',
                   'Operating System :: POSIX :: Linux',
                   'Programming Language :: Python :: 2.7',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   'Topic :: Utilities'],
      keywords='slack webhook kapacitor proxy',
      url='http://github.com/blaketmiller/relay2slack',
      author='Blake Miller',
      author_email='blakethomasmiller@gmail.com',
      license='GNU GPL v2.0',
      packages=['relay2slack'],
      install_requires=['requests', 'Flask'],
      scripts=['bin/relay2slack'],
      zip_safe=False)
