#!/usr/bin/env python
import sys
import os
import re

"""
Skim.py

Skim python files and return organized list of classes and functions used.
Indentation used in the original file is preserved:

class Foo(object):
    def __init__(self):
    def dostuff(thing1, thing2):
def bar(arg):
"""

def check_regex(line):
    """Check via regex if line is a class or function definition"""

    match = re.match('^\s*class.*:', line) or re.match('^\s*def.*:', line)
    try:
        return match.group()
    except AttributeError:
        return None

def get_matches(contents):
    """Returns list of class/def line matches for given file"""
    matches = [check_regex(line) for line in contents if check_regex(line)]
    return matches

def read_file_contents(filename):
    """Open and read contents of given file"""

    try:
        with open(filename, 'r') as f:
            content = f.readlines()
    except IOError:
        return
    except EnvironmentError as e:
        raise e

    return content

def process_files(filename):
    """Read file contents, return tuple of
    ([class/def line matches], filename, longest line in matches list)"""

    contents = read_file_contents(filename)
    if not contents:
        return

    matches= get_matches(contents)
    if not matches or not contents:
        return

    return (matches, filename, len(max(matches, key=len)))

def determine_longest_matched_line(results):
    """Results is a list of tuples: (match_list1, 'filename1.py', longest_line_in_match)"""

    if len(results) == 1:
        return results[0][2]
    return max(results, key=lambda x: x[2])[2]

def print_results(results):
    """Prints all class/def line matches to stdout"""

    length = determine_longest_matched_line(results)
    for result in results:
        matches = result[0]
        filename = result[1]

        print(filename.center(length, '-'))
        print
        for line in matches:
            print(line)
        print
        print(filename.center(length, '-'))

def run():
    """Process every file name given in sys.argv[1:]"""

    matches = []
    for arg in sys.argv[1:]:
        matches.append(process_files(arg))
    if not matches:
        return

    results = [match for match in matches if match]

    if results:
        print_results(results)
    else:
        print('No python classes or defintions found in these files.')

if __name__ == '__main__':
    run()

