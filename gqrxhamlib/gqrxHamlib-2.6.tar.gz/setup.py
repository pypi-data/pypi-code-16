from setuptools import setup, find_packages

setup(name='gqrxHamlib',
      version = '2.6',
      description = 'gqrx-Hamlib interface',
      url='http://github.com/g0fcu/gqrx-hamlib-gui',
      author='Simon Kennedy',
      license='GPL',
      packages=find_packages(),
      #install_requires=['xmlrpclib'],
      entry_points={
          'console_scripts': [
               'gqrxHamlib=gqrxHamlib:main'
                  ]
                }
)
