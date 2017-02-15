from distutils.core import setup
from setuptools import find_packages

setup(
    name='x509',
    version='0.1',
    packages=find_packages(),
    url='https://github.com/cniemira/py3x509',
    maintainer='cniemira',
    maintainer_email='siege@siege.org',
    license=open('LICENSE.txt').read(),
    description='Parse x509v3 certificates and PKCS7 signatures',
    long_description=open('README.rst').read(),
    install_requires=[
            "pyasn1 >= 0.1.7",
    ],
    entry_points={
        'console_scripts': [
            'x509_parse.py = x509.commands:print_certificate_info_cmd',
            'pkcs7_parse.py = x509.commands:print_signature_info_cmd',
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Security :: Cryptography",
        "Topic :: Software Development :: Libraries",
    ],
    test_suite='x509.test',
    zip_safe=False,
)
