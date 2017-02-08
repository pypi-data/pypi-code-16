

from setuptools import setup, find_packages


setup(name='remote-shell',
    version='0.1',
    description='a tools exc in remotes server',
    url='https://github.com/Qingluan/.git',
    author='Qing luan',
    author_email='darkhackdevil@gmail.com',
    license='MIT',
    zip_safe=False,
    packages=find_packages(),
    install_requires=['fabric3','mroylib-min'],
    entry_points={
        'console_scripts': ['rex=Ex.cmd:main']
    },
)


