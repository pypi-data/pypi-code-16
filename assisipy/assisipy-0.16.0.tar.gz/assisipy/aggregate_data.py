#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tools for loading data from CASU logfiles.
"""

import sys
import os
import csv

import scipy.io as sio

def load_from_csv(filepath):
    """
    Load log data from a csv file.
    """
    data = {}

    filename = os.path.basename(filepath)
    casu = ''
    if len(filename) < 25:
        sys.exit('{0} is an invalid CASU log file name!.'.format(filename))
    else:
        casu = filename[20:-4].replace('-','_')
        data[casu] = {}

    with open(filepath) as datafile:
        datareader = csv.reader(datafile,delimiter=';')
        dataid = None
        for row in datareader:
            if len(row) > 2:
                # Guard against incomplete rows
                # (e.g. interrupted program)
                dataid = row[0].replace('-','_')
                t_id = 't_' + dataid
                if not dataid:
                    # Empty data ids appear in some datasets
                    # This actually should not happen
                    # This is a quick fix until we figure out 
                    # the real cause of the problem
                    continue
                if dataid not in data[casu]:
                    # New row id
                    data[casu][dataid] = []
                    data[casu][t_id] = []
                try:
                    ts = float(row[1]) # timestamp
                    data[casu][t_id].append(ts)
                    data[casu][dataid].append([float(x) for x in row[2:]])
                except ValueError:
                    #print('ValueError in row {0}: {1}'.format(datareader.line_num,row))
                    # Accelerometers are currently not providing any data
                    # We don't want to bother users with that
                    pass

        # Check final row (my be incomplete)
        if dataid:
            # Some data were present
            if len(data[casu][dataid]) > 1:
                # At least two rows were present
                if not len(data[casu][dataid][-1]) == len(data[casu][dataid][-2]):
                    # Remove last row if it's incomplete
                    data[casu][dataid] = data[casu][dataid][:-1]

    return data

def process_folder(foldername):
    """
    Recurse into subfolders and process all csv files.
    """
    data = {}

    dirs = os.walk(foldername)
    for (dirpath, dirnames, filenames) in dirs:
        for filename in filenames:
            if filename[-4:] == '.csv':
                new_data = load_from_csv(os.path.join(dirpath,filename))
                if new_data.keys():
                    casu = new_data.keys()[0]
                    if casu in data.keys():
                        print('WARNING: Found more than one logfile for {0}!'.format(casu))
                        print('The output file will contain data from only one logfile!')
                data = dict(data, **new_data)

    return data

def main():
    """
    Main script entry point.
    """
    # TODO: Use argparse and add reasonable options
    # Document usage
    # Consider if the program should take an .assisi file as input?

    data = {}
    
    # The first argument is the name
    # of the file/folder to process
    outname = ''
    if len(sys.argv) < 2:
        sys.exit('Please provide a file or folder to process.')
    elif sys.argv[1][-4:] == '.csv':
        # We are assuming that we need to process a single .csv file
        data = load_from_csv(sys.argv[1])
        outname = sys.argv[1][:-4]
    else:
        # We are assuming that the argument is a folder
        # to be processed. It is assumed that it contains
        # subfolders, each of which corresponds to one CASU.
        # Each subfolder is assumed to contain one or more
        # .csv files.
        data = process_folder(sys.argv[1])
        outname = sys.argv[1].rstrip(os.sep)

    sio.savemat(outname,data,oned_as='column')


if __name__ == '__main__':

    main()
