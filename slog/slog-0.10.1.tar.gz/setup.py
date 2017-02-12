from distutils.core import setup

setup(
    name = 'slog',
    packages = ['slog'],
    version = '0.10.1',
    description = 'A simple logger.',
    author = 'Jules Mazur',
    author_email = 'julesmazur@gmail.com',
    url = 'https://github.com/verandaguy/slog',
    download_url = 'https://github.com/verandaguy/slog/releases/tag/v0.10.0',
    keywords = ['logging', 'simple'],
    install_requires = [
            'termcolor'
        ],
    classifiers = []
)

