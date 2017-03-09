#!/usr/bin/python3
# coding=utf-8
# -*- encoding: utf-8 -*-

import json
import os
import sys
import subprocess
from lxml import etree as ET
from lxml.etree import tostring
from itertools import chain
import argparse


def readConfig():
    with open(args.config) as dataFile:
        data = json.load(dataFile)
        return data['bidix']


def stringify_children(node):
    text = ([node.text]+list(chain(*([tostring(child).decode('utf-8')]
                                     for child in node.getchildren()))))
    return text


def makeKey(children):
    concat = []
    for child in children:
        if child is not None and '<s n=' not in child:
            concat.append(child)

    key = ''
    for strings in concat:
        key = key + strings

    return key


def genearateActualEntry(entry):
    children = stringify_children(entry)
    content = children[1]
    return content


def getLineNumber(pattern):
    with open(fName) as curFile:
        for num, line in enumerate(curFile, 1):
            if pattern in line:
                return num


def checkFile(fName):
    if os.path.isfile(fName.strip()):
        print('Working with monodix : ' + fName)
    else:
        print('File', fName, 'could not be found')
        exit(1)


def transferDirection():
    """
    As the name suggests, this is responsible for checking
    the transfer direction of the entry, which can only be one
    of the valid directions listed below.
    """
    validDirection = ['LR', 'RL', None]
    for key in mainSection:
        for lists in mainSection[key]:
            # This will only go through when a list with two nested lists is
            # encountered
            if len(lists) == 2 and (lists[-1] != 'regex' and
                                    lists[-1] != '<i>'):
                transferDir = (lists[0][0] if lists[0] is not None else None)
            else:
                continue
            if transferDir not in validDirection:
                print(errorsConf['transferDirection']
                      ['message'], key, transferDir)
                print('Issue found on line number : ',
                      getLineNumber(actualEntryMap[key]))


def repeatedEntries():
    """
    Responsible for detecting repeated entries in the
    main section. Eg :
    <e><p><l>sigrast<s n="vblex"/></l><r>övervinna<s n="vblex"/></r></p></e>
    <e><p><l>sigrast<s n="vblex"/></l><r>övervinna<s n="vblex"/></r></p></e>
    """
    for entry in mainSection:
        hashtable = []
        for lists in mainSection[entry]:
            if lists[-1] == 'regex' or lists[-1] == '<i>':
                continue
            leftData = lists[0]
            rightData = lists[1]
            try:
                leftData[2].sort
                leftData[3].sort

                rightData[2].sort
                rightData[3].sort
                rightData[4].sort
            except IndexError:
                continue

            hashtable.append(hash(str(leftData + rightData)))

        if len(set(hashtable)) != len(hashtable):
            print(errorsConf['repeatedEntries']['message'], entry)
            print('Issue found on line number : ',
                  getLineNumber(actualEntryMap[entry]))


def unwantedWhiteSpace():
    """
    According to apertium wide standards, white spaces
    are to be denoted using <b/>. This function is responsible
    for checking and reporting if any white spaces have crept
    in, in place of <b/>
    """
    for entry in mainSection:
        if entry is not None or len(entry) != 2:
            continue
        lKey = entry[0]
        rKey = entry[1]

        try:
            if ' ' not in lKey and ' ' not in rKey:
                pass
            else:
                print(errorsConf['unwantedWhiteSpace']['message'], entry)
                print('Issue found on line number : ',
                      getLineNumber(actualEntryMap[entry]))
        except TypeError:
            continue


def compareSdefs():
    """
    This function is responsible for comparing the
    sdefs of the sdefs of the two monodixes against
    that of the bidix and reporting if there are any
    sdefs present in the bidix that are absent in the
    monodixes.
    """

    print('Comparing Sdefs')
    # Sdefs present in bidix and not in left
    difference1 = set(bidixSdef).difference(leftSdef)
    # Sdefs present in bidix and not in right
    difference2 = set(bidixSdef).difference(rightSdef)
    difference = set(difference2).intersection(difference1)
    print(errorsConf['compareSdefs']['message'])
    print(difference)


def verifyInvariablePart():
    """
    Multiwords with inner inflection consist of a word that can inflect
    an invariable element. For these entries we need to specify the
    inflection paradigm just after the word that inflects.
    The invariable part must be marked with the element <g> in the right side.
    If the <g> tag is present in the bilingual dictionary,
    it should also be present in the monolingual dictionary.

    This function is responsible for detecting issues the same
    and notifying the user about the absence of <g>

    There is some issue in lt-expand which is causing an extra white space
    at the end of some of the characters, causing issues.
    """

    for entry in bidixCleaned:
        if 'LEFT' in bidixCleaned[entry]:
            monodix = leftCleaned
        else:
            monodix = rightCleaned

        gTagPresent = True if '#' in entry else False

        if gTagPresent:
            if entry.strip() in monodix:
                continue
            else:
                print(errorsConf['verifyInvariablePart']['message'], entry)


def parseExpandedDix(expanded):
    """
    This function given an expanded monolingual dictionary
    returns a dictionary of the format :

    lt-expand OP : bypasses:bypass<vblex><pres><p3><sg>
                   bypassed:bypass<vblex><past>

    Dictionary format : key = bypass
    Entry for key = [[vblex, presm, p3, sg], [vblex, past]]
    """
    extractedList = {}
    for entry in expanded:
        tmpList = []
        attributes = []
        try:
            if ':<:' in entry:
                rightPart = entry.split(':<:')[1]
            elif ':>:' in entry:
                rightPart = entry.split(':>:')[1]
            else:
                rightPart = entry.split(':')[1]  # Split it right in the centre

            rightPart = rightPart.split('<')

            for x in rightPart:
                hold = x.split('>')
                for iterator in hold:
                    if iterator != '':
                        attributes.append(iterator)
                tmpList.append(hold)

            head = tmpList[0][0]
            tail = tmpList[-1][-1]

            try:
                attributes.remove(head)
                attributes.remove(tail)
            except ValueError:
                pass

            key = head+tail

            if key in extractedList:
                extractedList[key].append(attributes)
            else:
                extractedList[key] = [attributes]

        except IndexError:
            pass
    return extractedList


def cleanExpandedBidixEntry(entry):
    """
    Formats the bidix entry that was generated to make
    it easier to work with.
    """

    tmpList = []
    tmpList = entry.split('<')
    tmpList = tmpList[1:]

    for x in tmpList:
        tmpList.remove(x)
        x = x[:-1]
        tmpList.append(x)

    return tmpList


def parseExpandedBidix(expanded):
    """
    Given data from lt-expand <<bidix>>,
    this parses it and make it maniputable (is that a word)?
    """
    extractedList = {}
    for entry in expanded:
        if ':<:' in entry:
            lr = entry.split(':<:')
        elif ':>:' in entry:
            lr = entry.split(':>:')
        else:
            lr = entry.split(':')

        try:
            tmpleft = lr[0]
            tmpright = lr[1]
        except IndexError:
            continue

        leftList = cleanExpandedBidixEntry(tmpleft)
        rightList = cleanExpandedBidixEntry(tmpright)

        leftKey = tmpleft.split('<')[0]
        rightKey = tmpright.split('<')[0]

        if leftKey not in extractedList:
            extractedList[leftKey] = [leftList, 'LEFT']
        else:
            extractedList[leftKey].append(leftList)

        if rightKey not in extractedList:
            extractedList[rightKey] = [rightList, 'RIGHT']
        else:
            extractedList[rightKey].append(rightList)

    return extractedList


def parseMainSection(tree):
    """
    Parses main section and makes the master dictionary
    """

    mainSection = {}

    sectionPath = './/e'
    i_path = './i'
    l_path = './/l'
    r_path = './/r'
    s_path = './s'
    regex_path = './re'

    for entry in tree.findall(sectionPath):

        tmpList = []
        tmpList2 = []
        tmpList3 = []
        tmpList4 = []
        tmpList5 = []
        lText, rText = None, None
        lKey, rKey = None, None

        actualEntry = genearateActualEntry(entry)

        try:
            transferDirection = entry.attrib['r']
        except:
            transferDirection = None

        tmpList.append(transferDirection)
        tmpList3.append(transferDirection)

        for lTag in entry.findall(l_path):
            lText = lTag.text
            tmpList.append(lText)

            tmpList2 = []
            for sTag in lTag.findall(s_path):
                tmpList2.append(sTag.attrib['n'])
            tmpList.append(tmpList2)
            allChildren = stringify_children(lTag)
            # debug
            lKey = makeKey(allChildren)

            tmpList2 = []
            for child in allChildren:
                try:
                    if '<b/>' in child:
                        tmpList2.append(child)
                except TypeError:
                    pass
            tmpList.append(tmpList2)

        for rTag in entry.findall(r_path):
            rText = rTag.text
            tmpList3.append(rText)
            allChildren = stringify_children(rTag)

            # debug
            rKey = makeKey(allChildren)

            tmpList2 = []
            for sTag in rTag.findall(s_path):
                tmpList2.append(sTag.attrib['n'])
            tmpList3.append(tmpList2)

            tmpList2 = []
            for child in allChildren:
                try:
                    if '<b/>' in child:
                        tmpList2.append(child)
                except TypeError:
                    pass
            tmpList3.append(tmpList2)

            tmpList2 = []
            for child in allChildren:
                try:
                    if '<g>' in child:
                        tmpList2.append(child)
                except TypeError:
                    pass
            tmpList3.append(tmpList2)

        for regex in entry.findall(regex_path):
            regExp = regex.text
            tmpList4.append(regExp)

            tmpList2 = []
            for sTag in regex.findall(s_path):
                tmpList2.append(sTag.attrib['n'])
            tmpList4.append(tmpList2)
            tmpList4.append('regex')

        for iTag in entry.findall(i_path):
            iText = iTag.text  # Lol seems like I'm doing something for apple
            tmpList5.append(iText)

            tmpList2 = []
            for sTag in iTag.findall(s_path):
                tmpList2.append(sTag.attrib['n'])
            tmpList5.append(tmpList2)
            tmpList5.append('<i>')

        if tmpList and tmpList3:
            key = (lKey, rKey)
            actualEntryMap[key] = actualEntry
            if key in mainSection:
                mainSection[key].append([tmpList, tmpList3])
            else:
                mainSection[key] = [[tmpList, tmpList3]]

        if tmpList4:
            key = (tmpList4[0])
            actualEntryMap[key] = actualEntry
            if key in mainSection:
                mainSection[key].append(tmpList4)
            else:
                mainSection[key] = [tmpList4]

        if tmpList5:
            key = (tmpList5[0])
            actualEntryMap[key] = actualEntry
            if key in mainSection:
                mainSection[key].append(tmpList5)
            mainSection[key] = [tmpList5]

    return mainSection


def parseSdef(tree):
    """
    Given any tree extracts sdefs
    """
    sdefs = []
    sdef_path = './/sdef'
    for sdef in tree.findall(sdef_path):
        sdefs.append(sdef.attrib['n'])

    return sdefs


def bidixErrors():
    """
    Takes care of errors related to pardef entries
    """

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
    Main function responsible for handling
    the bidix lint's worflow
    """

    global fName, errorsConf, actualEntryMap, sdefs, args
    args = arg_list

    actualEntryMap = {}
    sdefs = []
    # Read the config file to select the errors that are to be reported
    errorsConf = readConfig()
    fName = args.filename

    global leftTree, rightTree

    left = input("Enter path to the first language's monodix : ")
    checkFile(left)

    right = input("Enter the second language's monodix : ")
    checkFile(right)

    global mainSection, bidixSdef, leftSdef, rightSdef

    tree = ET.parse(fName)
    leftTree = ET.parse(left.strip())
    rightTree = ET.parse(right.strip())
    mainSection = parseMainSection(tree)

    bidixSdef = parseSdef(tree)
    leftSdef = parseSdef(leftTree)
    rightSdef = parseSdef(rightTree)

    leftCommand = subprocess.check_output(['lt-expand', left])
    rightCommand = subprocess.check_output(['lt-expand', right])
    bidixCommand = subprocess.check_output(['lt-expand', fName])

    str(leftCommand)

    leftExpanded = leftCommand.decode('utf-8').split('\n')
    rightExpanded = rightCommand.decode('utf-8').split('\n')
    bidixExpanded = bidixCommand.decode('utf-8').split('\n')

    # print (leftExpanded)

    global leftCleaned, rightCleaned, bidixCleaned

    leftCleaned = parseExpandedDix(leftExpanded)
    rightCleaned = parseExpandedDix(rightExpanded)
    bidixCleaned = parseExpandedBidix(bidixExpanded)

    # for entry in mainSection:
    #    print(entry, mainSection[entry])
    # print("Thanks")

    bidixErrors()  # Responsible for trigerring the lint

    # debugStatements
    # generateSTagOrders(leftTree)
    exit(1)


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='apertium_lint')

    argparser.add_argument('-c', '--config', action='store',
                           help='Configuration file for apertium-lint',
                           default='config.json')
    argparser.add_argument('filename', action='store', help='File to be linted')

    args = argparser.parse_args()
    sys.exit(main(args))
