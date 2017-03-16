from distutils.core import setup

NAME = 'zhangxulong'
VERSION = '0.0.1a'
DOWNLOAD = "https://github.com/zhangxulong/baseZhang/archive/baseZhang-" + VERSION + ".tar.gz"
DESCRIPTION = "My own codes"
setup(
    py_modules=['zhangxulong'],
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description="""A python module for personal.""",
    author="ZHANG Xu-long",
    author_email="fudan0027zxl@gmail.com",
    license="BSD",
    url="http://zhangxulong.site",
    download_url=DOWNLOAD,
    keywords='personal',
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",

    ],
    zip_safe=False,
)
