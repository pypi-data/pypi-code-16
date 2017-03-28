from setuptools import setup

setup(
    name='adk-testlab',
    version='0.0.1',
    author='Andrew Knight',
    author_email='knight.andrew@gmail.com',
    description=('A personal reference collection of test projects for my development efforts.'),
    license='MIT',
    keywords='knight testing lab',
    url='https://github.com/knightman/adk-testlab',
    packages=['helloworld', 'test'],
    long_description=open("README.md").read(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
    ],
)
