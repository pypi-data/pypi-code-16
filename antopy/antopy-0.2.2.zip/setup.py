from distutils.core import setup
setup(
    name = 'antopy',
    packages = ['antopy'],
    install_requires=[
          'paho-mqtt',
    ],
    version = '0.2.2',
    description = 'Python Library for using anto.',
    author = 'Isara Naranirattisai',
    author_email = 'isaradream@gmail.com',
    keywords = ['anto'],
    classifiers = [
      'Topic :: Education',
      'Topic :: Utilities'
      ],
)
