"""Set up script"""
import codecs
from setuptools import setup
import pypandoc


def _create_long_desc():
    """Create long description and README formatted with rst."""
    _long_desc = ''
    with codecs.open('README.rst', 'w', 'utf-8') as rf:
        try:
            _long_desc = pypandoc.convert('README.md', 'rst')
        except OSError as e:
            import os
            if not 'TRAVIS' in os.environ:
                raise OSError(e)
            else:
                return ''
        rf.write(_long_desc)
    return _long_desc
long_desc = _create_long_desc()

# Setup
setup(name='cronquot',
      version='0.1.0',
      description='Cron scheduler.',
      long_description=long_desc,
      classifiers=[
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'License :: OSI Approved :: MIT License',
          'Topic :: Software Development :: Libraries :: Python Modules'
          ],
      keywords='cron crontab schedule',
      author='Shohei Mukai',
      author_email='mukaishohei76@gmail.com',
      url='https://github.com/pyohei/cronquot',
      license='MIT',
      packages=['cronquot'],
      entry_points={
          'console_scripts': [
              'cronquot = cronquot.cronquot:execute_from_console'],
          },
      install_requires=['crontab'],
      test_suite='test' 
      )
