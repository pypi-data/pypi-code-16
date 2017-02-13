from distutils.core import setup
setup(
    name='wxyAlice',
    packages=['wxyAlice'],
    version='0.0.16',
    description='micro service on falcon',
    author='wangxiaoyu',
    author_email='wangxiaoyu.wangxiaoyu@gmail.com',
    license='MIT',
    install_requires=[
        'gevent',
        'falcon',
        'requests'
    ],
    url='https://github.com/netsmallfish1977/wxyAlice',
    download_url='https://github.com/netsmallfish1977/wxyAlice/tarball/0.0.16',
    keywords=['wxy', 'Alice', 'falcon', 'micro_service'],
    classifiers=[],
)
