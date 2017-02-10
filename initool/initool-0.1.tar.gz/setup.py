try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup  #  can't have the entry_points option here.



setup(
    name='initool',
    version='0.1',
    description='INI files manipulator (get/set/remove) options and sections',
    url="https://github.com/xmonader/initool",
    author='Ahmed T. Youssef',
    author_email='xmonader@gmail.com',
    maintainer='Ahmed T. Youssef',
    maintainer_email='xmonader@gmail.com',
    packages=['initool'],
    license='BSD 3-Clause License',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
    ],
    entry_points={
        'console_scripts': ['initool=initool:main']
    }
)
