"""
Copyright 2017 Jeff Ward

Licensed under the Apache License, Version 2.0 (the "License"); 
you may not use this file except in compliance with the License. 
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, 
software distributed under the License is distributed on an 
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, 
either express or implied. See the License for the specific 
language governing permissions and limitations under the License.
"""

from setuptools import setup

setup(
    name='easycache',
    packages=['easycache'],
    version='0.1.0a1',
    description = ("Implementation of a simple persistent value and function cache."),
    author = "Jeff Ward",
    url="https://bitbucket.org/GreedyUser/easycache",
    license='Apache License, Version 2.0',
    long_description=open("README.rst").read(),
    classifiers=[]
)