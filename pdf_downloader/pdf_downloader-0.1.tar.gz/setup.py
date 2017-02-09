from distutils.core import setup

setup(
    name='pdf_downloader',
    version='0.1',
    packages=['pdf_downloader'],
    url='https://github.com/sokrutu/PdfDownloader',
    license='MIT',
    author='Mathias Pfeiffer',
    author_email='mathias.pfeiffer@rwth-aachen.de',
    description='Download PDFs from the RWTH Aachen L2P',
    install_requires=[
        'python-ntlm'
    ]
)
