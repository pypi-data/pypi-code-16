from setuptools import setup, find_packages

setup(
    name='Amuru',
    description='a tiny command invoker/dispatcher pattern library ',
    long_description="""See the Github project page (https://github.com/thynquest/amuru.git) for more on information""",
    license='MIT',
    keywords="command invoker/dispatcher pattern library",
    version='1.0.0',
    author='Franck Kambiwa',
    author_email='thynquest@gmail.com',
    url='https://github.com/thynquest/amuru.git',

    packages=find_packages(),
    install_requires=['ez_setup'],
        
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Distributed Computing",
    ]
)
