"""
groundwork utilities
====================
"""
from setuptools import setup, find_packages
import re
import ast

_version_re = re.compile(r'__version__\s+=\s+(.*)')
with open('groundwork_utilities/version.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

setup(
    name='groundwork-utilities',
    version=version,
    url='http://groundwork-utilities.readthedocs.org',
    license='MIT license',
    author='team useblocks',
    author_email='info@useblocks.com',
    description="Provides groundwork plugins to monitor and validate applications during runtime.",
    long_description=__doc__,
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    platforms='any',
    install_requires=['groundwork', 'groundwork-web', 'psutil', 'groundwork-database'],
    tests_require=['pytest', 'pytest-flake8'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    entry_points={
        'groundwork.plugin': ["gw_resource_monitor = "
                              "groundwork_utilities.plugins.GwResourceMonitor.gw_resource_monitor:GwResourceMonitor",
                              "gw_resource_monitor_Web = "
                              "groundwork_utilities.plugins.GwResourceMonitorWeb.gw_resource_monitor_web"
                              ":GwResourceMonitorWeb",
                              "gw_db_validator = "
                              "groundwork_utilities.plugins.GwDbValidator.gw_db_validator"
                              ":GwDbValidator",
                              ],
    }
)
