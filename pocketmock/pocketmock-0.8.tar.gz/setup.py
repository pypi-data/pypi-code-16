from setuptools import setup

setup(
    name='pocketmock',
    version='0.8',
 
    description='A very easy mocking library',

    url='https://www.github.com/byxor/pocketmock',
    
    author='Brandon Ibbotson',
    author_email='brandon.ibbotson2@mail.dcu.ie',

    license='GPLv3',

    packages=["pocketmock"],

    install_requires=['dill']
)
