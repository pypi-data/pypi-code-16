from distutils.core import setup

PACKAGE = "/"
NAME = "baseZhang"
DESCRIPTION = "own base code"
AUTHOR = "ZHANG Xu-long"
AUTHOR_EMAIL = "fudan0027zxl@gmail.com"
URL = "http://zhangxulong.site"
VERSION = '0.1.1a'

setup(
    py_modules=['baseCodes', 'demo'],
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="BSD",
    url=URL,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Framework :: Django",
    ],
    zip_safe=False,
)
