from setuptools import setup, find_packages

setup(
    name='fiboseqcli',
    version='0.1.2',
    packages=find_packages(),
    include_package_data=True,
    py_modules=['fibocli'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        fibocli=fibocli:cli
    ''',
    author="Jose Torres",
    author_email="torres@balameb.com",
    description="Sample Fibonacci sequence tool.",
    license="MIT",
    keywords="fibonacci example examples",
    url="http://balameb.primate.tech/python/2017/03/15/distributing-python-packages.html",
)
