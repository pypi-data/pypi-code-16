from setuptools import setup
import fastentrypoints

with open('README.md') as f:
    long_description = f.read()

VERSION = "0.2"

"""
  entry_points = {
      'console_scripts': [
          'xaal-isalive = xaal.tools.isalive:run',
          'xaal-info   = xaal.tools.info:run',
          'xaal-dumper  = xaal.tools.dumper:run',
          'xaal-tail    = xaal.tools.tail:run',
          'xaal-walker  = xaal.tools.walker:run',
          'xaal-keygen  = xaal.tools.keygen:run',
      ],
    },
   
""" 


setup(
    name='bugone',
    version=VERSION,
    license='GPL License',
    author='Jerome Kerdreux',
    author_email='Jerome.Kerdreux@Finix.eu.org',
    url='https://github.com/jkx/bugone-python',
    description=('API to send/receive bugOne messages througt serial port or tcp mux'),
    long_description=long_description,
    classifiers=[
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords=['RFM12', 'bugOne','Wireless','Home-Automation'],
    platforms='any',
    packages=['bugone',],
    include_package_data=True,
    install_requires=['pyserial'],
    entry_points = {
      'console_scripts': [
          'bugone-dumper = bugone.dumper:main',
      ],
    },

    
)
