from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, "README.md")) as f:
    long_description = f.read()

setup(
    name="paginate_whoosh",
    version="0.2",
    description="Extension to the paginate module to support Whoosh",
    long_description=long_description,
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="pagination paginate whoosh",
    author="Lukas Weissenböck",
    author_email="lukas@lukes.space",
    install_requires=[
        "whoosh",
        "paginate>=0.4",
    ],
    url="https://github.com/myriogon/paginate_whoosh",
    license="MIT",
    zip_safe=False,
    packages=find_packages()
)