from setuptools import setup, find_packages
setup(
    name="papitools",
    version="0.1",
    packages=find_packages(),
    scripts=['papitools.py', 'CustomPAPIActions.py'],

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    #install_requires=['json>=2.0.9'],

    package_data={
        # If any package contains *.txt or *.rst files, include them:
        #'': ['*.txt', '*.rst'],
        # And include any *.msg files found in the 'hello' package, too:
        #'hello': ['*.msg'],
    },

    # metadata for upload to PyPI
    author="Vreddhi",
    author_email="vreddhi.bhat@gmail.com",
    description="This package is to a wrapper to PAPI framework at akamai",
    license="PSF",
    keywords="PAPI akamai Property Manager",
    url="https://github.com/vreddhi/PAPIWrapper",   # project home page, if any

    # could also include long_description, download_url, classifiers, etc.
)
