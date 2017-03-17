import os
from setuptools import setup
from setuptools import find_packages

version = "0.1.0"

setup(
    name='glossary',
    version=version,
    author='dissw-team',
    author_email='lab.dissw@gmail.com',
    maintainer='Dmitry Shlagov',
    maintainer_email='wessmoke@gmail.com',
    description='Glossary with common Ionosphere data',
    long_description=open(
        os.path.join(os.path.dirname(__file__), 'README.md')
    ).read(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: Russian',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5'
    ],
    license='MIT',
    packages=find_packages(include=["glossary", "glossary.*"]),
    include_package_data=True,
    install_requires=[
        "setuptools",
        "Django>=1.10.6,<1.11",
        "requests"
    ],
    zip_safe=False,
)
