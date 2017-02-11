

from setuptools import setup, find_packages


setup(name='mroy-trans',
    version='0.1',
    description='a simple way to use mongo db, let db like dict',
    url='https://github.com/Qingluan/mroy-trans.git',
    author='Qing luan',
    author_email='darkhackdevil@gmail.com',
    license='MIT',
    zip_safe=False,
    packages=find_packages(),
    install_requires=['mroylib-min'],
    entriy_points={
        'console_scripts': ['Translate=trans.cmd:main']
    }

)


