import re
import setuptools


setuptools.setup(
    name="listpad",
    version=re.search(r"__version__ *= *'([0-9]+\.[0-9]+\.[0-9]+)' *\n",
                      open("listpad/__init__.py").read()).group(1),
    description="Pad nested lists.",
    long_description=open("README.md").read(),
    license="Public Domain",
    author="Yota Toyama",
    author_email="raviqqe@gmail.com",
    url="https://github.com/raviqqe/listpad/",
    packages=["listpad"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: Public Domain",
        "Programming Language :: Python :: 3.5",
        "Topic :: Utilities",
    ],
)
