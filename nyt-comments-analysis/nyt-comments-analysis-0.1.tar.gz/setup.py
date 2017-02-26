from setuptools import setup
from setuptools import find_packages

setup(name='nyt-comments-analysis',
      version='0.1',
      description='A project written in Python to perform a sentiment analysis of the user comments made on nytimes.com using the Stanford CoreNLP.',
      url='https://github.com/julianla/nyt-user-sentiment-analysis',
      find_packages=find_packages(),
      author='julianla',
      packages=['nyt'],
      license='MIT')