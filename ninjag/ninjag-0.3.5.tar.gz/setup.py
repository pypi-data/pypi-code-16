from codecs import open as codecs_open
from setuptools import setup, find_packages


# Get the long description from the relevant file
with codecs_open('README.md', encoding='utf-8') as f:
    long_description = f.read()


setup(name='ninjag',
      version='0.3.5',
      description=u"Ninja config file generator",
      long_description=long_description,
      keywords='',
      author=u"Steven(Yuhang) Wang",
      url='https://github.com/yuhangwang/ninjag-python',
      license='MIT',
      packages=find_packages(exclude=['test']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'PyYAML',
          'typing'
      ],
      extras_require={
          'test': ['pytest'],
      },
      entry_points={
          'console_scripts': [
                  'ninjag = ninjag.cli:cli'
              ],
      },
      package_data={'':['usage.txt']},
      )
