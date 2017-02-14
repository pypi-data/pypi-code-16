from setuptools import setup, find_packages
setup(
    name="papitools",
    version="0.10",
    packages=find_packages(),
    namespace_packages=['papitools'],

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine

    # metadata for upload to PyPI

    author="Vreddhi",
    author_email="vreddhi.bhat@gmail.com",
    description="This package is to a wrapper to PAPI framework at akamai",
    license="MIT",
    keywords="PAPI akamai Property Manager",
    url="https://github.com/vreddhi/PAPITools",   # project home page, if any

    # could also include long_description, download_url, classifiers, etc.
)
