# coding=utf-8
# -*- encoding: utf-8 -*-


import json
import sys
import os
import subprocess
from lxml import etree as ET
from lxml.etree import tostring
from itertools import chain
import argparse


def readConfig():
    with open(args.config) as dataFile:
        data = json.load(dataFile)
        return data['modes']


def stringify_children(node):
    text = ([node.text]+list(chain(*([tostring(child).decode('utf-8')]
                                     for child in node.getchildren()))))
    return text


def getLineNumber(pattern):
    with open(fName) as curFile:
        for num, line in enumerate(curFile, 1):
            if pattern in line:
                return num


def installBool():
    """
    In modes files, the install attribute can only
    take binary values : 'yes' or 'no'

      <mode name="fr-eo" install="no">

    This function is responsible for making sure
    nothing else is used for the same
    """

    valid = ['yes', 'no']
    for entry in modes:
        try:
            installMode = modes[entry]['install']
        except KeyError:
            continue

        if installMode not in valid:
            print(errorsConf['installBool']['message'] % (installMode, entry))


def repeatedProgram():
    """
    Ever modes files consits of various programs
    and there is always a chance that a certain
    program may unintentionally get repeated

    <program name="apertium-transfer">
        <file name="apertium-eo-fr.fr-eo.t1x"/>
        <file name="fr-eo.t1x.bin"/>
        <file name="fr-eo.autobil.bin"/>
     </program>

     <program name="apertium-transfer">
        <file name="apertium-eo-fr.fr-eo.t1x"/>
        <file name="fr-eo.t1x.bin"/>
        <file name="fr-eo.autobil.bin"/>
     </program>

    This function reports any such errors if they
    manage to creep in.
    """
    print('Checking repeated programs in modes')
    for entry in modes:
        modes[entry]
        for program in progData:
            hashList = []

            if program == 'install':
                continue

            fileLists = progData[program]

            for fileList in fileLists:
                hashText = ''
                for file in fileList:
                    temp = file.strip()
                    hashText = hashText + temp
                hashText = hashText + program
                hashList.append(hashText)

            if len(set(hashList)) != len(hashList):
                print(errorsConf['repeatedProgram']['message'] % (program))


def validateProgram():
    """
    Ever modes files consists of various programs,
    each having a unique name. It is possible that
    a program may be wrongly named and passes unnoticed.

      <program name="apertium-ppretransfer"/>

    This function detects and reports such invalid names.

    It assumes that you have apertium and lt-toolbox
    install on your system.
    """
    print('Checking to ensure valid program names')

    for entry in modes:
        elements = modes[entry]
        for element in elements:
            if element == 'install':
                continue

            program = element.split()
            # Generating the man page of the program to check if it exists or
            # not
            ['man', program[0]]

            try:
                devnull = open(os.devnull)
                # This prevents the o/p of the subprocess from totally clogging
                # up the terminal
                subprocess.Popen(temp, stdout=devnull,
                                 stderr=devnull).communicate()
            except OSError as e:
                if e.errno == os.errno.ENOENT:  # Incase the file is not found
                    print(errorsConf['validateProgram']
                          ['message'] % (program[0]))


def enforceRules():
    """
    This function is responsible for enforcing
    certain rules specific to given programs.
    This is not an exhaustive function and new
    rules relating to programs (flags and attributes)
    will be added here.
    """

    print('Enforcing certain rules')

    # 1. Enforcing the use of apertium-tagger with “-g $2”
    for entry in modes:
        for program in modes[entry]:
            # Splitting the name into a list for easier comparision
            tokenList = program.split()
            if tokenList[0] == 'apertium-tagger':
                validTokens = ['-g', '$2']
                # Diff is going to be empty if -g $2 are used in the name.
                diff = set(validTokens) - set(tokenList)
                if diff:
                    print(
                        'Warning : apertium-transfer used without'
                        " the flag '-g' or argument '$2'")


def installSwitchNo():
    """
    If in the definition of a certain mode, the attribute
    install=”no”, the name should have an
    appropriate suffix like -morph, -interchunk, etc.

    -anmor or -morph run the morphological analysers
    -disam runs up until morphological (CG) disambiguation
    -syntax runs up until syntactical (CG) disambiguation
    -tagger runs up until probabilistic (apertium-tagger)
     disambiguation (or, if no .prob, up until the last disambiguation step)
    -biltrans runs up until the bidix
    -lex runs up until lexical selection
    -transfer runs up until (1-stage) transfer
    -chunker runs up until the first stage of 3-or-more-stage transfer
    -interchunk runs up until the second stage of 3-stage transfer
    -interchunk1 and -interchunk2 are used when the pair has 4-stage transfer
    -postchunk runs up until the last stage of transfer
    -dgen run up until generation (using lt-proc -d to include debug symbols)
    """

    validSuffix = ['morph', 'interchunk', 'anmor', 'disam', 'syntax',
                   'tagger', 'biltrans', 'lex', 'transfer', 'chunker'
                   'interchunk1', 'interchunk2', 'postchunk', 'dgen']

    # Need to add more suffixes here

    print("Enforcing rules related to install='no'")
    for entry in modes:
        flag = 0
        # Flag indicates if proper suffix has been used or not.
        # flag = 1 --> Valid suffix
        attr = modes[entry]
        install = attr['install']
        # This should only work when install="no" or the install attribute is
        # absent
        if install is None or install == 'no':
            modeName = entry.split('-')
            for iterator in validSuffix:
                if iterator in modeName:
                    flag = 1  # Valid suffix found

            if flag == 0:
                print(errorsConf['installSwitchNo']['message'] % (entry))
                print('Valid suffixes to be used : ', validSuffix)


def locateFile():
    """
    Assuming you're working with modes.xml present
    in the same directory as the other files for
    the given language pair, this function checks
    and prompts incase a file defined in a program :

    <program name="apertium-interchunk">
        <file name="apertium-eo-fr.fr-eo.antaux1_t2x"/>
        <file name="xyz.bin"
    </program>

    is present in the PWD or not.
    """

    for entry in modes:
        for element in modes[entry]:
            if element == 'install':
                continue
            for fileLists in modes[entry][element]:
                for file in fileLists:
                    # Checking if the file is present in the PWD
                    if not os.path.isfile(file):
                        print(errorsConf['locateFile']['message'] % (file))


def emptyProgram():
    """
    Not so much a risk, but this function prompts
    if a given program does not have any file
    associated with it.

        <program name="apertium-pretransfer"/>

    """
    for entry in modes:
        for element in modes[entry]:
            if element == 'install':
                continue
            if modes[entry][element] == [[]]:
                print(errorsConf['emptyProgram']['message'] % (element, entry))


def parseModes():
    """
    Structure of the modes dictionary

    {modeName :
                { programName : [[list of files associated],
                [list of files associated if repeated definition]]
                },
                { programName : [[list of files associated]]
                }
    }
    """

    modes = {}  # The main dictionary in which all the data will be indexed
    modePath = './/mode'
    programPath = './/program'

    for mode in tree.findall(modePath):
        modeName = mode.attrib['name']
        progDict = {}

        try:  # Sometimes, the install attrib is not present in the definition.
            modeInstall = mode.attrib['install']
            progDict['install'] = modeInstall

        except KeyError:
            progDict['install'] = None  # Defaulting it to None
            print("Error : 'install' attrib missing in mode "
                  'definition <mode name = \"%s\"> ' % (modeName),
                  file=sys.stderr)
            # can force quit here to enforce use of install

        for program in mode.findall(programPath):
            progName = program.attrib['name']

            if progName not in progDict:
                progDict[progName] = []

            fileList = []  # List of files associated with each program

            for file in program.iterchildren():
                try:
                    fileName = file.attrib['name']
                except KeyError:
                    continue
                fileList.append(fileName)

            progDict[progName].append(fileList)

        modes[modeName] = progDict

    return modes


def modesErrors(errorsConf):
    for key in errorsConf:
        if errorsConf[key]['enable']:
            valid = globals().copy()
            valid.update(locals())
            method = valid.get(key)
            if not method:
                raise NotImplementedError('Method %s not implemented' % key)
            method()


def main(arg_list):
    """
    Main function, handles the lint's workflow
    """
    global errorsConf, tree, fName, args
    args = arg_list

    errorsConf = readConfig()
    fName = arg1

    global modes

    tree = ET.parse(fName)
    modes = parseModes()

    # print(modes)

    # modesErrors(errorsConf)


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='apertium_lint')

    argparser.add_argument('-c', '--config', action='store',
                           help='Configuration file for apertium-lint',
                           default='config.json')
    argparser.add_argument('filename', action='store', help='File to be linted')

    args = argparser.parse_args()
    sys.exit(main(args))
