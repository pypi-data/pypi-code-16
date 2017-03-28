from setuptools import setup, find_packages

setup(
    name="arc",
    version="0.0.1b",
    packages=find_packages(),
    # install_requires=(
    #     "python-dateutil",
    #     "requests",
    #     "iso8601",
    #     "pytz",
    # ),
    # test_suite='p2p.tests',
    author="Tronc Newsroom Product Team, Charley Bodkin",
    author_email="charley.bodkin@latimes.com",
    description="Wrapper for Arc's various APIs",
    long_description="Python wrapper for communicating to The Washington Post's Arc CMS",
    url="https://diggit.trbprodcloud.com/newsroom-products/arc-python",
    license="MIT",
)
