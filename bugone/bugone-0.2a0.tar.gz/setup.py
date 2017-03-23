from setuptools import setup
import fastentrypoints

with open('README.md') as f:
    long_description = f.read()

VERSION = "0.2a"


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
