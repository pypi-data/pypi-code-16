from setuptools import setup, find_packages

setup(
    name='pyalsi',
    version='0.4.2',
    packages=find_packages(),
    install_requires=['psutil', 'click', 'py-cpuinfo'],
    license='GPL2',
    author='chestm007',
    author_email='chestm007@hotmail.com',
    url='https://github.com/chestm007/pyalsi',
    download_url='https://github.com/chestm007/pyalsi/mypackage/archive/0.3.tar.gz',
    description='python rewrite of alsi (Arch Linux System Information) to support multiple systems',
    entry_points="""
        [console_scripts]
        pyalsi=pyalsi.__init__:cli
    """,
    requires=[
        'nose',
        'mock'
    ]
)
