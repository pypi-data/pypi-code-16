from setuptools import setup

with open('version.txt', 'r') as f:
	curr_version = f.read()

version_url = 'https://github.com/jonesmartins/pycrusher/tarball/'\
             + curr_version
setup(
    name='pycrusher',
    version=curr_version,
    url='https://github.com/jonesmartins/pycrusher',
    download_url=version_url, 
    license='MIT',
    author='Jones Martins',
    author_email='jonesmvc@hotmail.com',
    description='Generate lossy image compressions for fun!',
    keywords=['lossy', 'compression', 'compress', 'jpeg'], 
    install_requires=['Pillow', 'argparse', 'tqdm'], 
    packages=['pycrusher'],
    entry_points={'console_scripts': ['pycrusher = pycrusher:main']},    
    )
