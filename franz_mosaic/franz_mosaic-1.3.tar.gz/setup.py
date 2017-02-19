from setuptools import setup

setup(
    name='franz_mosaic',
    packages=['franz_mosaic'],
    version='v1.03',  # Ideally should be same as your GitHub release tag varsion
    description='reduces pictures and creates new image based on reduced information',
    author='raymond schmidt',
    author_email='raymond.schmidt@googlemail.com',
    url='https://github.com/kingmray/franz_mosaic',
    download_url='https://github.com/kingmray/franz_mosaic/archive/v1.0.3.tar.gz',
    keywords=['image', 'processing'],
    classifiers=[],
    entry_points={
        'console_scripts': ['franz-mosaic=franz_mosaic.app:main'],
    },
    install_requires=[
        "instagram-scraper==1.1.0",
        "Pillow==4.0.0"
    ]
)
