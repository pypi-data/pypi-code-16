#!/usr/bin/env python
"""  COPYRIGHT (c) 2017 UNIVERSITY OF NEBRASKA NIMBUS LAB - JOHN-PAUL ORE
        PHRIKY-UNITS, THE PHYSICAL UNITS INCONSISTENCY DETECTION TOOL 
"""

from __future__ import print_function
from cps_units_checker import CPSUnitsChecker
from distutils import spawn
from subprocess import Popen
import argparse
import os
import pkg_resources
import re
import sys
from shutil import copyfile



def eprint(*args, **kwargs):
    """ HELPER FUNCTION FUNCTION FOR DEBUG PRINTING
        input: <standard python command line input>
        returns: none.  side effect prints to stdout
    """
    print(*args, file=sys.stderr, **kwargs)


def main(
        ):
    """Console script for phriky_units"""
    # 'Detect physical unit inconsistencies in C++ code, especially ROS code.')

    # PARSE COMMAND LINE ARGS
    parser = argparse.ArgumentParser(description='Apply physical unit inconsistency detection to C++ files for ROS.',
                epilog='Copyright 2017 NIMBUS LAB - University of Nebraska, Lincoln, USA')
    parser.add_argument('target_cpp_file', type=str, help='C++ file to be analyzed.')
    parser.add_argument('--include-dir', type=str, help='Include directory.')
    parser.set_defaults(include_dir='')
    parser.add_argument('--database-analysis-audit-id', type=int, help='Database analysis audit id.')
    parser.set_defaults(database_analysis_audit_id=0)
    parser.add_argument('--current-repository', type=str, help='For Database analysis audit trail - sets the Current repository name')
    # DEBUG PRINT AST
    parser.add_argument('--debug-print-ast', dest='debug_print_ast', action='store_true')
    parser.add_argument('--no-debug-print-ast', dest='debug_print_ast', action='store_false')
    parser.set_defaults(debug_print_ast=False)
    parser.add_argument('--show-high-confidence', dest='show_high_confidence', action='store_true')
    parser.add_argument('--no-show-high-confidence', dest='show_high_confidence', action='store_false')
    parser.set_defaults(show_high_confidence=True)
    # SHOW_LOW_CONFIDENCE    
    parser.add_argument('--show-low-confidence', dest='show_low_confidence', action='store_true')
    parser.add_argument('--no-show-low-confidence', dest='show_low_confidence', action='store_false')
    parser.set_defaults(show_low_confidence=False)
    # USE_VAR_NAME_HEURISTIC    
    parser.add_argument('--use-var-name-heuristic', dest='use_var_name_heuristic', action='store_true')
    parser.add_argument('--no-use-var-name-heuristic', dest='use_var_name_heuristic', action='store_false')
    parser.set_defaults(use_var_name_heuristic=False)
    # CHECK_UNIT_SMELL    
    parser.add_argument('--check-unit-smell', dest='check_unit_smell', action='store_true')
    parser.add_argument('--no-check-unit-smell', dest='check_unit_smell', action='store_false')
    parser.set_defaults(check_unit_smell=False)
    # DELETE_DUMP_FILE    
    parser.add_argument('--delete-dump-file', dest='delete_dump_file', action='store_true')
    parser.add_argument('--no-delete-dump-file', dest='delete_dump_file', action='store_false')
    parser.set_defaults(delete_dump_file=True)
    # USE_EXISTING_DUMP_FILE    
    parser.add_argument('--use-existing-dump-file', dest='use_existing_dump_file', action='store_true')
    parser.add_argument('--no-use-existing-dump-file', dest='use_existing_dump_file', action='store_false')
    parser.set_defaults(use_existing_dump_file=True)
    # ONLY_FIND_FILES_WITH_UNITS    
    parser.add_argument('--only-find-files-with-units', dest='only_find_files_with_units', action='store_true')
    parser.add_argument('--no-only-find-files-with-units', dest='only_find_files_with_units', action='store_false')
    parser.set_defaults(only_find_files_with_units=False)
    # WRITE_RESULTS_TO_DATABASE    
    parser.add_argument('--write-results-to-database', dest='write_results_to_database', action='store_true')
    parser.add_argument('--no-write-results-to-database', dest='write_results_to_database', action='store_false')
    parser.set_defaults(write_results_to_database=False)

    # PARSE COMMAND LINE ARGUMENTS
    args = parser.parse_args()

    # target_cpp_file = args.target_cpp_file
    # include_dir  = args.include_dir 
    # debug_print_ast = args.debug_print_ast
    # show_high_confidence = args.show_high_confidence
    # show_low_confidence = args.show_low_confidence
    # use_var_name_heuristic = args.use_var_name_heuristic
    # check_unit_smell = args.check_unit_smell
    # delete_dump_file = args.delete_dump_file
    # use_existing_dump_file = args.use_existing_dump_file
    # only_find_files_with_units = args.only_find_files_with_units
    # write_results_to_database = args.write_results_to_database
    # database_analysis_audit_id = args.database_analysis_audit_id
    # current_repository = args.current_repository
    
    original_directory = os.getcwd()
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    # TEST FOR CPPCHECK
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

    if not spawn.find_executable('cppcheck'):
        # CPPCHECK NOT GLOBALLY INSTALLED, CHECK BIN DIRECTORY
        if not os.path.exists('bin/cppcheck'):
            eprint( 'Could not find required program Cppcheck') #todo
            eprint( 'two options: ')
            eprint( '  1.  sudo apt-get install cppcheck')  #todo
            eprint( '  2.  brew install cppcheck')  #todo
        sys.exit(1)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    # RUN CPPCHECK
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    # EXTRACT DIR

    if not os.path.exists(args.target_cpp_file):
        eprint( 'file does not exist: %s' % args.target_cpp_file)
        sys.exit(1)

    # print( 'Run cppcheck...'),
    target_cpp_file_dir = os.path.dirname(args.target_cpp_file)
    target_cpp_file  = args.target_cpp_file.replace("//", "/")
    target_cpp_file_base_name = os.path.basename(target_cpp_file)
    dump_filename = os.path.basename(target_cpp_file) + '.dump'

    # CHECK IF DUMP EXISTS, AND IF SO, SHOULD WE USE IT
    if not os.path.exists(target_cpp_file + '.dump' ) or not args.use_existing_dump_file:
        # if not os.path.exists(dump_filename):
            # print("does not exist : %s" % (target_cpp_file + '.dump'))
        # else:
            # print("exists! : %s " % (target_cpp_file + '.dump'))
                
        os.chdir(target_cpp_file_dir)
        # CREATE LOCAL COPY OF CFG
        if pkg_resources.resource_exists('phriky_units', 'resources'):
            if pkg_resources.resource_exists('phriky_units', 'resources/cppcheck'):
                if pkg_resources.resource_exists('phriky_units', 'resources/cppcheck/std.cfg'):
                    if not os.path.exists('cfg'):
                        os.makedirs('cfg')
                    with open('std.cfg', 'w') as f:
                        f.write(pkg_resources.resource_string('phriky_units', 'resources/cppcheck/std.cfg'))
                    os.rename('std.cfg', 'cfg/std.cfg')
        else:
            eprint("resource phriky_units not found: trying local option")
            if not os.path.exists('cfg'):
                os.makedirs('cfg')
            copyfile(os.path.join(original_directory, 'std.cfg'), os.path.join(os.path.join(target_cpp_file_dir, 'cfg'), 'std.cfg'))
        if not os.path.exists(dump_filename):
            args = ['cppcheck', '--dump', '-I ../include', '--suppress="*"', '-q', target_cpp_file_base_name]
            cppcheck_process = Popen(' '.join(args),  shell=True)
            cppcheck_process.communicate()
            if cppcheck_process.returncode != 0:
                eprint( 'cppcheck appears to have failed...exiting with return code %d' % cppcheck_process.returncode)
                sys.exit(1)
            eprint( "Created: %s'" % dump_filename)
        # REMOVE LOCAL COPY OF CFG
        if os.path.exists('cfg/std.cfg'):
            try:
                os.remove('cfg/std.cfg')
                os.rmdir('cfg')
            except:
                # eprint('problem removing cfg folder')
                pass # todo - fail silently for now
         
        # RETURN TO HOME
        os.chdir(original_directory)

    print( 'TARGET: %s' % target_cpp_file )
    cps_unit_checker = CPSUnitsChecker()
    dump_file = os.path.join(os.path.dirname(target_cpp_file), dump_filename)
    source_file = dump_file.replace('.dump','')
    #   APPLY COMMAND LINE CONFIGURATION OPTIONS
    cps_unit_checker.debug_print_AST = args.debug_print_ast
    cps_unit_checker.SHOULD_MATCH_ON_HEURISTIC_VARIABLE_NAMES = args.use_var_name_heuristic
    cps_unit_checker.SHOULD_ONLY_FIND_FILES_WITH_UNITS = args.only_find_files_with_units
    cps_unit_checker.SHOULD_CHECK_UNIT_SMELLS = args.check_unit_smell
    if args.write_results_to_database:
        cps_unit_checker.SHOULD_WRITE_RESULTS_TO_DATABASE = True  # SHOULD BE REDUNDANT
        # ACTUALLY INITIALIZES THE DATABASE CONNECTION 
        cps_unit_checker.init_database_connection()
        # ATTEMPTS TO GET GIT REPO NAME
        cps_unit_checker.database_connector.database_analysis_audit_id = args.database_analysis_audit_id
        cps_unit_checker.database_connector.current_repository = args.current_repository
        cps_unit_checker.database_connector.current_file_under_analysis = target_cpp_file
    cps_unit_checker.main_run_check(dump_file, source_file)
    # OVERRIDE DELETING THE DUMP FILE WHEN IT EXISTS
    if args.use_existing_dump_file:
        args.delete_dump_file = False

    # COMMAND LINE OPTION TO KEEP THE DUMP FILE
    if args.delete_dump_file or not cps_unit_checker.found_ros_units_in_this_file:
        try:
            os.remove(dump_file)
            print("removing %s" % dump_file)
        except: 
            pass


    # for e in cps_unit_checker.errors:
    if len(cps_unit_checker.error_checker.all_errors) > 0:
        print ("inconsistencies for file: %s" % target_cpp_file)
        cps_unit_checker.error_checker.pretty_print(args.show_high_confidence, args.show_low_confidence)
        # eprint( "%s" % e.get_error_desc())
        # eprint( "%s" % e.linenr)
        # eprint( "%s" % e.units_at_first_assignment)
        # eprint( "%s" % e.all_units_assigned_to_var)
        # eprint( "%s" % e.units_when_multiple_happened)
    # eprint("Total errors: %i" % len(cps_unit_checker.errors))




if __name__ == "__main__":
    main()
