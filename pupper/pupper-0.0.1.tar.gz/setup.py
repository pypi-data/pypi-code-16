import setuptools
import subprocess


INSTALL_REQUIRES = [
    'Click>=6.0',
    # TODO: put package requirements here
]

EXTRAS_REQUIRE = [
    # TODO: put conditional requirements here
]

# if int(setuptools.__version__.split(".", 1)[0]) < 18:
#     if sys.version_info[0:2] < (3, 3):
#        INSTALL_REQUIRES.append("monotonic")
# else:
#     EXTRAS_REQUIRE[":python_version<'3.3'"] = ["monotonic"]

TESTS_REQUIRE = [
    # TODO: put test requirements here
]


class Venv(setuptools.Command):
    user_options = []

    def initialize_options(self):
        """Abstract method that is required to be overwritten"""

    def finalize_options(self):
        """Abstract method that is required to be overwritten"""

    def run(self):
        venv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'venv', 'pupper')
        venv_cmd = [
            'virtualenv',
            venv_path
        ]
        print('Creating virtual environment in ', venv_path)
        subprocess.check_call(venv_cmd)
        print('Linking `activate` to top level of project.\n')
        print('To activate, simply run `source activate`.')
        try:
            os.symlink(
                os.path.join(venv_path, 'bin', 'activate'),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), 'activate')
            )
        except OSError:
            print('Unable to create symlink, you may have a stale symlink from a previous invocation.')


setuptools.setup(
    name='pupper',
    version='0.0.1',
    description="Pupper is a utility to manage all your python cli utils!",
    author="Loren M. Carvalho",
    author_email='me@loren.pizza',
    url='https://github.com/sixninetynine/pupper',
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'pupper=pupper.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=INSTALL_REQUIRES,
    extras_reqiure=EXTRAS_REQUIRE,
    tests_require=TESTS_REQUIRE,
    license="MIT license",
    zip_safe=False,
    keywords='pupper',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='test',
    cmdclass={'venv': Venv},
)
