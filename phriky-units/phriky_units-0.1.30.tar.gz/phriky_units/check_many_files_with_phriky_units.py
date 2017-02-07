#!/usr/bin/env python
# -*- coding: utf-8 -*-


import git
import os
import sys
from subprocess import Popen
from database_connector import DatabaseConnector
from cps_units_checker import CPSUnitsChecker
import time

import click


@click.command()
@click.argument('file_containing_list_of_files_to_be_analyzed') 
#TODO: make this generic or read from the same location as phriky units
@click.option('--include_dir', default='', help='include directory for cppcheck')
# @click.option('--debug_print_ast/--no-debug_print_ast', default=False, help='Very verbose debug print of Abstract Syntax Trees and unit decorations')
@click.option('--show_high_confidence/--no_show_high_confidence', default=True, help='Should show hig-confidence inconsistences. Defaults to True')
@click.option('--show_low_confidence/--no_show_low_confidence', default=False, help='Should show low-confidence inconsistencies. Defaults to False.')
@click.option('--use_var_name_heuristic/--no_use_var_name_heuristic', default=False, help='Should use variable name heuristics to assignm units. Experimental.')
@click.option('--check_unit_smell/--no_check_unit_smell', default=False, help='Should check for strange unit assignments (unit smells). See error_checker.py')
@click.option('--delete_dump_file/--no_delete_dump_file', default=False, help='Will not delete temporary cppcheck "dump" file.')
@click.option('--use_existing_dump_file/--no_use_existing_dump_file', default=True, help='Reuses existing dump file, if possible.')
@click.option('--only_find_files_with_units/--no_only_find_files_with_units', default=False, help='No inconsistency analysis. Only finds files with physical units.')
@click.option('--write_results_to_database/--no_write_results_to_database', default=True, help='Write results to database.  See DatabaseConnector.py for details.')
@click.option('--note_for_database', default='', help='note for database analysis record')
def main(file_containing_list_of_files_to_be_analyzed, 
        include_dir, 
        # debug_print_ast,
        show_high_confidence,
        show_low_confidence,
        use_var_name_heuristic,
        check_unit_smell,
        delete_dump_file,
        use_existing_dump_file,
        only_find_files_with_units,
        write_results_to_database,
        note_for_database):
    """Console script for phriky_units"""
    # 'Detect physical unit inconsistencies in C++ code, especially ROS code.')

    # VERIFY TARGET FILE EXISTS
    if not os.path.exists(file_containing_list_of_files_to_be_analyzed):
        print ('File not found: %s' % file_containing_list_of_files_to_be_analyzed)

    database_analysis_audit_id = 0
    if write_results_to_database:
        # database_analysis_audit_id = 157
        dbc = DatabaseConnector()
        dbc.VERSION = CPSUnitsChecker().VERSION
        # INSERT nOTE
        note = note_for_database
        if not note:
            note = file_containing_list_of_files_to_be_analyzed
        dbc.create_database_entry_for_one_time_analysis(file_containing_list_of_files_to_be_analyzed, note)
        database_analysis_audit_id = dbc.database_analysis_audit_id
        print( 'NEW DATABASE ANALYSIS: ID=%d' % database_analysis_audit_id)

    args = ['./phriky_units.py']
    if write_results_to_database and database_analysis_audit_id > 0:
        args.append('--write_results_to_database')
        args.append('--database_analysis_audit_id='+str(database_analysis_audit_id))
    if check_unit_smell:
        args.append('--check_unit_smell')
    if use_existing_dump_file:
        args.append('--use_existing_dump_file')
    if delete_dump_file:
        args.append('--delete_dump_file')
    else:
        args.append('--no_delete_dump_file')

    if use_var_name_heuristic:
        args.append('--use_var_name_heuristic')
    

    # if include_dir:
        # args.append('--include_dir ' + include_dir)

    all_files_to_analyze = [f.strip() for f in open(file_containing_list_of_files_to_be_analyzed).readlines()]
    iter_of_all_files_to_analyze = iter(all_files_to_analyze)


    # for file_name in all_files_to_analyze:
        # if not os.path.exists(file_name):
            # print ('Could not find file: %s' % file_name)
            # continue
        # current_repository = ''
        # # GET THE GIT REPOSITORY
        # if write_results_to_database:
            # s = git.cmd.Git(os.path.dirname(file_name)).execute(['git', 'rev-parse', '--show-toplevel'])  # same as above
            # current_repository = os.path.basename(s)
        # # OPEN PHRIKY-UNITS
        # phriky_units_process = Popen(' '.join(args + ['--current_repository='+current_repository]+ [file_name]),  shell=True)
        # phriky_units_process.communicate()
        # # processes_started += 1
        # # list_of_processes.append(phriky_units_process)

    # ------------------------------------------
    # RUN MULTIPLE PROCESS AT ONCE
    # ------------------------------------------
    number_of_processes = 3
    # number_of_processes = 5
    list_of_processes = []
    first = True
    processes_started = 0
    processes_finished = 0

    process_counter = 0

    while ( len(list_of_processes) > 0 )  or first:
        first = False
        # print len(list_of_processes)
        # print ('Number of processes active: %d' % len(list_of_processes))
        # ADD PROCESSES UNTIL LIMIT REACHED
        while len(list_of_processes) < number_of_processes:
            file_name = next(iter_of_all_files_to_analyze, None)
            if not file_name:
                break
            # TEST FOR NON-ASCII CHARACTERS IN NAME
            try:
                file_name.decode('ascii')
            except UnicodeDecodeError:
                print("Skipping non-ascii filename %s" % file_name)
                continue
            # TEST FOR FILE EXISTS
            if not os.path.exists(file_name):
                print ('Could not find file: %s' % file_name)
                continue
            current_repository = ''
            # GET THE GIT REPOSITORY
            if write_results_to_database:
                s = git.cmd.Git(os.path.dirname(file_name)).execute(['git', 'rev-parse', '--show-toplevel'])  # same as above
                current_repository = os.path.basename(s)
            # OPEN PHRIKY-UNITS
            # phriky_units_process = Popen(' '.join(args + ['--current_repository='+current_repository]+ [file_name]),  shell=False)
            phriky_units_process = Popen(' '.join(args + ['--current_repository='+current_repository]+ [file_name]),  shell=True)
            processes_started += 1
            # print("starting proc %d : %s " % (phriky_units_process.pid, file_name))
            list_of_processes.append(phriky_units_process)

        p_to_remove = None
        # CHECK IF THE PROCESS IS DONE, AND REMOVE IF POSSIBLE
        # print list_of_processes
        for p in list_of_processes:
            # ASK PROCESS TO UPDATE ITS RETURNCODE
            # if process_counter == 100:
                # print ("running : %d " %  p.pid)
            if not p.poll() :
                if p.returncode is not None:
                    # p.terminate()
                    # print("process %d complete returncode: %s" % (p.pid, str(p.returncode)))
                    # p.communicate()
                    p_to_remove = p
                    break
                # else:
                    # print("process %d still running p.poll() is None, returncode is None: " % p.pid)
                    # pass
            # else:
                # print("process %d still running: p.poll() is not None " % p.pid)
                # pass

        if process_counter == 100:
            process_counter = 0
        process_counter += 1


        if p_to_remove and p_to_remove in list_of_processes:
            # p_to_remove.terminate()
            # print("removing process %d: " % p_to_remove.pid)
            list_of_processes.remove(p_to_remove)
            # p_to_remove = None
            processes_finished += 1
        # GO EASY ON YOUR OS
        # print ('S-F: %d ' % (processes_started - processes_finished))
        time.sleep(0.05)

    # for file_name in iter(all_files_to_analyze):







if __name__ == "__main__":
    main()
