#!/usr/bin/python3
# coding=utf-8
# -*- encoding: utf-8 -*-

import json
import sys
from lxml import etree as ET
from lxml.etree import tostring
from itertools import chain
from collections import OrderedDict
import argparse


def readConfig():
    with open(args.config) as dataFile:
        data = json.load(dataFile)
        return data['transfer']


def reportError(errorNum):
    print('Repeated paradigms ', errorNum)
    return


def stringify_children(node):
    text = ([node.text]+list(chain(*([tostring(child).decode('utf-8')]
                                     for child in node.getchildren()))))
    return text


def getLineNumber(pattern):
    with open(fName) as curFile:
        for num, line in enumerate(curFile, 1):
            if pattern in line:
                return num


def repeatedEntriesCatItem():
    """
    Checks for repeated cat-items
    """

    print('Checking for repeated entries within def-cat')

    for entry in defCats:
        hashTableTags = []
        hashTableCombined = []

        for items in defCats[entry]:
            tagHash = hash(entry[1])
            entireHash = hash(str(items))
            hashTableTags.append(tagHash)
            hashTableCombined.append(entireHash)

        if len(set(hashTableTags)) != len(hashTableTags):
            print('Warning : Repeated tag entries found for : ', entry)

        if len(set(hashTableCombined)) != len(hashTableCombined):
            print(errorsConf['repeatedEntriesCatItem']['message'], entry)


def conflictingCatItem():
    """
    """

    print('Checking for presence of same cat-items in different def-cats')

    reverseMap = {}
    for item in defCats:
        elements = defCats[item]
        for element in elements:
            element = tuple(element)
            if element in reverseMap:
                print('Repeated cat-item', element,
                      'found for entries :', item, reverseMap[element])
            else:
                reverseMap[element] = item


def repeatedEntriesAttrItem():
    """
    Checks for repeated attr-items
    """

    print('Checking for repeated entries with in def-attr')

    for entry in defAttrs:
        hashTable = []

        for items in defAttrs[entry]:
            tagHash = hash(items)
            hashTable.append(tagHash)

        if len(set(hashTable)) != len(hashTable):
            print(errorsConf['repeatedEntriesAttrItem']['message'], entry)


def checkValidPosition():
    """
    When calling the macroinstructions in a rule,
    it must be specified which is the main lexical
    unit (the one which most heavily determines the
    gender or number of the other lexical units) and
    which other lexical units of the pattern have to
    be included in the agreement operations,
    in order of importance. This is done with the <with-param pos=""/> element.
    Other than with-param, various other tags like <clip pos=""/>
    depend on the position of the element.
    This function makes sure the numbers used
    align with those in the pattern definition
    """

    print('Checking for valid position')

    for entry in rules:
        for elements in rules[entry]:
            if 'pattern-item' == elements[0]:
                validMaxPos = len(elements[1])
            if 'pos' in elements[1]:
                tag = elements[0]
                pos = int(elements[1]['pos'])
                if pos > validMaxPos:
                    print(errorsConf['checkValidPosition']
                          ['message'], tag, pos, entry)


def enforceBreakTag():
    """
    This works now.
    """

    print('Checking for the presence of <b/> tags between consecutive <lu>s')

    sectionPath = './section-rules'

    for section in tree.findall(sectionPath):
        for rule in section:
            for tags in rule.iter():
                childList = []

                for child in tags.iterchildren():
                    childList.append(child.tag)

                if 'lu' in childList:
                    luCount = childList.count('lu')
                    bCount = childList.count('b')

                    if luCount > bCount + 1:
                        lineNum = tags.sourceline
                        element = tags.tag
                        print(errorsConf['enforceBreakTag'][
                              'message'] % (element, lineNum))


def enforceSide():
    """
    """

    print("Checking to ensure that side='tl' in <out> tags ")

    sectionPath = './section-rules'

    for section in tree.findall(sectionPath):
        for rule in section:
            for tags in rule.iter():
                element = tags.tag
                if element == 'out':
                    for child in tags.iter():
                        attributes = child.attrib
                        if 'side' in attributes and attributes['side'] == 'sl':
                            print(errorsConf['enforceSide']['message'] % (
                                child.tag, child.sourceline))


def macroNames():
    """
    """

    macroNames = []
    for entry in defMacros:
        if entry not in macroNames:
            macroNames.append(entry)
        else:
            print(errorsConf['macroNames']['message'], entry)


def xsdValidation():
    """
    """

    print('Validating transfer file against transfer.xsd')

    temp = open('transfer.xsd', 'r')
    xsd = ET.parse(temp)
    xmlSchema = ET.XMLSchema(xsd)

    doc = ET.parse(fName)

    print(xmlSchema.assertValid(doc))


def unusedDefCats():
    """
    There are certain redundant def-cats that maybe
    present in the transfer rules definition but are
    never actually used. This function is responsible
    for detecting and reporting such unused def-cats
    """

    print('Checking for unused def-cats')

    patternItemHash = []

    for entry in rules:
        for iterator in rules[entry]:
            if 'pattern-item' in iterator:
                patternList = iterator[1]
                for pattern in patternList:
                    patternItemHash.append(pattern)

    hashSet = set(patternItemHash)

    hashDefCats = []
    for entry in defCats:
        hashDefCats.append(entry)

    hashCatsSet = set(hashDefCats)

    difference = hashCatsSet - hashSet

    print(errorsConf['unusedDefCats']['message'], difference)


def checkValidPartClip():
    """
    In transfer files, one common error is calling,
    for instance in <clip> an attribute in part="" that does not exist.
    This function is responsible for handling that very issue.
    """

    print('Checking for the validity of the part in the clip tag')

    tmpList = []
    for entry in defAttrs:
        tmpList.append(entry)

    validParts = ['whole', 'lem', 'lemh', 'lemq', 'tags']

    for x in validParts:
        tmpList.append(x)

    validParts = list(set(tmpList))

    for entry in rules:
        for attribs in rules[entry]:
            if 'clip' in attribs:
                part = attribs[1]['part']
                if part not in validParts:
                    print(errorsConf['checkValidPartClip']
                          ['message'] % (entry, part))

    for entry in defMacros:
        for attribs in defMacros[entry]:
            if 'clip' in attribs:
                part = attribs[1]['part']
                if part not in validParts:
                    print(errorsConf['checkValidPartClip']
                          ['message'] % (entry, part))


def compareClipLit(element):
    """
    """
    part, v = None, None
    for child in element:
        if child.tag == 'clip':
            part = child.attrib['part']
        if child.tag == 'lit':
            v = child.attrib['v']
        if v is None and child.tag == 'lit-tag':
            v = child.attrib['v']

    return (part, v)


def checkValidEqualTag():
    """
    In transfer files, a common error is trying
    to compare an attribute to a value it cannot take,
    such as using,

    <equal><clip pos="1" side="tl" part="a_nom"/><lit-tag v="n.acr"/></equal>

    when the definition of attribute a_nom matches only
    "n" and "np" in attr-item definitions.
    """

    print('Checking if <equal> tags are valid or not')
    print('Checking in <section-rules>')

    undetectedKeys = []
    sectionPath = './section-rules'

    for section in tree.findall(sectionPath):
        for rule in section:
            for tags in rule.iter():
                element = tags.tag
                if element == 'equal':
                    validationTuple = compareClipLit(tags)
                    if None in validationTuple:
                        continue
                    try:
                        if (validationTuple[1] not in
                                defAttrs[validationTuple[0]]):
                            print(errorsConf['checkValidEqualTag']['message'],
                                  validationTuple, ' line number : ',
                                  tags.sourceline)
                    except KeyError:
                        undetectedKeys.append(validationTuple[0])

    sectionPath = './section-def-macros'
    print('Checking in <section-macros>')
    for section in tree.findall(sectionPath):
        for defMacro in section:
            for tags in defMacro.iter():
                element = tags.tag
                if element == 'equal':
                    validationTuple = compareClipLit(tags)
                    if None in validationTuple:
                        continue
                    try:
                        if (validationTuple[1] not in
                                defAttrs[validationTuple[0]]):
                            print(errorsConf['checkValidEqualTag']
                                  ['message'], validationTuple,
                                  ' line number : ', tags.sourceline)
                    except KeyError:
                        undetectedKeys.append(validationTuple[0])

    undetectedKeys = set(undetectedKeys)
    for x in undetectedKeys:
        print('Key : \"', x, '\" Not found and hence could not be compared')


def parseDefCats(tree):
    """
    """

    defCats = {}
    sectionPath = './section-def-cats'

    for defCat in tree.findall(sectionPath):
        for child in defCat:
            catList = []
            try:
                tag = child.attrib['n']
            except KeyError:
                continue
            for catItem in child.findall('./cat-item'):
                itemList = []

                try:
                    lemma = catItem.attrib['lemma']
                except KeyError:
                    lemma = None

                tags = catItem.attrib['tags']
                itemList.append(lemma)
                itemList.append(tags)
                catList.append(itemList)
            defCats[tag] = catList

    return defCats


def parseDefAttrs(tree):
    """
    """

    defAttrs = {}
    sectionPath = './section-def-attrs'

    for defAttr in tree.findall(sectionPath):
        for child in defAttr:
            tagList = []
            tag = child.attrib['n']
            for attrItem in child.findall('./attr-item'):
                tags = attrItem.attrib['tags']
                tagList.append(tags)
            defAttrs[tag] = tagList
    return defAttrs


def parseDefVars(tree):
    """
    """

    defVars = []
    sectionPath = './section-def-vars'

    for defVar in tree.findall(sectionPath):
        for child in defVar.findall('def-var'):
            defVars.append(child.attrib['n'])

    return defVars


def parseDefLists(tree):
    """
    """

    defLists = {}
    sectionPath = './section-def-lists'

    for defList in tree.findall(sectionPath):
        for child in defList:
            n = child.attrib['n']
            vList = []
            for listItem in child.findall('list-item'):
                tag = listItem.attrib['v']
                vList.append(tag)
            defLists[n] = vList

    return defLists


def parseMacros(tree):
    """
    """

    macros = {}
    sectionPath = './section-def-macros'

    for section in tree.findall(sectionPath):
        for defMacro in section:
            try:
                macroHead = defMacro.attrib['n']
            except KeyError:
                continue
            nPar = defMacro.attrib['npar']
            macroHead = macroHead + ' ' + nPar
            macroDict = []
            for tags in defMacro.iter():
                element = tags.tag
                elementAttrib = tags.attrib
                elementTuple = (element, elementAttrib)
                macroDict.append(elementTuple)
            macros[macroHead] = macroDict

    return macros


def parseRules(tree):
    """
    """

    rules = OrderedDict()
    sectionPath = './section-rules'

    for section in tree.findall(sectionPath):
        for rule in section:
            try:
                comment = rule.attrib['comment']
            except KeyError:
                continue
            patternList = []
            ruleDict = []
            for tags in rule.iter():
                element = tags.tag
                if element == 'pattern-item':
                    patternList.append(tags.attrib['n'])
                    continue
                elif element == 'action':
                    ruleDict.append(('pattern-item', patternList))
                    elementAttrib = tags.attrib
                else:
                    elementAttrib = tags.attrib
                ruleDict.append((element, elementAttrib))
            rules[comment] = ruleDict

    # This is how we plan to iterate over the rules
    # for m in rules :
    #   print (m)
    #   for x in rules[m]:
    #       if "call-macro" in x:
    #           print (x)

    return rules


def TransferErrors(errorsConf):
    """
    Takes care of errors
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
    Main function, handles the lint's workflow
    """
    global errorsConf, tree, fName, args
    args = arg_list

    errorsConf = readConfig()
    fName = args.filename

    global defCats, defAttrs, defVars, defLists, defMacros, rules

    tree = ET.parse(fName)

    defCats = parseDefCats(tree)
    defAttrs = parseDefAttrs(tree)
    defVars = parseDefVars(tree)
    defLists = parseDefLists(tree)
    defMacros = parseMacros(tree)
    rules = parseRules(tree)

    # print(defMacros)

    # for x in rules["REGLA: ADV ADJ TO INF ENC (BCN: canviem la prep TO per
    #                                            DE; els adjectius que no
    #                                            compleixin la regla s'han
    #                                            de codificar al lèxic.
    #                                            Queda com a GD i ND fins al
    #                                            interchunk)"]:
    #   print (x)

    TransferErrors(errorsConf)


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='apertium_lint')

    argparser.add_argument('-c', '--config', action='store',
                           help='Configuration file for apertium-lint',
                           default='config.json')
    argparser.add_argument('filename', action='store', help='File to be linted')

    args = argparser.parse_args()
    sys.exit(main(args))
