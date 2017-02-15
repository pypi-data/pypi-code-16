from setuptools import setup, find_packages

setup(name='gqrxHamlib',
      version = '2.0',
      description = 'gqrx-Hamlib interface',
      url='http://github.com/g0fcu/gqrx-hamlib',
      author='Simon Kennedy',
      license='GPL',
      packages=find_packages(),
      #install_requires=['PyQt4'],
      entry_points={
          'console_scripts': [
               'gqrxHamlib=gqrxHamlib.gqrxHamlib:main'
                  ]
                }
)
