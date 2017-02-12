from setuptools import setup

setup(
    name='FejsaFlaskProject',
    version='1.0',
    author='Vladimir Fejsov',
    author_email='vlada@way2cu.com',
    packages=['app', 'app.module_one'],
    include_package_data=True,
    install_requires=['flask',],
)