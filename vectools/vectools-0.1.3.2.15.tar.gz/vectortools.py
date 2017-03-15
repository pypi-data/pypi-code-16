#!/usr/bin/python3.5
# #!/usr/bin/env python
""" Vectortools - A bioinformatics-focused command-line utility for linear algebra, table manipulation,
machine leaning, network graphs, and more.
"""

# For those wishing to modify the Vectortools source code:
# This is the main program used to control Vectortools. It basically starts the argparse and imports lib/__init__.py.
# examples/ - Contains files that can be used for example input.
# features/ - Contains files for integration testing.
# lib/      - Contains the sub-section classes.
# lib/__init__.py - A dictionary mapping function names to their respective classes and functions.
# test/     - Contains files for unit testing.

from __future__ import print_function
import sys
import argparse
import os.path
from signal import signal, SIGPIPE, SIG_DFL

# Ignore SIG_PIPE and don't throw exceptions on it... (http://docs.python.org/library/signal.html)
# Problem with broken pipe error (Errno-32) solved with
# http://newbebweb.blogspot.de/2012/02/python-head-ioerror-errno-32-broken.html
signal(SIGPIPE, SIG_DFL)


def generatehelpstr():
    """ Handles the main help output for Vectortools

    1. The function first checks for a pre-built strings in /tmp as generating the string from scratch takes time.
    2. If pre-build string is not available it iterates over the dictionary in lib/__init__.py
    3. The first line of each doc string is read

    :return: joined_list - A string of possible operations formatted as a help string.
    """

    doc_f = "/tmp/.vectortools_docstring"
    if False:  # (os.path.isfile(doc_f)) and (os.path.getctime(doc_f) > os.path.getctime(__file__)):
            with open(doc_f, 'r') as doc:
                joined_list = doc.read()
    else:
        import lib
        function_dicts = lib.operations_dict
        offset = "    "
        out_list = []
        longest_name = 0

        # Get the longest name to calculate description offset.
        for main_type in function_dicts:
            for operation_name_el in function_dicts[main_type]:
                if len(operation_name_el) > longest_name:
                    longest_name = len(operation_name_el)

        # Build the argparse help strings.
        for main_type in sorted(function_dicts):

            # Main types serve as headings for groups of operations.
            out_list.append(main_type)

            for operation_name_el in sorted(function_dicts[main_type]):

                # Generate the number of spaces we need to
                description_offset = "".join([" " for i in range(longest_name - len(operation_name_el))]) + " -"

                out_list.append("".join([
                    offset,
                    operation_name_el,
                    description_offset,
                    function_dicts[main_type][operation_name_el].__doc__.split("\n")[0]
                ]))

        joined_list = "\n".join(out_list)
        with open(doc_f, "w") as docstring:
            docstring.write(joined_list)

    return joined_list


if len(sys.argv) > 1 and not sys.argv[1] in ("--help", "-help", "-h", "--h", "--commands?"):
    # Run an operation or function.

    # Get the base program name.
    program_name = os.path.basename(sys.argv[0])

    # The name of the operation should be the first argument.
    operation_name = sys.argv[1]

    # Rebase the sys.argv command, pretend the operation is the program that was ran.
    sys.argv = sys.argv[1:]

    # Helps catch cases where the argument supplied does not match the available operations.
    operation_found = False

    import lib
    # Since we organize the data structure by headings, loop through each heading.
    for section_name in lib.operations_dict:
        # Check for the operation name within each heading.
        if operation_name in lib.operations_dict[section_name]:

            # Build the argument parser for the operation.
            parser = argparse.ArgumentParser(
                prog=" ".join((program_name, operation_name)),
                formatter_class=argparse.RawTextHelpFormatter,
                epilog="\n".join(lib.operations_dict[section_name][operation_name].__doc__.split("\n")[1:])
            )

            # Run the operation.
            lib.operations_dict[section_name][operation_name](parser)
            operation_found = True
            break

    if not operation_found:
        sys.stderr.write("function {} not found\n".format(operation_name))

else:
    """
    Handle base help page here. There is probably a better way to do this, but argparse does strange things when
    you call it twice.
    Added --commands? flag to print all available commands in one line
    """

    if len(sys.argv) > 1 and sys.argv[1] == "--commands?":
        # Prints all available functions on a single line separated by spaces.
        ops = "/tmp/.vectortools_opstring"
        if (os.path.isfile(ops)) and (os.path.getctime(ops) > os.path.getctime(__file__)):
            with open(ops, 'r') as doc:
                opstring = doc.read()
        else:

            import lib
            opstring = ""
            for category in lib.operations_dict:
                for operation in lib.operations_dict[category]:
                    opstring += operation
                    opstring += " "
            with open(ops, 'w') as op:
                op.write(opstring)
        print(opstring)
    else:
        parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
        help_str = generatehelpstr()
        parser.add_argument('operation', type=str, nargs=1, help='Operations Available:\n' + help_str)
        parser.print_help()


"""
# Import the operation selector. At this time it is a big elseif list.
# We tried a dict of function names but this takes a long time to load.
from lib.PackageController import operationselector
# Get the function used to preform the operation.
# Returns None if no matching function is found.
operation_function = operationselector(operation_name)

if operation_function is not None:
    # Generate the initial parser for the function, each function may add additional arguments
    # to this.
    parser = argparse.ArgumentParser(
        prog=" ".join((program_name, operation_name)),
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="\n".join(operation_function.__doc__.split("\n")[1:])
    )
    # Run the operation
    operation_function(parser)
else:
    # In the case of a type or non-existing function is found.
    sys.stderr.write("function {} not found\n".format(operation_name))
"""
