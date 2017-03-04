from setuptools import setup

setup(
    name='grcpass',
    version='1.0.1',
    description='Simple script which scrapes off password from www.grc.com/passwords.htm',
    url='https://github.com/arturtamborski/grcpass',
    download_url='https://github.com/arturtamborski/grcpass/archive/1.0.1.tar.gz',
    keywords='password generator',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Security',
    ],
    author='Artur Tamborski',
    author_email='tamborskiartur@gmail.com',
    license='MIT',
    packages=['grcpass'],
    entry_points={'console_scripts':['grcpass=grcpass.command_line:main']},
    include_package_data=True,
    zip_safe=False
)
