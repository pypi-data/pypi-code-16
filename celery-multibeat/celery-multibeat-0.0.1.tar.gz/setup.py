from setuptools import setup

setup(
    name = "celery-multibeat",
    description = "A Distributed Celery Beat Scheduler built on Redis",
    version = "0.0.1",
    license = "Apache License, Version 2.0",
    author = "Ryler Hockenbury",
    author_email = "ryler.hockenbury@gmail.com",
    url = "https://github.com/rhockenbury/multibeat",
    download_url = 'https://github.com/rhockenbury/multibeat/tarball/0.0.1',
    keywords = [
        "celerybeat",
        "celery",
        "beat",
        "distributed",
        "redis",
        "lock"
    ],
    packages = [
        "multibeat"
    ],
    install_requires=[
        "setuptools",
        "redis>=2.10.3",
        "celery>=3.1.9,<3.2"
    ]
)
