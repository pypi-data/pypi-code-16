from setuptools import setup, find_packages
setup(
    name='base10',
    packages=find_packages('.'),
    version='0.4',
    license='MIT',
    description='Base10 is a metrics abstraction layer for \
            linking multiple metrics source and stores. It also \
            simplifies metric creation and proxying.',
    author='Matt Davis',
    author_email='mattdavis90@googlemail.com',
    url='https://github.com/mattdavis90/base10',
    download_url='https://github.com/mattdavis90/base10/archive/0.4.tar.gz',
    keywords=['metrics', 'abstraction'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Monitoring",
    ],
)
