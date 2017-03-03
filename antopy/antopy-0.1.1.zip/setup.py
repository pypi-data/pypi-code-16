from distutils.core import setup
setup(
    name = 'antopy',
    packages = ['antopy'],
    install_requires=[
          'paho-mqtt',
    ],
    version = '0.1.1',
    description = 'Python Library for using anto.',
    author = 'Isara Naranirattisai',
    author_email = 'isaradream@gmail.com',
    url = 'https://github.com/DreamN/AntoPY',
    download_url = 'https://github.com/DreamN/AntoPY/archive/0.1.0.tar.gz',
    keywords = ['anto'],
    classifiers = [
      'Topic :: Education',
      'Topic :: Utilities'
      ],
)
