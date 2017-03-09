#!/usr/bin/python3
# coding=utf-8
# -*- encoding: utf-8 -*-

import json
import os
import re
import argparse
from apertium_lint import dict_lint
from apertium_lint import bidix_lint
from apertium_lint import transfer_lint
from apertium_lint import modes_lint
from apertium_lint import tagger_lint


def readConfig():
    try:
        config = open(args.config)

        try:
            json.load(config)
        except ValueError:
            print('Error :  Config file does not contain valid JSON')
            print('Please validate and try again')
            exit(1)

    except FileNotFoundError:
        print('File not found : Configuration file not found')
        print('Please use a valid config file and try again')
        exit(1)

    print('Valid configuration file loaded succesfully')


def parseFile(fName, fPath):
    """
    Given the filename determines what
    kind file we are working with.
    """

    # Dictionaries
    for x in range(2):
        for y in range(2):

            match = re.search(
                'apertium-[a-z]{' + str(x+2) + '}-[a-z]{' + str(y+2)
                + '}\.[a-z]{' + str(y+2) + '}\.dix', fName)
            if match is not None and os.path.isfile(fPath):
                print('Working with monodix : ' + fName)
                return 'monodix'

            match = re.search(
                'apertium-[a-z]{' + str(x+2)+'}\.[a-z]{' + str(y+2)
                + '}\.dix', fName)
            if match is not None and os.path.isfile(fPath):
                print('Working with monodix : ' + fName)
                return 'monodix'

            match = re.search(
                'apertium-[a-z]{' + str(x+2) + '}-[a-z]{'
                + str(y+2) + '}\.[a-z]{' + str(x+2) + '}-[a-z]{'
                + str(y+2) + '}\.dix', fName)
            if match is not None and os.path.isfile(fPath):
                print('Working with bidix : ' + fName)
                return 'bidix'

    # Transfer files
    match = re.search('apertium.*\.t[0-3]x', fName)
    if match is not None and os.path.isfile(fPath):
        print('Working with transfer file : ' + fName)
        return 'transfer'

    # Modes files
    match = re.search('modes.xml', fName)
    if match is not None and os.path.isfile(fPath):
        print('Working with modes file : ' + fName)
        return 'modes'

    # Tagger files
    match = re.search('apertium.*\.tsx', fName)
    if match is not None and os.path.isfile(fPath):
        print('Working with tagger file : ' + fName)
        return 'tagger'

    print('Invalid file')
    exit(1)


def main():
    '""Parse the arguments using argparse package""'
    argparser = argparse.ArgumentParser(description='apertium_lint')

    argparser.add_argument('-c', '--config', action='store',
                           help='Configuration file for apertium-lint',
                           default='config.json')
    argparser.add_argument('filename', action='store', help='File to be linted')

    global args
    args = argparser.parse_args()
    categories = {'monodix': 'dict_lint', 'bidix': 'bidix_lint',
                  'transfer': 'transfer_lint', 'modes': 'modes_lint',
                  'tagger': 'tagger_lint'}
    fName = args.filename
    fName = fName.strip()
    fType = parseFile(fName.split('/')[-1], fName)
    readConfig()

    if fType == 'monodix':
        dict_lint.main(args)

    elif fType == 'bidix':
        bidix_lint.main(args)

    elif fType == 'transfer':
        transfer_lint.main(args)

    elif fType == 'modes':
        modes_lint.main(args)

    elif fType == 'tagger':
        tagger_lint.main(args)

    else:
        print('Support coming in soon')

    # Can do a subprocess call here or work on the individual files


if __name__ == '__main__':
    main()
