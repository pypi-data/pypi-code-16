from setuptools import setup, find_packages

version = "0.3.1"

setup(
    name='flashboard',
    version=version,
    packages=find_packages(exclude=['test_app']),
    author='Gary Reynolds',
    author_email='gary@touch.asn.au',
    description='',
    url='https://bitbucket.org/fixja/flashboard',
    install_requires=[
        'vitriolic[competition]',
    ],
    include_package_data=True,
    zip_safe=False,
)
