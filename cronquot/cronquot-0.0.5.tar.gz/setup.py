import codecs
from setuptools import setup
import pypandoc

long_desc = ''
with codecs.open('README.md', 'r', 'utf-8') as f:
    logn_desc_md = f.read()
    with codecs.open('README.rst', 'w', 'utf-8') as rf:
        print pypandoc.convert('README.md', 'rst')
        rf.write(pypandoc.convert('README.md', 'rst'))

setup(name='cronquot',
      version='0.0.5',
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
