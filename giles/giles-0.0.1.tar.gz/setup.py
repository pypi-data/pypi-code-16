from setuptools import setup, find_packages
import giles


setup(
    author="Anthony Almarza",
    name="giles",
    version=giles.__version__,
    packages=find_packages(exclude=["test*", ]),
    url="https://github.com/anthonyalmarza/giles",
    description=(
        "``giles`` "
    ),
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    keywords=['giles', 'jira', 'workflow', ],
    install_requires=[
        'jira',
        'GitPython',
        'PyGithub',
        'pychalk',
        'slackclient',
        'urllib3[secure]'
    ],
    extras_require={'dev': ['ipdb', 'mock', 'tox', 'coverage']},
    include_package_data=True,
    scripts=[
        'bin/giles'
    ]
)
