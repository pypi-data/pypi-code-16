from distutils.core import setup

setup(
    name='media-transporter',
    version='0.1.1',
    author='Steve Coward',
    author_email='steve.coward@gmail.com',
    url='https://github.com/stevecoward/transporter',
    license='LICENSE.txt',
    description='Manages the transportation of TV/Movie files to a mountable media share.',
    long_description=open('README.txt').read(),
    scripts=['bin/media-transporter'],
    packages=['media_transporter', 'media_transporter.classes'],
)
