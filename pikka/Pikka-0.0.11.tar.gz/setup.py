from distutils.core import setup

setup(
    name = 'Pikka',
    packages = ['Pikka', 'Pikka.core', 'Pikka.actor', 'Pikka.action', 'Pikka.thread'],
    scripts = [],
    version = '0.0.11',
    description = 'Project implements network pattern to like Akka base on Pyro',
    author = 'mmmaaaxxx77',
    author_email = 'mmmaaaxxx77@gmail.com',
    url = 'https://github.com/mmmaaaxxx77/Pikka',
    download_url = 'https://github.com/mmmaaaxxx77/Pikka/archive/master.zip',
    keywords = ['Pikka', 'Pyro'],
    classifiers = [],
)