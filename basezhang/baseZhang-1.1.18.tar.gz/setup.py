from distutils.core import setup

NAME = 'baseZhang'
_MAJOR = 1
_MINOR = 1
_MICRO = 18
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
    install_requires=['numpy==1.12.1', 'pandas==0.19.2', 'matplotlib==2.0.0', 'h5py==2.7.0', 'tqdm==4.11.2',
                      'PyAudio==0.2.11', 'pydub==0.18.0', 'pyPdf==1.13', 'PyYAML==3.12', 'six==1.10.0',
                      'SoundFile==0.9.0.post1', 'Theano==0.9.0', 'scikit-learn==0.18.1', 'Keras==1.2.2'],
    zip_safe=False,
)
