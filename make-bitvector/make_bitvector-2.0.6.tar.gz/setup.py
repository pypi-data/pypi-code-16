from setuptools import setup

setup(name='make_bitvector',
			version='2.0.6',
			description='Create bitvectors for DMS seq data',
			url='https://gitlab.com/Rouskin-Lab/bitvector',
			author='Rouskin-Lab',
			author_email='srouskin@wi.mit.edu',
			license='MIT',
			packages=['make_bitvector'],
			entry_points = {
				"console_scripts": ['make_bitvector = make_bitvector.make_bitvector:main']
				},
			classifiers=[
			# How mature is this project? Common values are
			#   3 - Alpha
			#   4 - Beta
			#   5 - Production/Stable
			'Development Status :: 3 - Alpha',

			# Indicate who your project is intended for
			'Intended Audience :: Developers',

			# Pick your license as you wish (should match "license" above)
			'License :: OSI Approved :: MIT License',

			# Specify the Python versions you support here. In particular, ensure
			# that you indicate whether you support Python 2, Python 3 or both.
			'Programming Language :: Python :: 2.7',
			],

			install_requires=[
					'pandas',
					'pysam',
					'numpy',
					'multiprocessing',
			],
			zip_safe=False)