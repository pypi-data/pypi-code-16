# coding=utf-8
# -*- encoding: utf-8 -*-

import json
import sys
from lxml import etree as ET
from lxml.etree import tostring
from itertools import chain
import argparse


def readConfig():
    with open(args.config) as dataFile:
        data = json.load(dataFile)
        return data['tagger']


def stringify_children(node):
    text = ([node.text]+list(chain(*([tostring(child).decode('utf-8')]
                                     for child in node.getchildren()))))
    return text


def getLineNumber(pattern):
    with open(fName) as curFile:
        for num, line in enumerate(curFile, 1):
            if pattern in line:
                return num


def defLabelClosed():
    print("Checking validity of the 'closed' attribute in def-label")

    valid = ['true', 'false']

    for entry in tagsetData:
        closedVal = tagsetData[entry]['closed']
        if closedVal not in valid:
            print(errorsConf['defLabelClosed']['message'], entry, closedVal)


def validateLabelSequence():
    print('Validating label sequence')

    for entry in forbidSequences:
        if entry:
            label1 = entry[0]
            label2 = entry[1]

            if label1 not in tagsetData:
                print(errorsConf['validateLabelSequence']['message'] % (label1))

            if label2 not in tagsetData:
                print(errorsConf['validateLabelSequence']['message'] % (label2))


def parseLabels():

    tagsetPath = './/tagset'
    forbidPath = './/forbid'
    rulesPath = './/enforce-rules'

    for tagset in tree.findall(tagsetPath):
        for label in tagset.iterchildren():
            if label.tag == 'def-label':  # Singular labels
                labelDict = {}
                try:
                    labelName = label.attrib['name']
                except KeyError:
                    labelName = None

                try:
                    labelClosed = label.attrib['closed']
                except KeyError:
                    labelClosed = 'false'

                tagList = []

                for tagsItem in label.iterchildren():

                    try:
                        lemma = tagsItem.attrib['lemma']
                    except KeyError:
                        lemma = None

                    try:
                        tags = tagsItem.attrib['tags']
                    except KeyError:
                        tags = None

                    tagList.append((lemma, tags))

                labelDict['name'] = labelName
                labelDict['closed'] = labelClosed
                labelDict['tagsItem'] = tagList

                tagsetData[labelName] = labelDict

            if label.tag == 'def-mult':
                labelDict = {}
                try:
                    labelName = label.attrib['name']
                except KeyError:
                    labelName = None

                try:
                    labelClosed = label.attrib['closed']
                except KeyError:
                    labelClosed = False

                tagList1, tagList2 = [], []

                for sequence in label.iterchildren():
                    for tagsItem in sequence.iterchildren():

                        if tagsItem.tag == 'tags-item':
                            try:
                                lemma = tagsItem.attrib['lemma']
                            except KeyError:
                                lemma = None
                            try:
                                tags = tagsItem.attrib['tags']
                            except KeyError:
                                tags = Non

                        if tagsItem.tag == 'label-item':
                            try:
                                label = tagsItem.attrib['label']
                            except KeyError:
                                label = None

                        tagList1.append((lemma, tags))
                        tagList2.append(label)

                labelDict['name'] = labelName
                labelDict['closed'] = labelClosed
                labelDict['label-item'] = tagList2
                labelDict['tags-item'] = tagList1

                multTagset[labelName] = labelDict

        for forbid in tree.findall(forbidPath):
            for labelSequences in forbid.iterchildren():
                labelItemList = []
                for labelItems in labelSequences.iterchildren():
                    try:
                        labelItemList.append(labelItems.attrib['label'])
                    except KeyError:
                        continue
                forbidSequences.append(labelItemList)

        for rules in tree.findall(rulesPath):
            enforceDict = {}
            for enforceAfter in rules.iterchildren():
                if enforceAfter.tag != 'enforce-after':  # Skips comments
                    continue
                enforceAfterLabel = enforceAfter.attrib['label']
                for labelset in enforceAfter.iterchildren():
                    labelList = []
                    for label in labelset.iterchildren():
                        if label.tag == 'label-item':
                            labelList.append(label.attrib['label'])
                    enforceDict[enforceAfterLabel] = labelList
            rulesList.append(enforceDict)

        # print(rulesList)

    # for x in tagsetData:
    #   print(x)
    #   print(tagsetData[x])


def taggerErrors(errorsConf):
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

    global tagsetData, forbidSequences, multTagset, rulesList

    tagsetData, forbidSequences, multTagset, rulesList = {}, [], {}, []

    errorsConf = readConfig()
    fName = args.filename

    tree = ET.parse(fName)

    parseLabels()
    taggerErrors(errorsConf)


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='apertium_lint')

    argparser.add_argument('-c', '--config', action='store',
                           help='Configuration file for apertium-lint',
                           default='config.json')
    argparser.add_argument('filename', action='store', help='File to be linted')

    args = argparser.parse_args()
    sys.exit(main(args))
