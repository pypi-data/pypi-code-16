import codecs
import setuptools
import sys


long_description = codecs.open('README.rst', "r").read()

# Conditional load of enumeration
# See https://hynek.me/articles/conditional-python-dependencies/

INSTALL_REQUIRES = [
    "Django >= 1.7",
    "google-api-python-client >= 1.5.1",
    "python-dateutil >= 2.5.3",
    "requests >= 2.10.0",
    "django-appconf >= 1.0.2",
    "oauth2client >= 2.2.0",
    "six >= 1.10.0"
    ""
]

EXTRAS_REQUIRE = dict()

if int(setuptools.__version__.split(".", 1)[0]) < 18:
    if sys.version_info[0:2] < (3, 4):
        INSTALL_REQUIRES.append("enum34 >= 1.1.6")
else:
    EXTRAS_REQUIRE[":python_version<'3.4'"] = ["enum34 >= 1.1.6"]

__version__ = '0.0.0'
exec([line for line in open('googledriveapi/__init__.py','r').readlines()
      if line.startswith('__version__')][-1])

setuptools.setup(
    name="django-googledrive-api",
    version=__version__,
    author="Chaiwat Suttipongsakul",
    author_email="cwt@bashell.com",
    description=("Django integration with Google Drive API"),
    license="LICENSE.txt",
    keywords="django google drive api googledrive",
    url="https://bitbucket.org/bashell-com/django-googledrive-api",
    download_url="https://bitbucket.org/bashell-com/django-googledrive-api/get/%s.zip" % __version__,
    packages=setuptools.find_packages(exclude=["django_googledrive_api", "googledriveapi.tests", "docs"]),
    long_description=long_description,
    package_data={
        '': ['README.rst'],
    },
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Django",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6"
    ],
)
