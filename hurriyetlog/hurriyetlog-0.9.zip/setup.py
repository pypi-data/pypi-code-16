from distutils.core import setup

setup(
    name="hurriyetlog",
	packages = ["hurriyetlog"],
    version="0.9",
    description="Hurriyet.com.tr merkezi log kutuphanesine loglamak icin kullanabilirsiniz",

	install_requires=["pika"],

    author="hurriyet.com.tr",
    author_email="destek@hurriyet.com.tr",

    url="http://www.hurriyet.com.tr",
    license="MIT"
)
