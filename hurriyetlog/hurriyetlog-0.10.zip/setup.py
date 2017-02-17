from distutils.core import setup

setup(
    name="hurriyetlog",
	packages = ["hurriyetlog"],
    version="0.10",
    description="Hurriyet.com.tr merkezi log kutuphanesine loglamak icin kullanabilirsiniz",

	install_requires=["pika>=0.10.0"],

    author="hurriyet.com.tr",
    author_email="destek@hurriyet.com.tr",

    url="http://www.hurriyet.com.tr",
    license="MIT"
)
