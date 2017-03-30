from setuptools import setup
from os import path


setup(

    name='pyspeakrec',

    version='0.1.0',

    description='A Speaker Recognition tool in Python',

    url='https://github.com/AKBoles/pyspeakrec',

    author='Andrew Boles',

    author_email='andrew.boles@my.utsa.edu',

    license='MIT',

    packages=['pyspeakrec'],

    install_requires=['tflearn','librosa','pydub','pyaudio'],

    keywords='speaker recognition, machine learning',

    classifiers=[
        'Development Status :: 3 - Alpha',

        'Programming Language :: Python :: 2.7'
    ],
    zip_safe=False
)
