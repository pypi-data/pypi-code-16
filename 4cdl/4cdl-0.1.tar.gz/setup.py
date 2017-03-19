import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages
setup(
    name="4cdl",
    version="0.1",
    packages=find_packages(),
    scripts=['4cdl.py'],

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires=[],

    package_data={
    },

    # metadata for upload to PyPI
    author="AnhLam",
    author_email="tuananhlam@gmail.com",
    description="Lightweight 4chan downloader",
    license="Free4All",
    keywords="4chan downloader image board",
    url="https://github.com/tuananhlam/4cdl",   # project home page, if any

    # could also include long_description, download_url, classifiers, etc.
)