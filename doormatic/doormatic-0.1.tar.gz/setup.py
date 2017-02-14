from distutils.core import setup

setup(
    name='doormatic',
    version='0.1',
    packages=['doormatic', 'doormatic.authentication', 'doormatic.authentication.mongo'],
    url='https://github.com/droberin/doormatic-authentication-service',
    download_url='https://github.com/droberin/doormatic-authentication-service/tarball/0.1',
    license='AGPL',
    author='Roberto Salgado',
    author_email='drober@gmail.com',
    description='Doormatic Authentication Service'
)
