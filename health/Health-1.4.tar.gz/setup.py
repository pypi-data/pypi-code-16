from distutils.core import setup

setup(
    name='Health',
    version='1.4',
    author='Sean Wade',
    author_email='seanwademail@gmail.com',
    packages=['health'],
    license='Apache-2.0',
    description='Healthcare research tools',
    package_data={
        'health': ['data/*.p'],
        },
    include_package_data=True,
    install_requires=[
        "gensim",
    ],
)
