# encoding: UTF-8
from setuptools import setup
"""
打包的用的setup必须引入
"""

VERSION = '2.6.3'

setup(
    name='gopage',  # 文件名
    version=VERSION,  # 版本(每次更新上传Pypi需要修改)
    description="use cache for parser and crawler",
    classifiers=[],
    keywords='python google crawler',  # 关键字
    author='xgeric',  # 用户名
    author_email='guxt1994@gmail.com',  # 邮箱
    url='https://xgeric.github.io',  # github上的地址,别的地址也可以
    license='MIT',  # 遵循的协议
    packages=['gopage'],  # 发布的包名
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        'bs4',
        'requests'
    ],  # 满足的依赖
)
