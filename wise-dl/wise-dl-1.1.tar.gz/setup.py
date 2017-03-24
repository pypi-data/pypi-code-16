from setuptools import setup, find_packages

setup(
    name="wise-dl",
    version="1.1",
    # 包含所有src目录下的包
    packages=find_packages(),
    install_requires=[
        'requests>=2.10.0',
        'pycrypto>=2.6.1',
    ],
    entry_points='''
        [console_scripts]
        wise-dl=netease.main:run
    ''',
    author='wise',
    author_email='wisecsj@gmail.com',
    url='http://hfut.oyj.cn',
    description='网易云音乐歌曲下载器',
    keywords=['music', 'netease', 'download', 'command tool'],
)
