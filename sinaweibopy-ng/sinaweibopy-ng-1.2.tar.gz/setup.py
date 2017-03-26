from distutils.core import setup
import weibo

kw = dict(
    name='sinaweibopy-ng',
    version=weibo.__version__,
    description='Sina Weibo OAuth 2 API Python SDK',
    long_description=open('README', 'r').read(),
    author='ifanr',
    author_email='ifanrx@ifanr.com',
    url='https://github.com/ifanrx/sinaweibopy',
    download_url='https://github.com/ifanrx/sinaweibopy',
    py_modules=['weibo'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ])

setup(**kw)
