# -*- coding: UTF-8 -*-
#!/usr/bin/env python
from setuptools import setup

setup(
    name='yixinPyLib',
    version='0.0.39',
    description='易鑫金融测试用例公共库',
    url='http://192.168.145.20:8088/testsite',
    author='Zhouxs',
    author_email='zhouxs@yixincapital.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='public library test case python',
    packages=['yixinPyLib','yixinPyLib.demo','yixinPyLib.testcaseupload','yixinPyLib.Library','yixinPyLib.LocalMethod'],
)