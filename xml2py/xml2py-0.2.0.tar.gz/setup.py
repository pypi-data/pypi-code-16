"""
This package contains classes and functions which convert
an XML object into a dict or DotDict.  The DotDict is
convenient for exploring the XML object interactively with
the Python interpreter.
"""
from distutils.core import setup

long_description = 'xml2py is hosted at https://github.com/pwexler/xml2py'

setup(
        name='xml2py',
        version="0.2.0",
        author='Paul Wexler',
        author_email='paul.e.wexler@gmail.com',
        license='MIT',
        description=__doc__,
        long_description=long_description,
        url='https://github.com/pwexler/xml2py',
        download_url='https://pypi.python.org/pypi/xml2py',
        packages=['xml2py'],
        package_dir={'xml2py': 'xml2py'},
        platforms='Any',
        keywords=('dict', 'DotDict', 'JavaScript', 'dot-notation', 'convert'),
        classifiers=[
                'Intended Audience :: Developers',
                'Operating System :: OS Independent',
                'Programming Language :: Python',
                ],
        )
