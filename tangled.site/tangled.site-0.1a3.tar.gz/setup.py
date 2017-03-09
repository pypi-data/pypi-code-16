from setuptools import setup


setup(
    name='tangled.site',
    version='0.1a3',
    description='Simple site/blog/cms',
    long_description=open('README.rst').read(),
    url='http://tangledframework.org/',
    download_url='https://github.com/TangledWeb/tangled.site/tags',
    author='Wyatt Baldwin',
    author_email='self@wyattbaldwin.com',
    packages=[
        'tangled',
        'tangled.site',
        'tangled.site.model',
        'tangled.site.resources',
        'tangled.site.tests',
    ],
    include_package_data=True,
    install_requires=[
        'tangled.mako>=0.1a3',
        'tangled.sqlalchemy>=0.1a5',
        'tangled.web>=0.1a10',
        'bcrypt>=3.1.3',
        'Markdown>=2.6.8',
        'SQLAlchemy>=1.1.6',
    ],
    extras_require={
        'dev': [
            'tangled.web[dev]>=0.1a10',
        ],
    },
    entry_points="""
    [tangled.scripts]
    site = tangled.site.command

    """,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)
