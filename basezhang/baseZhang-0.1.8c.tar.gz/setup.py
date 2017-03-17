from distutils.core import setup

NAME = 'baseZhang'
VERSION = '0.1.8c'
DOWNLOAD = "https://github.com/zhangxulong/baseZhang/archive/baseZhang-" + VERSION + ".tar.gz"
DESCRIPTION = "My own base util code"
setup(
    # py_modules=['baseZhang', 'baseZhangRecordAudio', 'baseZhangVideoProcess'],
    packages=['baseZhang'],
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
