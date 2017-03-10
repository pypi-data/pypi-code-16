from distutils.core import setup

NAME = 'baseZhang'
VERSION = '0.1.3c'
DOWNLOAD = "https://github.com/zhangxulong/baseZhang/archive/baseZhang-0.1.1.tar.gz"
DESCRIPTION = "Own base util code"
# 'baseCodes', 'demo', 'getMFCC'
setup(
    py_modules=['basecodes'],
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author="ZHANG Xu-long",
    author_email="fudan0027zxl@gmail.com",
    license="BSD",
    url="http://zhangxulong.site",
    download_url=DOWNLOAD,

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
