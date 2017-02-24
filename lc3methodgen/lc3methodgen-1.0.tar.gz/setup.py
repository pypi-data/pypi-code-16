from setuptools import setup

setup(name='lc3methodgen',
      version='1.0',
      description='LC3 Method Generator',
      url='http://github.com/skyman/lc3methodgen',
      author='Cem Gokmen',
      author_email='cgokmen@gatech.edu',
      license='MIT',
      packages=['lc3methodgen'],
      install_requires=[
          'docopt',
      ],
      scripts=['bin/lc3methodgen'],
      zip_safe=False)
