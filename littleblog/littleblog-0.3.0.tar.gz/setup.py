from setuptools import setup

setup(
    name='littleblog',
    version='0.3.0',
    description='littleblog - a simple static site generator',
    url='https://github.com/wookalar/littleblog',
    author='Wookalar Software',
    author_email='doc.tart@wookalar.io',
    license='AGPLv3',
    package_data={
        'littleblog': [
            'skel/*.py', 'skel/templates/*.html', 'skel/static/*.css'],
    },
    install_requires=[
        'click>=6.6',
        'Jinja2>=2.8',
        'Markdown>=2.6.7',
        'MarkupSafe>=0.23',
        'Pygments>=2.1.3',
    ],
    install_package_data=True,
    entry_points = {
        'console_scripts': ['littleblog=littleblog.cli:cli'],
    },
    packages=['littleblog'],
)
