import glob

from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

long_description = (
    'Read the output of a terminal command like "man" or "ls" and write a PNG.')

term2image_license = 'GNU Lesser General Public License v3 (LGPLv3)'


def font_data():
    for file_path in glob.glob('term2image/fonts/*'):
        yield file_path[len('term2image/'):]


setup(
    name='term2image',
    version='0.3',
    description='Convert terminal command output to an image',
    long_description=long_description,
    url='https://github.com/ajdavis/term2image',
    author='A. Jesse Jiryu Davis',
    author_email='jesse@emptysquare.net',
    license=term2image_license,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'License :: OSI Approved :: ' + term2image_license,
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],

    keywords='terminal image',
    packages=find_packages(),
    package_data={
        'term2image': list(font_data()),
    },
    include_package_data=True,
    install_requires=['pillow'],
    entry_points={
        'console_scripts': [
            'term2image=term2image:main',
        ],
    },
)
