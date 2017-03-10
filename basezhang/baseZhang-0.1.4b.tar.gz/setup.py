from distutils.core import setup

NAME = 'baseZhang'
VERSION = '0.1.4b'
DOWNLOAD = "https://github.com/zhangxulong/baseZhang/archive/baseZhang-0.1.1.tar.gz"
DESCRIPTION = "Own base util code"
setup(
    py_modules=['baseCodes', 'demo', 'getMFCC'],
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description="""A python module for audio and music processing.""",
    author="ZHANG Xu-long",
    author_email="fudan0027zxl@gmail.com",
    license="BSD",
    url="http://zhangxulong.site",
    download_url=DOWNLOAD,
    keywords='audio music sound',
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",

    ],
    zip_safe=False,
)
