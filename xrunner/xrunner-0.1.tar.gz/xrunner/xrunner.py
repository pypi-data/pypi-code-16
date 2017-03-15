'''
XMLTest is a small utility written to test XML responses returned by resful
APIs. It uses yaml file to load tests and executes them.
'''

import argparse
import logging
import sys
import os.path
from parser import Parser

log = logging.getLogger("XMLTestLogger")
log.addHandler(logging.StreamHandler(sys.stdout))


def __get_command_line_args__():
    cli_parser = argparse.ArgumentParser(
        description='XMLTest is a small utility written to test XML responses \
        returned by restful APIs. It has been built to be used in place of \
        pyresttest for xml responses. Test cases are loaded from YAML file \
        and the utility executes them.'
    )

    cli_parser.add_argument("file", metavar='file', type=str,
                            help='Test set file')
    cli_parser.add_argument("api", metavar='api', type=str,
                            help='API to execute the test cases on')

    cli_parser.add_argument("--log", type=str, default="INFO",
                            help='Logging Level - (INFO, DEBUG)')

    return cli_parser.parse_args()


def execute_from_command_line():
    # Read Command Line Arguments.
    args = __get_command_line_args__()

    # Set logging level
    if args.log != "INFO" and args.log != "DEBUG":
        print "Invalid Logging Level"
        sys.exit(1)
    # Set Log with formatter
    if args.log == "INFO":
        log.setLevel(logging.INFO)
    if args.log == "DEBUG":
        log.setLevel(logging.DEBUG)

    # Validate if file exists
    if not os.path.isfile(args.file):
        log.error("File Not Found.")
        sys.exit(1)

    # Lets Parse the file
    parser = Parser(args.file, args.api)
    tests = parser.get_tests()
    counter = 0
    try:
        for test in tests:
            log.debug("------------------------------------------------------")
            log.debug("Running Test: " + test.name)
            log.debug("------------------------------------------------------")
            try:
                test.run()
                counter = counter + 1
            except Exception as ex:
                print "Failed: " + test.name  + "  due to: "+ ex.message
            log.debug("\n------------------------------------------------------")
            continue
    except Exception as ex:
        print "Passed: " + str(counter) + "/" + str(len(tests))
        print ex.message
        sys.exit(9)

    print "Passed: " + str(counter) + "/" + str(len(tests))
    sys.exit(0)
