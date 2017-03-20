#coding=utf-8

from setuptools import setup, find_packages

setup(
    name = 'mypypilxp',
    version = '1.0.3',
    discription = 'A pypi demo',
    long_discription = 'Really a pypi demo',
    author = 'dragonflylxp',
    author_email = 'dragonflylxp@gmail.com',

    #项目地址
    url = 'https://dragonflylxp.github.io/python-package',

    #开源许可
    license = 'MIT',

    #项目分类: https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        #项目状态
        'Development Status :: 3 - Alpha',
        
        #受众
        'Intended Audience :: Developers',
        
        #开源许可
        'License :: OSI Approved :: MIT License',

        #支持python版本
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
    ],

    #关键字
    keyword = 'pypi easy_install pip',
    
    #指定或搜搜项目代码   
    packages = find_packages(exclude=['docs','tests']),

    #指定依赖包
    install_requires = ['ujson'],

    #指定其他依赖
    extras_require = {},

    #指定依赖数据
    package_data = {},
    data_file = [],
    
    #产生可以运行脚本
    entry_points = {
        'console_scripts': ['pypidemo=mypypi:main'],
    }
)
