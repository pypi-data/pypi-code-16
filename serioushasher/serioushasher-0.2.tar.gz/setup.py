from setuptools import setup

setup(
    name='serioushasher',
    version='0.2',
    py_modules=['serioushasher'],
    author = 'Jun Zheng',
    description = 'A powerful hashing tool for back-end developers',
    author_email = 'me@jackzh.com',
    url = 'https://github.com/junthehacker/serious_hasher',
    download_url = 'https://github.com/junthehacker/serious_hasher/releases/tag/v0.2',
    keywords = ['python','command-line','tool','back-end','hash','security'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        serioushasher=serioushasher:hash
    ''',
)