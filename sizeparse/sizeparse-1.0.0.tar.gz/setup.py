from setuptools import setup

def main():
	setup(
		name="sizeparse",
		version="1.0.0",
		description="A simple Python library for parsing strings denoting byte-capacities with SI or IEC suffixes.",
		license="Unlicense",
		url="https://github.com/chrisgavin/sizeparse",
		packages=["sizeparse"],
		test_suite="tests.get_suite",
		classifiers=[
			"License :: Public Domain",
			"Topic :: Software Development :: Libraries :: Python Modules",
			"Programming Language :: Python :: 2",
			"Programming Language :: Python :: 2.7",
			"Programming Language :: Python :: 3",
			"Programming Language :: Python :: 3.2",
			"Programming Language :: Python :: 3.3",
			"Programming Language :: Python :: 3.4",
			"Programming Language :: Python :: 3.5",
			"Programming Language :: Python :: 3.6",
		],
	)

if __name__ == "__main__":
	main()
