from setuptools import setup

def readme():
    with open('README.txt') as f:
        return f.read()
 
setup(
    name = 'awssamlpy2',
    version = '1.0.6.2',
    description = 'SAML federated API access for AWS',
    author='Neeharika',
    author_email='neeharika.mm@gmail.com',
    classifiers=[
        'Programming Language :: Python',
        'Environment :: Console',
    ],
	long_description=readme(),
	install_requires=['beautifulsoup4','requests','html5lib','boto'],
	scripts=['aws-saml']
)
