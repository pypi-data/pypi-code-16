from setuptools import setup

setup(name='etherwatch',
      packages=['etherwatch'],
      version='0.1.4',
      description='Notifies you about ether prices.',
      author = 'Ryan Culligan',
      author_email='rrculligan@gmail.com',
      license='MIT',
      install_requires=[
        'coinbase',
        'twilio',
        'slackclient',
      ],
      url='http://github.com/theculliganman/ether_watch',
      download_url='https://codeload.github.com/TheCulliganMan/ether_watch/archive/master.tar.gz',
      keywords = ['ether', 'ethereum', 'coinbase'],
      classifiers = [],
)
