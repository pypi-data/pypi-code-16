from distutils.core import setup
setup(
    name = 'uniqueWords',
    version = '1.1.0',
    py_modules = ['uniqueWords'],
    author = 'Ankit Aich',
    author_email = 'ankitaich09@gmail.com',
    description = 'The module helps the user make new files with stemmed words for keyword extraction. The user needs to put a text file into the same folder and use function uniqueWords(filename). Automatically two files with names assigned by the function are made. The first contains the final words but not stemmed and the second file contains all stemmed words and have no duplicates. The final files are without any punctuations numbers or meaningless words.',
    )
