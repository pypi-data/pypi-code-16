import os
import setuptools
import sys

from yaz_zichtgithub_plugin.version import version

if sys.argv[-1] == "tag":
    os.system("git tag -a {} -m \"Release {}\"".format(version, version))
    os.system("git push origin {}".format(version))
    sys.exit()

if sys.argv[-1] == "publish":
    os.system("python3 setup.py sdist upload")
    os.system("python3 setup.py bdist_wheel upload")
    print("You probably want to also tag the version now")
    sys.exit()

setuptools.setup(
    name="yaz_zichtgithub_plugin",
    packages=["yaz_zichtgithub_plugin"],
    version=version,
    description="A github plugin for YAZ",
    author="Boudewijn Schoon",
    author_email="boudewijn@zicht.nl",
    url="http://github.com/boudewijn-zicht/yaz_zichtgithub_plugin",
    license="MIT",
    zip_safe=False,
    install_requires=[
        "yaz",
        "pygithub",
        # spreadsheet requirements
        "gspread",
        "oauth2client",
    ],
    scripts=["bin/yaz-zicht-dependency-matrix"],
    test_suite="nose.collector",
    tests_require=["nose", "coverage"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6"
    ])
