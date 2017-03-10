import os
from setuptools import setup

def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    try:
        return open(file_path).read()
    except IOError as ex:
        print("Error '{}' for file {}".format(ex, file_path))
        raise ex

setup (
    name = "analyze_site",
    version = "0.1.2",
    author = "Tim Lee",
    author_email = "timhl81@gmail.com",
    description = "Utility to crawl web site looking for key words",
    license = "Apache 2.0",
    keywords = ["web","crawl","analyze"],
    url = "https://github.com/OV105/site-analyzer",
    long_description = read("README.md"),
    classifiers = [
        "Topic :: Utilities",
        "License :: OSI Approved :: Apache Software License",
        "Development Status :: 4 - Beta"
    ],
    py_modules = ["analyze_site"],
    install_requires = [ "nltk", "html", "urllib ", "operator "]
)
