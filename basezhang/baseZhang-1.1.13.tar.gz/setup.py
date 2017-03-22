from distutils.core import setup

NAME = 'baseZhang'
_MAJOR = 1
_MINOR = 1
_MICRO = 13
VERSION = '%d.%d.%d' % (_MAJOR, _MINOR, _MICRO)
DOWNLOAD = "https://github.com/zhangxulong/baseZhang/dist/baseZhang-" + VERSION + ".tar.gz"
DESCRIPTION = "My own base util code"
setup(
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
    install_requires=['numpy',  'matplotlib', 'h5py', 'tqdm', 'pydub', 'scikit-learn'],
    zip_safe=False,
)
