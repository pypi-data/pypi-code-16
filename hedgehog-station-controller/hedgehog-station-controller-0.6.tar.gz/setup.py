import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='hedgehog-station-controller',
    version='0.6',
    packages=find_packages(),
    include_package_data=True,
    license='Apache 2.0 License',  # example license
    description='A VISA Web interface.',
    long_description=README,
    url='https://www.example.com/',
    author='lordoftheflies',
    author_email='laszlo.hegedus@cherubits.hu',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.10',  # replace "X.Y" as appropriate
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',  # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        # Replace these appropriately if you are stuck on Python 2.
        'Programming Language :: Python :: 2.7',
        # 'Programming Language :: Python :: 3.4',
        # 'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Database',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: System :: Monitoring',
        'Development Status :: 2 - Pre-Alpha'
    ],
    install_requires=[
        'django',
        'cronlikescheduler',
        'pyyaml',
        'pyusb',
        'pyserial',
        'pyvisa',
        'pyvisa-py',
        'pyvisa-sim',
        'pika',
        'jinja2',
        'numpy',
        'scipy',
        'matplotlib',
        'mpld3'
    ],
    entry_points = {
        'console_scripts': [
            'hedgehog-ingestion=dataingestion.main:main',
            'hedgehog-cli=cli.main:main'
        ]
    }
)