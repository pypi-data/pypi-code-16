from setuptools import setup

setup(name='demographer_popgen',
      version='0.0.0.dev5',
      description='DemoGrapher: Software for graphically studying population histories.',
      url='https://github.com/ejewett/demographer',
      author='Ethan Jewett',
      author_email='ejewett@gmail.com',
      license='GPL3.0',
      packages=['demographer_popgen'],
      install_requires=['division','mpmath','numpy','scipy','matplotlib','ast','json','pillow'],
      classifiers=['Development Status :: 3 - Alpha','Intended Audience :: End Users/Desktop','License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)','Programming Language :: Python :: 2.7','Topic :: Scientific/Engineering :: Bio-Informatics',],
      zip_safe=False)