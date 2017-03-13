from distutils.core import setup

setup(
    name='easy_sharepoint',
    version='0.1',
    packages=['easy_sharepoint'],
    url='https://github.com/Landarell/EasySharePoint',
    license='MIT',
    author='Krzysztof Growinski',
    author_email='k.growisnski@outlook.com',
    description='Sharepoint Operations Python Library',
    keywords = ['sharepoint'],
    requires=[
        "requests",
        "requests_ntlm"
    ]
)
