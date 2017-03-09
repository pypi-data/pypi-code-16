#!/usr/bin/python3
# coding=utf-8
# -*- encoding: utf-8 -*-

import json
import sys
import re
from lxml import etree as ET
from lxml.etree import tostring
from itertools import chain
import argparse


def readConfig():
    with open(args.config) as dataFile:
        data = json.load(dataFile)
        return data['monodix']


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


def nonesorter(a):
    if not a:
        return ''
    return a


def genearateActualEntry(entry):
    children = stringify_children(entry)
    content = children[1]
    return content


def listDuplicates(seq):
    seen = set()
    seen_add = seen.add
    # adds all elements it doesn't know yet to seen and all other to seen_twice
    seen_twice = set(x for x in seq if x in seen or seen_add(x))
    # turn the set into a list (as requested)
    return list(seen_twice)


def decideList(lists, arg1, arg2):
    seq1 = listDuplicates(lists[arg1])
    seq2 = listDuplicates(lists[arg2])
    if seq1:
        print(seq1)
    else:
        print(seq2)


def cleanTagText(children):
    concat = []
    for child in children:
        if child is not None and '<s n=' not in child:
            concat.append(child)

    tagText = ''
    for strings in concat:
        tagText = tagText + strings

    return tagText


def redundantPardef():
    """
    Searches and reports redundant pardefs like
    <pardef n="tip__vblex"><e><par n="step__vblex"/></e></pardef>
    """
    print('Checking for redundant pardef entries')
    for entry in paradigms:
        for lists in (paradigms[entry]):
            if len(lists) == 2 and len(paradigms[entry]) == 1:
                try:
                    if lists[1][0] in paradigms:
                        print(errorsConf['redundantPardef']['message'], entry)
                        format = 'pardef n=\"'+entry+'\">'
                        print('Issue found on line :', getLineNumber(format))
                except IndexError:
                    pass


def paradigmNames():  # Still to be made better
    """
    Finds paradigm names and makes sure they follow
    a specific format
    """
    print('Checking paradigm names for issues')
    pattern = '^([a-zA-Z]*[\/]?)[a-zA-Z]*[_]?[\/]?([a-zA-Z\-]*(_{2})?[a-zA-Z]+)*$'
    for entry in paradigms:
        match = re.search(pattern, entry)
        if match is None:
            print(errorsConf['paradigmNames']['message'], entry)
            format = 'pardef n=\"'+entry+'\">'
            print('Issue found on line :', getLineNumber(format))


def rTagData():
    """
    Checks for consistency in the data in the
    <r> tags in pardef enrties
    """
    print('Checking the data in <r> tags')
    for entry in paradigms:
        prev, cur = None, None
        for lists in paradigms[entry]:
            cur = prev
            try:
                prev = lists[2]
            except IndexError:
                continue
            if cur is not None:
                if cur != prev:
                    print(errorsConf['rTagData']['message'], entry)
                    format = 'pardef n=\"'+entry+'\">'
                    print('Issue found after the line :', getLineNumber(format))
                    break


def repeatedAttributesPardef():
    """
    Checks for repeated attributes in the <s>
    tag in pardef entries.
    Eg : <s n="vblex"/><s n="vblex"/><s n="inf"/>
    """
    print('Checking for repeated attributes in pardefs')
    for entry in paradigms:
        for lists in paradigms[entry]:
            try:
                for independentSTags in lists[3]:
                    if len(set(independentSTags)) != len(independentSTags):
                        print(errorsConf['repeatedAttributesPardef'][
                              'message'], entry)
                        format = 'pardef n=\"'+entry+'\">'
                        print('Issue found after the line :',
                              getLineNumber(format))
            except (IndexError, TypeError) as error:
                # Certain lists for unique pardef entries are of length 2
                pass


def repeatedEntriesPardef():
    """
    Currently doing what it needs to but slight improvement
    is required. Changes don't need to be made here, but rather
    in parsing the pardef entries. Remember to change
    parseParadigms() to adapt to <re> and <b/>
    """
    print('Checking for repeated entries in pardefs')
    for entry in paradigms:
        hashTable = []

        for lists in paradigms[entry]:
            try:
                lists[3].sort()
                lists[4].sort()
            except (IndexError, AttributeError) as error:
                pass
            hashTable.append(hash(str(lists)))

        if len(set(hashTable)) != len(hashTable):
            errorLocation = []

            for x, iter1 in zip(hashTable, range(len(hashTable))):
                for y, iter2 in zip(hashTable, range(len(hashTable))):
                    if x == y and iter1 != iter2:
                        errorLocation.append((iter1, iter2))

            print(errorsConf['repeatedEntriesPardef']['message'], entry)
            format = 'pardef n=\"'+entry+'\">'
            print('Issue found after the line :', getLineNumber(format))
            print('Entries : ')
            for position in errorLocation:
                print('Entry Number : ', position[
                      0]+1, 'and', position[1]+1, paradigms[entry][position[0]])


def repeatedEntriesMainSection():
    """
    Checks for repeated entries in the main section
    Eg :
    <e lm="house"><i>house</i><par n="house__n"/></e>
    <e lm="house"><i>house</i><par n="house__n"/></e>
    """
    print('Checking for repeated entries in the main section')

    for entry in singleWordEntries:
        hashTable = []
        for lists in singleWordEntries[entry]:
            lists[-1].sort()
            hashTable.append(hash(str(lists)))
        if len(set(hashTable)) != len(hashTable):
            print(errorsConf['repeatedEntriesMainSection']['message'], entry)
            format = 'lm=\"'+entry+'\"'
            print('Issue found after the line :', getLineNumber(format))

    hashTable = []

    for entry in multiWordEntries:
        hashTable = []
        for lists in multiWordEntries[entry]:
            if len(lists) == 4:
                lists[-1].sort()
                lists[-2].sort()
            else:
                for iterator in range(5):
                    try:
                        sorted(lists[-(iterator+1)],
                               key=lambda x: (x is None, x))
                    except (TypeError, IndexError):
                        pass
            hashTable.append(hash(str(lists)))
        if len(set(hashTable)) != len(hashTable):
            print(errorsConf['repeatedEntriesMainSection']['message'], entry)
            format = 'lm=\"'+entry+'\"'
            print('Issue found after the line :', getLineNumber(format))


def repeatedTagEntries():
    """
    Checking for repeated <par n="xyz"> entries
    and repeated <s n="xyz> entries for single
    and multi word entries in the main section
    """
    print('Checking for repeated tag entries')

    for entry in multiWordEntries:
        for lists in multiWordEntries[entry]:
            if len(lists) == 4:
                if len(set(lists[-1])) != len(lists[-1]):
                    print(errorsConf['repeatedTagEntries']['message'], entry)
                    print(listDuplicates(lists[-1]))

            if len(lists) == 8:
                if (len(set(lists[-1])) != len(lists[-1]) and
                        len(set(lists[-3])) != len(lists[-1])):
                    print(errorsConf['repeatedTagEntries']['message'], entry)
                    decideList(lists, -1, -3)

    for entry in singleWordEntries:
        for lists in singleWordEntries[entry]:
            if len(lists) == 4:
                if len(set(lists[-1])) != len(lists[-1]):
                    print(errorsConf['repeatedTagEntries']['message'], entry)
                    print(listDuplicates(lists[-1]))

            if(len(lists) == 6):
                if (len(set(lists[-1])) != len(lists[-1]) and
                        len(set(lists[-2])) != len(lists[-2])):
                    print(errorsConf['repeatedTagEntries']['message'], entry)
                    decideList(lists, -1, -2)

            if(len(lists) == 8):
                if (len(set(lists[-1])) != len(lists[-1]) and
                        len(set(lists[-3])) != len(lists[-3])):
                    print(errorsConf['repeatedTagEntries']['message'], entry)
                    decideList(lists, -1. - 3)


def transferDirection():
    """
    As the name says, the function is responsible
    for checking the direction of trasnfer.
    It can either be
    *left->right
    *right->left
    *None
    Any other transfer direction is unacceptable
    """
    print('Checking for transfer direcion')

    validDirection = ['LR', 'RL', None]

    # SingleWordEntries
    for entry in singleWordEntries:
        for lists in singleWordEntries[entry]:
            if lists[1] not in validDirection:
                print('Issue found in the main section')
                print(errorsConf['transferDirection']
                      ['message'], lists[1], entry)

    for entry in multiWordEntries:
        for lists in multiWordEntries[entry]:
            if lists[1] not in validDirection:
                print('Issue found in the main section')
                print(errorsConf['transferDirection']
                      ['message'], lists[1], entry)

    for entry in paradigms:
        for lists in paradigms[entry]:
            if lists[0] not in validDirection:
                print('Issue found in the pardefs')
                print(errorsConf['transferDirection']
                      ['message'], lists[0], entry)


def unusedParadigms():
    """
    This function is responsible for checking any
    paradgms that have been defined but have not been
    used for any entry in the main section.
    """
    print('Checking for unused paradigms')

    hashTableEntries = []
    hashTableParadigms = []

    for entry in singleWordEntries:
        for lists in singleWordEntries[entry]:
            for pars in lists[-1]:
                if pars not in hashTableEntries:
                    hashTableEntries.append(pars)

    for entry in multiWordEntries:
        for lists in multiWordEntries[entry]:
            for pars in lists[-1]:
                hash(pars)
                if pars not in hashTableEntries:
                    hashTableEntries.append(pars)

    for entry in paradigms:
        hashTableParadigms.append(entry)

    print('Total paradigms used :', len(hashTableEntries))
    print('Total paradigms defined :', len(hashTableParadigms))

    unusedPars = list(set(hashTableParadigms) - set(hashTableEntries))

    if unusedPars:
        print(errorsConf['unusedParadigms']['message'])
        print(unusedPars)


def blankSpaceDetection():
    """
    This function is responsible for detecting blank spaces
    in entries in the main section. Other than in the lemma
    everywhere else, the blank spaces are to be denoted using a
    <b/> tag. This function enforces that.
    """
    print('Detecing black spaces in entries now')

    for entry in multiWordEntries:
        for lists in multiWordEntries[entry]:
            try:
                for textEntry in filter(lambda textEntry: ' ' in textEntry,
                                        lists[2]):
                    print('Space found in <i> tag text for entry : ', entry)
            except TypeError:
                pass
            if len(lists) > 4:
                for textEntry in lists[3]:
                    try:
                        if ' ' in textEntry:
                            print('Space found in <l> tag text for entry : ',
                                  entry)
                    except TypeError:
                        pass
                for textEntry in lists[4]:
                    try:
                        if ' ' in textEntry:
                            print('Space found in <r> tag text for entry : ',
                                  entry)
                    except TypeError:
                        pass

    for entry in singleWordEntries:
        for lists in singleWordEntries[entry]:
            if len(lists) == 4:
                try:
                    if ' ' in lists[2]:
                        print('Space found in <i> tag text for entry : ', entry)
                except TypeError:
                    pass
            if len(lists) == 6 or len(lists) == 8:
                try:
                    if ' ' in lists[3]:
                        print('Space found in <l> tag text for entry : ', entry)
                except TypeError:
                    pass
                try:
                    if ' ' in lists[4]:
                        print('Space found in <r> tag text for entry : ', entry)
                except TypeError:
                    pass


def partiallyInLemma():
    """
    Ah, this is an interesting one.
    Full lemmas in entries where part of the lemma is specified by the pardef
    One common error when you have a pardef that defines part of the
    lemma, is to write that part twice (once in the pardef,
    once in the entry using the pardef), e.g.

    <pardef n="enk/e__n">
     <e><p><l>a</l> <r>e<s n="n"/><s n="f"/><s n="sg"/><s n="def"/></r></p></e>
     <e><p><l>e</l> <r>e<s n="n"/><s n="f"/><s n="sg"/><s n="ind"/></r></p></e>
     …
    </pardef>
    …
    <e lm="slette"><i>slette</i><par n="enk/e__n"></e>
    Here the correct entry should be

    <e lm="slette"><i>slett</i><par n="enk/e__n"></e>

    This function points out any such issues.
    """
    print('Checking for another issue')
    for entry in singleWordEntries:
        for lists in singleWordEntries[entry]:
            lists[0]
            parList = lists[-1]
            splitPars = []
            replaceableParts = []

            for pars in parList:
                temp = pars.split('/')  # Splitting paradigm at "/"
                if len(temp) != 1:  # Successfully split
                    # Store list of endings of split pars
                    splitPars.append(temp[1])

            for parts in splitPars:
                temp = parts.split('__')
                if len(temp) != 0:
                    replaceableParts.append(temp[0])

            # Re-iterate if no part to be split or added
            if len(replaceableParts) == 0:
                continue

            if len(lists) == 4:
                text = lists[2]
                for part in replaceableParts:
                    if part == '' or text is None:
                        continue
                    partLen = len(part)
                    toMatch = text[-partLen:]
                    check = lists[0][-(partLen+partLen): -partLen]
                    if toMatch == part and check != toMatch:
                        print(errorsConf['partiallyInLemma']['message'], entry)


def unwantedTag():
    """
    Under construction. Single word entries is still giving
    some problem. Will tackle soon.
    This is repsonsible for checking unwanted <b/>
    tags that might be present in the beginning or the
    end of the entries and are repeated anywhere in the middle
    """
    print('Checking for unwanted <b/> tags')
    for entry in multiWordEntries:
        for lists in multiWordEntries[entry]:
            if len(lists) == 4:
                splitText = lists[2]
                for text in splitText:
                    if text == '<b/>':
                        print(errorsConf['unwantedTag']['message'], entry)
            if len(lists) == 8:
                iText = lists[2]
                lText = lists[3]
                rText = lists[4]

                for text in iText:
                    if text == '<b/>':
                        print(errorsConf['unwantedTag']['message'], entry)

                for text in lText:
                    if text == '<b/>':
                        print(errorsConf['unwantedTag']['message'], entry)

                for text in rText:
                    if text is None:
                        continue

                    if '<g>' in text:
                        tmp1 = text.split('<g>')[1]
                        tmp2 = tmp1.split('<g/>')[0]
                        splitText = tmp2.split('<b/>')

                        for iterator in splitText:
                            if iterator == '<b/>':
                                print(errorsConf['unwantedTag']
                                      ['message'], entry)

                    else:
                        if text == '<b/>':
                            print(errorsConf['unwantedTag']['message'], entry)


def singleWordMainSection(tree):  # Could do with a better name
    """
    This function is responsible for taking
    an XML tree as an input and returning a
    dictionary containing single word entries
    in the main section.
    """

    singleWordEntries = {}
    sectionPath = './/e'
    i_path = './i'
    l_path = './/l'
    r_path = './/r'
    par_path = './par'

    for entry in tree.findall(sectionPath):
        tmpList = []
        tmpList2 = []
        lemma = None

        try:  # Certain entries do not have the lm attribute
            lemma = entry.attrib['lm']
            if ' ' in lemma:  # Ensures that only single word lemmas are parsed
                continue
        except KeyError:
            continue

        try:
            # This detects if there are repeated entries for one lemma
            if(singleWordEntries[lemma]):
                pass
        except KeyError:
            # If entry not already present initiliaze here
            singleWordEntries[lemma] = []

        tmpList.append(lemma)

        try:  # Enters the attribute present at r in <e r="??">
            tmpList.append(entry.attrib['r'])
        except KeyError:
            tmpList.append(None)

        # Finds the text in the <i> tag and appends that
        for i in entry.findall(i_path):
            tmpList.append(i.text)

        # Certain Monodix entries are of the type : <e r="LR"
        # lm="bibliographical"><p><l>bibliographical</l><r>bibliographic</r></p>
        # <par n="expensive__adj"/></e>
        for ls in entry.findall(l_path):
            # This takes care of adding the text content present in the <l> tag
            tmpList.append(ls.text)

        # This takes care of adding the text content in the <r> tag
        for rs in entry.findall(r_path):
            tmpList.append(rs.text)
            tmpList2 = []

            # This is to handle the <j/> tags like : <r>prperss n="p2"/><s
            # n="mf"/><s n="sp"/><j/>have<s n="vbhaver"/><s n="past"/>
            for s in rs.findall('./s'):
                tmpList2.append(s.attrib['n'])
            tmpList.append(tmpList2)

            x = stringify_children(rs)
            try:
                for a in x:
                    if '<j/>' in a:
                        tmpList.append(a)
            except:
                tmpList.append(None)

        tmpList2 = []
        # tmpList2 consists of a list of all the paradigms associated
        # with a given entry
        for pars in entry.findall(par_path):
            tmpList2.append(pars.attrib['n'])
        tmpList.append(tmpList2)

        # Entries in the dictionary are of the type, "lemma":[<feature list>]
        singleWordEntries[lemma].append(tmpList)

    print('Single word entries loaded')
    return singleWordEntries
    # Returns the dictionary of single word entries in the monodix


def multiWordMainSection(tree):
    """
    This function is similar to the
    singleWordEntries() function. It
    has been designed to understand multi-word
    entries in the dictionary and parse
    the content of the nested tags

    The manner in which the data is parsed
    varies fairly (3 kinds) depending on the
    kind of entry in the monodix. For futher
    information on how the data is organized in
    the lists, have a look at :
    multi-word-format.txt
    """

    sectionPath = './/e'
    multiWordEntries = {}

    i_path = './i'
    l_path = './/l'
    r_path = './/r'
    par_path = './par'

    for entry in tree.findall(sectionPath):
        tmpList = []
        tmpList2 = []
        lemma = None

        try:
            lemma = entry.attrib['lm']
            # This prevents any single word entries from creeping in.
            if lemma is None or ' ' not in lemma:
                continue
            try:
                # This detects if there are repeated entries for one lemma
                if(multiWordEntries[lemma]):
                    pass
            except KeyError:
                # If entry not already present initiliaze here
                multiWordEntries[lemma] = []
        except KeyError:
            if lemma is None:
                continue

        tmpList.append(lemma)
        try:
            tmpList.append(entry.attrib['r'])
        except KeyError:
            tmpList.append(None)

        for i in entry.findall(i_path):
            # Here instead of extract just the text from the tags, we pull out
            # the entire content as there might be possible bugs present there
            tmpList.append(stringify_children(i))

        for ls in entry.findall(l_path):
            tmpList.append(stringify_children(ls))

        for rs in entry.findall(r_path):
            try:
                rText = rs.text
            except TypeError:
                rText = None

            childList = stringify_children(rs)

            gText = None
            for iterator in childList:
                # takes care of text enclosed <g>, usually just one entry
                if iterator is not None:
                    if '<g>' in iterator:
                        gText = iterator

            tmpList.append([rText, gText])

            # This is to handle the <j/> tags like : <r>prperss n="p2"/><s
            # n="mf"/><s n="sp"/><j/>have<s n="vbhaver"/><s n="past"/>
            for s in rs.findall('./s'):
                tmpList2.append(s.attrib['n'])

            tmpList.append(tmpList2)

            jAttrList = []
            for jTagData in childList:
                if jTagData is not None:
                    if '<j/>' in jTagData:
                        jAttrList.append(jTagData)

            tmpList.append(jAttrList)

        tmpList2 = []
        for pars in entry.findall(par_path):
            tmpList2.append(pars.attrib['n'])
        tmpList.append(tmpList2)

        # Entries in the dictionary are of the type, "lemma":[<feature list>]
        multiWordEntries[lemma].append(tmpList)

    print('Multi word entries loaded')
    return multiWordEntries


def parseParadigms(tree):
    """
    When sent the XML tree, it returns
    a dictionary of the paradigms.

    Assumption : There is only a single <j/>
    in any entry.
    """

    paradigms = {}
    paradigmPath = './/pardef'
    e_path = './e'
    i_path = './i'
    l_path = './/l'
    r_path = './/r'
    s_path = './s'
    re_path = './re'
    par_path = './par'

    for paradigm in tree.findall(paradigmPath):
        name = paradigm.attrib['n']
        paradigms[name] = []

        for es in paradigm.findall(e_path):
            tmpList = []
            try:
                tmpList.append(es.attrib['r'])
            except KeyError:
                tmpList.append(None)

            for i in es.findall(i_path):
                tmpList.append(i.text)

            for ls in es.findall(l_path):
                tmpList.append(cleanTagText(stringify_children(ls)))

            for rs in es.findall(r_path):

                counter, jPos = 0, None
                for tempTag in rs:
                    x = tempTag.tag
                    counter += 1
                    if x == 'j':
                        jPos = counter

                jTagPresent = True if jPos is not None else False
                counter = 0

                rTagText = cleanTagText(stringify_children(rs))
                tmpList2 = []

                if '<j/>' in rTagText:
                    tmpList2 = rTagText.split('<j/>')
                else:
                    tmpList2 = rTagText
                tmpList.append(tmpList2)

                tmpList2 = []  # tmpList 2 consists of all <s> attributes
                tmpList3 = []
                for ss in rs.findall(s_path):
                    counter += 1
                    if jPos == counter and jTagPresent:
                        tmpList2.append(tmpList3)
                        tmpList3 = []
                    tmpList3.append(ss.attrib['n'])

                tmpList2.append(tmpList3)
                tmpList.append(tmpList2)

            tmpList2 = []
            for ps in es.findall(par_path):
                tmpList2.append(ps.attrib['n'])  # tmpList2
            tmpList.append(tmpList2)

            tmpList2 = []
            for re in es.findall(re_path):
                tmpList2.append(re.text)
            tmpList.append(tmpList2)

            try:
                vAttribEntry = es.attrib['v']
                tmpList.append(vAttribEntry)
            except KeyError:  # Incase the v attrib is absent
                pass

            # Entries in the dictionary are of the type, "paradigm":[<feature
            # list>]
            paradigms[name].append(tmpList)

    print('Paradigms loaded')
    return paradigms


def monodixErrors(paradigms, errorsConf):
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
    the dictionary lint's worflow
    """

    global fName, errorsConf

    # Read the config file to select the errors that are to be reported
    errorsConf = readConfig()
    fName = arg1

    # Temporary
    # for errors in errorsConf:
    #   print (errors+" "+"enabled : "+errorsConf[errors]['enable'])

    # for i in range(len(errorsConf)):
    #   errorsConf[str(i+1)]["enable"] == "yes"

    global paradigms, singleWordEntries, multiWordEntries, args
    args = arg_list

    tree = ET.parse(fName)
    paradigms = parseParadigms(tree)
    singleWordEntries = singleWordMainSection(
        tree)  # Could do with a better name
    multiWordEntries = multiWordMainSection(tree)

    monodixErrors(paradigms, errorsConf)

    # debugStatements

    # for entry in paradigms:
    #   print(entry)
    #   for x in paradigms[entry]:
    #       print(x)
    # for entry in multiWordEntries:
    #   print(entry, multiWordEntries[entry])


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='apertium_lint')

    argparser.add_argument('-c', '--config', action='store',
                           help='Configuration file for apertium-lint',
                           default='config.json')
    argparser.add_argument('filename', action='store', help='File to be linted')

    args = argparser.parse_args()
    sys.exit(main(args))
