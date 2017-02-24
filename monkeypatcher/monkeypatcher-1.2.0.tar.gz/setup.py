from setuptools import setup, find_packages

setup(
    name='monkeypatcher',
    version='1.2.0',
    description='A python monkey-patching library',
    url='https://github.com/iki/monkeypatch',
    author='Thomas Vagner',
    author_email='vagner.thomas@yandex.com',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7'
    ],
    keywords='monkeypatch testing mock',
    packages=find_packages(),
    install_requires=['requests']
)
