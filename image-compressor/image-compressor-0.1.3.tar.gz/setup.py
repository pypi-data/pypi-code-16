from distutils.core import setup

setup(
    name='image-compressor',
    version='0.1.3',
    description='A Python package to compress images ',
    author='sandesh naroju',
    author_email='sandeshnaroju@gmail.com',
    package_dir={'': 'compress'},
    py_modules=['compress'],
    entry_points='''
        [console_scripts]
        image-compress=compress:main
    ''',
    install_requires=[
        # list of this package dependencies
        'pillow'
    ]

)
