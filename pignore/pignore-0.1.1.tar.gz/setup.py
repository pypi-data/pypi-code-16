from distutils.core import setup

setup(
    name = 'pignore',
    packages = ['pignore'],
    version = '0.1.1',
    description = 'Gitignore generator written in Python',
    author = 'Jake Shelley',
    author_email = 'jakeshelley1@gmail.com',
    url = 'https://github.com/JakeShelley1/pignore',
    download_url = 'https://github.com/JakeShelley1/pignore/tarball/0.1',
    keywords = ['gitignore', 'generator'],
    entry_points='''
        [console_scripts]
        pignore=pignore:main
    ''',
    classifiers = [],
)
