from setuptools import setup, find_packages

setup(
    name='bdtranslate',
    version='1.0.0',
    keywords = ('baidu', 'translate'),
    description='baidu translate service python api',
    license='Free',
    author='rust.ch3n',
    author_email='rust.ch3n@gmail.com',
    url='http://ch3n.co',
    platforms = 'any',
    packages = find_packages('./'),
    package_dir = {'':'./'}
)