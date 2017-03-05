from setuptools import setup, find_packages

setup(
        name='pyalsi',
        version='0.3',
        packages=find_packages(),
        install_requires=['psutil', 'click', 'py-cpuinfo'],
        license='GPL2',
        author='chestm007',
        author_email='chestm007@hotmail.com',
        description='python rewrite of alsi (Arch Linux System Information)',
        entry_points="""
            [console_scripts]
            pyalsi=pyalsi.__init__:main
        """,
)
