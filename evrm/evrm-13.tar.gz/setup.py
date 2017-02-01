#!/usr/bin/env python3
#
#

import os
import sys
import os.path

def j(*args):
    if not args: return
    todo = list(map(str, filter(None, args)))
    return os.path.join(*todo)

if sys.version_info.major < 3:
    print("you need to run mads with python3")
    os._exit(1)

try:
    use_setuptools()
except:
    pass

try:
    from setuptools import setup
except Exception as ex:
    print(str(ex))
    os._exit(1)

target = "evrm"
upload = []

def uploadfiles(dir):
    upl = []
    if not os.path.isdir(dir):
        print("%s does not exist" % dir)
        os._exit(1)
    for file in os.listdir(dir):
        if not file or file.startswith('.'):
            continue
        d = dir + os.sep + file
        if not os.path.isdir(d):
            if file.endswith(".pyc") or file.startswith("__pycache"):
                continue
            upl.append(d)
    return upl

def uploadlist(dir):
    upl = []

    for file in os.listdir(dir):
        if not file or file.startswith('.'):
            continue
        d = dir + os.sep + file
        if os.path.isdir(d):   
            upl.extend(uploadlist(d))
        else:
            if file.endswith(".pyc") or file.startswith("__pycache"):
                continue
            upl.append(d)

    return upl

setup(
    name='evrm',
    version='13',
    url='https://bitbucket.org/thatebart/evrm',
    author='Bart Thate',
    author_email='bthate@dds.nl',
    description="ANTIPSYCHOTICA - AKATHISIA - KATATONIE - SEDERING - SHOCKS - LETHALE KATATONIE !!!".upper(),
    license='MIT',
    include_package_data=True,
    zip_safe=False,
    install_requires=["mads",],
    scripts=["bin/evrm"],
    packages=['evrm', ],
    long_description='''

“After 17 to 27 months of treatment, both haloperidol- and olanzapine-treated monkeys had an equivalent and highly significant 8% to 11% decrease in fresh brain weight and volume when compared with the sham group.”

STRAFBAAR

| Antipsychotica zijn dodelijk, het zijn neurotoxines.
| Het toedienen van dodelijke stof is strafbaar en het Openbaar Ministerie dient te vervolgen voor slachtoffers die dat zelf niet kunnen.
| De (F)ACT methodiek is onverantwoord, het brengt met toediening van dodelijke stof EN het ontbreken van zorg levensbedreigende situaties.

| Met EVRM kan je loggen welke bijwerkingen je van de medicijnen krijgt.

LOGGEN

| log <txt>
| log <txt> +5
| log <txt> -2

Het find command om log terug te zoeken:

| find log
| find log=wakker
| find email From=om.nl From Subject Date start=2013-01-01 end=2013-02-01

Om over een periode te kunnen zoeken:

| today log
| week log
| week log=wiet
| week log=wakker

CONTACT

| Bart Thate
| botfather on #dunkbots irc.freenode.net
| bthate@dds.nl, thatebart@gmail.com

| MADS is sourcecode released onder een MIT compatible license.
| MADS is een event logger.

''',
   data_files=[("docs", ["docs/conf.py","docs/index.rst"]),
               (j('docs', 'jpg'), uploadlist(j("docs","jpg"))),
               (j('docs', 'txt'), uploadlist(j("docs", "txt"))),
               (j('docs', '_templates'), uploadlist(j("docs", "_templates")))
              ],
   package_data={'': ["*.crt"],
                 },
   classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Topic :: Utilities'],
)
