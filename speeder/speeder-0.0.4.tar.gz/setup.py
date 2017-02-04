import os
import re
import codecs
from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))


def find_version(*file_paths):
    try:
        f = codecs.open(os.path.join(here, *file_paths), 'r', 'latin1')
        version_file = f.read()
        f.close()
    except:
        raise RuntimeError("Unable to find version string.")

    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


try:
    f = codecs.open('README.rst', encoding='utf-8')
    long_description = f.read()
    f.close()
except:
    long_description = ''


setup(
    name='speeder',
    version=find_version('net.py'),
    description='Debian Net Speeder ',
    long_description=long_description,
    keywords='Debain, Internet speed',
    author='Gaurav Kumar Verma',
    author_email='gkverma1094@gmail.com',
    url='https://github.com/gkdeveloper/speeder',
    license='GNU',
    install_requires=["psutil==4.3.0","netifaces==0.10.4"],
    py_modules=["net"],
    entry_points={
        'console_scripts': [
            'speeder=net:main'
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'Environment :: Console',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',

    ]
)
