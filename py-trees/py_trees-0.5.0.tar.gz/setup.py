#!/usr/bin/env python

from setuptools import find_packages, setup
# from catkin_pkg.python_setup import generate_distutils_setup

install_requires = [
    # docs
    "sphinx_argparse",
    "sphinx_rtd_theme",
    "pydot",
    # runtime
    'enum34',
    'PyYAML',
    'vcstool',
]

d = setup(
    name='py_trees',
    version='0.5.0',
    packages=find_packages(exclude=['tests*', 'docs*']),
    install_requires=install_requires,
    author='Daniel Stonier, Naveed Usmani, Michal Staniaszek',
    maintainer='Daniel Stonier <d.stonier@gmail.com>, Naveed Usmani <naveedhd@gmail.com>',
    url='http://github.com/stonier/py_trees_suite',
    keywords='behaviour-trees',
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Software Development :: Libraries'
    ],
    description="pythonic implementation of behaviour trees",
    long_description="A behaviour tree implementation for rapid development of small scale decision making engines that don't need to be real time reactive.",
    license='BSD',
    # test_suite='tests',
    # Unfortunately catkin builds do not like this
    #     entry_points={
    #         'console_scripts': [
    #             'py-trees-demo-action-behaviour = py_trees.demos.action:main',
    #             'py-trees-demo-behaviour-lifecycle = py_trees.demos.lifecycle:main',
    #             'py-trees-demo-blackboard = py_trees.demos.blackboard:main',
    #             'py-trees-demo-context-switching = py_trees.demos.context_switching:main',
    #             'py-trees-demo-dot-graphs = py_trees.demos.dot_graphs:main',
    #             'py-trees-demo-selector = py_trees.demos.selector:main',
    #             'py-trees-demo-sequence = py_trees.demos.sequence:main',
    #             'py-trees-demo-tree-stewardship = py_trees.demos.stewardship:main',
    #         ],
    #     },
    # So we do the tedious way
    scripts=['scripts/py-trees-demo-action-behaviour',
             'scripts/py-trees-demo-behaviour-lifecycle',
             'scripts/py-trees-demo-blackboard',
             'scripts/py-trees-demo-context-switching',
             'scripts/py-trees-demo-dot-graphs',
             'scripts/py-trees-demo-selector',
             'scripts/py-trees-demo-sequence',
             'scripts/py-trees-demo-tree-stewardship',
             ],
)
