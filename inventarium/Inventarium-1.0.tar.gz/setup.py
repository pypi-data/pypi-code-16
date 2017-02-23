from setuptools import setup

setup(
    name='Inventarium',
    version='1.0',
    py_modules=['inventarium'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        inventarium=inventarium:menu
    '''
)
