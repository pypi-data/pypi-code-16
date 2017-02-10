#coding:utf-8
from setuptools import setup,find_packages

setup(
    name='django-bootstrap-submenu',
    version='0.1.2',
    description='bootstrap-submenu',
    long_description=open('README.md','r').read(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: End Users/Desktop',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Framework :: Django',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
    ],
    keywords=('bootstrap','submenu'),
    author=u'depth.net(深度网络)',
    author_email='yuerthe9@aliyun.com',
    url='http://sdcto.cn',
    license='MIT License',
    packages=find_packages(),
    install_requires=[
        'django>=1.8.7',
    ],
    include_package_data=True,
    zip_safe=False,
)
