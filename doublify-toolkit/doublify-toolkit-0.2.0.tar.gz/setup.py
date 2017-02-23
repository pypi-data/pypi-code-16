from setuptools import find_packages, setup

DEPENDENCIES = (
    'antlr4-python3-runtime>=4.6',
    'PyJWT>1.4', )

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='doublify-toolkit',
    version='0.2.0',
    author='Doublify APIs',
    author_email='opensource@doublify.io',
    description='Doublify API toolkit for Python',
    long_description=long_description,
    url='https://github.com/doublifyapis/toolkit-python',
    packages=find_packages(),
    namespace_packages=('doublify', ),
    install_requires=DEPENDENCIES,
    license='MIT',
    keywords='doublify toolkit',
    classifiers=(
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development',
        'Topic :: Text Processing :: Filters', ), )
