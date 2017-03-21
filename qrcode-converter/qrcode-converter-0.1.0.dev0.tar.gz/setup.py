"""
`````````````````
Run it:

.. code:: bash

    $ pip install qrcode-converter
    $ python app/run.py [inner_img_path] [content] [width] [height]
Links
`````

* `website <https://github.com/jackqt/py-qrcode-generator/>`_
* `documentation <https://github.com/jackqt/py-qrcode-generator/>`_

"""
import re
import ast
from setuptools import setup


_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('app/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

setup(
    name='qrcode-converter',
    version=version,
    url='https://github.com/jackqt/py-qrcode-generator/',
    license='MIT',
    author='Jack Li',
    author_email='jack.qingtian@gmail.com',
    description='A qrcode generator with inner image',
    long_description=__doc__,
    packages=['app'],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Pillow>=4.0.0',
        'qrcode>=5.3'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
