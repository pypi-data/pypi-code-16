from setuptools import setup

repo_url = 'https://github.com/chillaranand/httpie-token-auth'


setup(
    name='httpie-token-auth',
    description='token Auth plugin for HTTPie.',
    long_description=open('README.md').read().strip(),
    version='0.1.1',
    author='Chillar Anand',
    author_email='anand21nanda@gmail.com',
    license='MIT',
    url=repo_url,
    download_url=repo_url,
    py_modules=['httpie_token_auth'],
    zip_safe=False,
    entry_points={
        'httpie.plugins.auth.v1': [
            'httpie_token_auth = httpie_token_auth:TokenAuthPlugin'
        ]
    },
    install_requires=[
        'httpie>=0.7.0'
    ],

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Environment :: Plugins',
        'License :: OSI Approved :: MIT License',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Utilities'
    ],
)
