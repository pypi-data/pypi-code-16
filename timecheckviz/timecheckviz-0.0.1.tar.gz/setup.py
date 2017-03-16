from setuptools import find_packages, setup


setup(
    name = 'timecheckviz',
    packages = find_packages(),
    version = '0.0.1',
    description = 'Visualizer for timecheck',
    author = 'Arpit Bhayani',
    author_email = 'arpit.b.bhayani@gmail.com',
    url = 'https://github.com/arpitbbhayani/timecheckviz',
    download_url = 'https://github.com/arpitbbhayani/timecheckviz',
    keywords = ['time', 'metrics', 'visualizer', 'timecheck'],
    include_package_data=True,
    install_requires=[
        'numpy==1.12.0',
        'matplotlib==2.0.0'
    ],
    entry_points= {
        'console_scripts': [
            'timecheckviz=timecheckviz.cmdline:execute'
        ]
    }
)
