from setuptools import setup

setup(
    name="espada",
    version='2.0',
    description='C++ Project and Class Generator',
    url='https://bitbucket.org/cajun_code/espada.py',
    author='Allan Davis',
    author_email='cajun.code@gmail.com',
    license='MIT',
    packages=['espada'],
    install_requires=[
        'Click',
        'Jinja2',
        'inflection',
    ],
    entry_points='''
        [console_scripts]
        espada=espada:cli
    ''',
    zip_safe=False
)
