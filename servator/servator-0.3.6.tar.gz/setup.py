from setuptools import setup

setup(
    name='servator',
    version='0.3.6',
    author='Raman Barkholenka',
    author_email='raman.barkholenka@gmail.com',
    keyword=['servator'],
    py_modules=['servator'],
    install_requires=[
        'click',
        'requests',
    ],
    entry_points='''
        [console_scripts]
        servator=servator:cli
    '''
)
