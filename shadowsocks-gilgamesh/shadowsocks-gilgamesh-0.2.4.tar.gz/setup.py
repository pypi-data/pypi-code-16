

from setuptools import setup, find_packages


setup(name='shadowsocks-gilgamesh',
    version='0.2.4',
    description='a simple way to use mongo db, let db like dict',
    url='https://github.com/Qingluan/.git',
    author='Qingluan',
    author_email='darkhackdevil@gmail.com',
    license='MIT',
    zip_safe=False,
    packages=find_packages(),
    install_requires=['termcolor'],
    entry_points={
        'console_scripts': ['gilgamesh=Gill.cmd:main']
    },

)


