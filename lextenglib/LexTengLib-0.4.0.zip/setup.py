import codecs
import os
import sys

# 引入打包用的setup
try:
    from setuptools import setup
except:
    from distutils.core import setup
 

def read(fname):

    """

    定义一个read方法，用来读取目录下的长描述

    我们一般是将README文件中的内容读取出来作为长描述，这个会在PyPI中你这个包的页面上展现出来，

    你也可以不用这个方法，自己手动写内容即可，

    PyPI上支持.rst格式的文件。暂不支持.md格式的文件，<BR>
	.rst文件PyPI会自动把它转为HTML形式显示在你包的信息页面上。

    """

    return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()

# 安装包名 
NAME = "LexTengLib"

# 包含的包
PACKAGES = ["LexTengLib",]

# 包描述（简介）
DESCRIPTION = "this is a test package for packing python liberaries tutorial."
 
# 包说明（长描述）
LONG_DESCRIPTION = read("README.txt")
 
# 关键字，方便PyPI进行分类
KEYWORDS = "test python package"

# 包作者
AUTHOR = "LexTeng"

# 作者邮箱
AUTHOR_EMAIL = "lexteng@163.com"
 
# 包的项目地址
URL = "http://lexteng.cn"

# 版本
VERSION = "0.4.0"

# 授权方式
LICENSE = "MIT"

# 安装函数
setup(
    name = NAME,
    version = VERSION,
    description = DESCRIPTION,
    long_description = LONG_DESCRIPTION,

    classifiers = [

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python',

        'Intended Audience :: Developers',

        'Operating System :: OS Independent',

    ],

    keywords = KEYWORDS,
    author = AUTHOR,
    author_email = AUTHOR_EMAIL,
    url = URL,
    license = LICENSE,
    packages = PACKAGES,
    include_package_data=True,
    zip_safe=True,
)
