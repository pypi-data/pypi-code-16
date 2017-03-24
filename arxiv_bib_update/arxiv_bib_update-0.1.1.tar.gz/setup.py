from setuptools import setup
from glob import glob

def find_version(path):
    import re
    # path shall be a plain ascii text file.
    s = open(path, 'rt').read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              s, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Version not found")

setup(name="arxiv_bib_update", 
      version=find_version("arxiv_bib_update.py"),
      author="Nick Hand",
      maintainer="Nick hand",
      maintainer_email="nicholas.adam.hand@gmail.com",
      description="tool to search for and update out-of-date arXiv preprints in bibtex files",
      url="http://github.com/nickhand/arxiv_bib_update",
      install_requires=['bibtexparser', 'ads'],
      py_modules=['arxiv_bib_update'],
      entry_points={'console_scripts': ['arxiv_bib_update = arxiv_bib_update:main']},
)

