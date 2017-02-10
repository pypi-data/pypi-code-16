from distutils.core import setup
setup(
        name = 'kordic',
        version = '1.0.0',
        packages=['kordic'],
        description = 'A simple query of dictionary on terminal for Korean',
        url = 'http://www.coupang.com',
        author = 'sonic',
        author_email = 'ultrakain@gmail.com',
        py_modules = ['kordic'],
        license='MIT',
        keywords='simple english dictionary korean',
        install_requires=['beautifulsoup4', 'requests'],
        entry_points={
                'console_scripts': [
                    'kordic=kordic:main',
                ],
            },
)