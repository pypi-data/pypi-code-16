from distutils.core import setup
VERSION = '0.1.2a'

setup(
    py_modules=['baseCodes', 'demo'],
    data_files=['README.md','requirements.txt','readme'],
    name="baseZhang",
    version=VERSION,
    description="own base code",
    author="ZHANG Xu-long",
    author_email="fudan0027zxl@gmail.com",
    license="BSD",
    url="http://zhangxulong.site",
    download_url="https://github.com/zhangxulong/baseZhang/archive/baseZhang-0.1.1.tar.gz",

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
