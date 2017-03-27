#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 Ben Lindsay <benjlindsay@gmail.com>

from os import popen, mkdir
from os.path import join, isfile, isdir
import pandas as pd
import time
import string

def job_tree(input_file_list=None, tier_list=None, base_param_dict={},
             base_dir='.', **kwargs):
    """
    Recursively generate the directory tree specified by values in files or
    functions from 'tier_list'. Copies the files in 'input_file_list' to each
    job directory and replaces all the variables with appropriate values
    """
    # Get and check variables
    if tier_list is None:
        raise ValueError("No tier_list provided")
    for i, tier in enumerate(tier_list):
        if not isinstance(tier, Tier):
            tier_list[i] = Tier(tier)
    if input_file_list is None:
        raise ValueError("No input_file_list provided")
    flat = kwargs.get('flat', True)
    name_sep = kwargs.get('name_sep', '-')
    job_name = kwargs.get('job_name', '')
    sub_file = kwargs.get('sub_file', 'sub.sh')
    kwargs['sub_file'] = sub_file
    if sub_file not in input_file_list:
        input_file_list.append(sub_file)
    # The first time through, determine whether to use qsub or sbatch
    # and store that back into the kwargs dictionary
    sub_prog = kwargs.get('sub_prog', _find_sub_prog())
    kwargs['sub_prog'] = sub_prog
    sleep_time = kwargs.get('sleep_time', 0)
    submit = kwargs.get('submit', True)

    # Remove the first Tier object from the tier_list
    next_tier = tier_list.pop(0)
    df = None
    name_field = next_tier.name_field
    # If provided, read data from CSV file into dataframe df
    if next_tier.csv_file is not None:
        df = pd.read_csv(next_tier.csv_file, dtype=str)
        for column in df:
            df[column] = df[column].astype(str)
        if name_field is None:
            name_field = df.columns[0]
    # If provided, add fields in next_tier's dictionary to the dataframe df
    if next_tier.field_dict is not None:
        df, name_field = _add_dict_to_df(next_tier.field_dict, df, name_field)
    # Use any functions provided to generate data for other fields to add to df
    if next_tier.dict_func is not None:
        field_arrays_dict = next_tier.dict_func(df, base_param_dict)
        df, name_field = _add_dict_to_df(field_arrays_dict, df, name_field)
    # Create a list of dictionaries where each dictionary contains key-value
    # pairs for variable replacements within its corresponding branch
    param_dict_list = df.to_dict(orient='records')
    if len(tier_list) == 0:
        last_tier = True
    else:
        last_tier = False
    # Handle each branch on this tier by copying/editing files and submitting
    # jobs if this is the last tier, or recursively generating the next tier
    for param_dict in param_dict_list:
        param_dict = _merge_dicts(base_param_dict, param_dict)
        if job_name == '':
            new_job_name = param_dict[name_field]
        else:
            new_job_name = job_name + name_sep + param_dict[name_field]
        kwargs['job_name'] = new_job_name
        param_dict['JOB_NAME'] = new_job_name
        if flat:
            if last_tier:
                new_dir = join(base_dir, new_job_name)
            else:
                new_dir = base_dir
        else:
            new_dir = join(base_dir, param_dict[name_field])
        if isdir(new_dir):
            if last_tier:
                print('{} already exists. Skipping.'.format(new_dir))
                continue
        else:
            if ( not flat ) or ( flat and last_tier ):
                mkdir(new_dir)
        if last_tier:
            _copy_input_files(input_file_list, new_dir, param_dict)
            sub_fname = _replace_vars(sub_file, param_dict)
            if submit:
                _submit_job(new_dir, sub_fname, sleep_time, sub_prog)
        else:
            tier_list_copy = list(tier_list)
            job_tree(input_file_list, tier_list_copy, param_dict,
                     new_dir, **kwargs)

class Tier():
    """
    Simple wrapper for metadata corresponding to the generation of one tier
    in a job tree
    """
    def __init__(self, *args, **kwargs):
        self.csv_file = None
        self.field_dict = None
        self.dict_func = None
        self.name_field = kwargs.get('name_field', None)
        data_found = False
        for arg in args:
            if isinstance(arg, basestring):
                if isfile(arg):
                    if self.csv_file == None:
                        self.csv_file = arg
                    else:
                        msg = "Only 1 file name can be passed to Tier!"
                        raise ValueError(msg)
                else:
                    raise ValueError("Couldn't find file called {}!".format(arg))
                data_found = True
            elif isinstance(arg, dict):
                self.field_dict = arg
                data_found = True
            elif callable(arg):
                self.dict_func = arg
                data_found = True
            else:
                raise ValueError("Tier argument {} not recognized!".format(arg))
        if not data_found:
            raise ValueError("No files, dicts, or functions passed to Tier!")

def _add_dict_to_df(field_dict, df=None, name_field=None):
    """
    Helper function for job_tree() that takes a dataframe (or NoneType) and a
    dictionary structured like
    {'col_1': ['val_1', 'val_2', ...], 'col_2': ['val_3', 'val_4', ...], ...}
    then either creates a dataframe or adds to the given one and returns the
    final dataframe.
    """
    # Force data to stay as strings
    df_tmp = pd.DataFrame(field_dict, dtype=str)
    for column in df_tmp:
        df_tmp[column] = df_tmp[column].astype(str)
    # If not provided in Tier object and no CSV file was provided, use the
    # first field name from the first function provided as the names for
    # next tier
    if name_field is None:
        name_field = df_tmp.columns[0]
    if df is None:
        df = df_tmp.copy()
    elif len(df) == len(df_tmp):
        try:
            df = df.join(df_tmp, how='outer')
        except ValueError:
            msg = "{} and {} contain overlapping names!"
            msg = msg.format(df.columns, df_tmp.columns)
            raise ValueError(msg)
    else:
        msg = "Rows of df and df_tmp don't line up!\n"
        msg += "df:\n{}".format(df)
        msg += "df_tmp:\n{}".format(df_tmp)
        raise ValueError(msg)
    return df, name_field

def _find_sub_prog():
    """
    Returns the first job submission command found on the system.
    Currently, only qsub and sbatch are supported
    """
    possible_sub_prog_list = ['qsub', 'sbatch']
    for prog in possible_sub_prog_list:
        if popen('command -v ' + prog).read() != '':
            return prog
    return None

def _merge_dicts(*dict_args):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    See http://stackoverflow.com/a/26853961/2680824
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result

def _copy_input_files(input_file_list, job_dir, param_dict):
    """
    Given a list of file paths 'input_file_list' and job directory
    'job_dir', copies the files to the job directory and replaces
    variables in those files.
    """
    # Make a copy of input_file_list just for safety
    file_list = list(input_file_list)
    # Replace variables in file names, if any
    file_list = [ _replace_vars(fname, param_dict) for fname in file_list ]
    print("Copying {} to {} and replacing vars".format(file_list, job_dir))
    for fname in file_list:
        # Copy file to job_dir with variables in text of file replaced
        with open(fname, 'r') as f_in, \
                open(join(job_dir, fname), 'w') as f_out:
            text = f_in.read()
            text = _replace_vars(text, param_dict)
            f_out.write(text)

def _replace_vars(text, param_dict):
    """
    Given a block of text, replace any instances of '{key}' with 'value'
    if param_dict contains 'key':'value' pair.
    This is done safely so that brackets in a file don't cause an error if
    they don't contain a variable we want to replace.
    See http://stackoverflow.com/a/17215533/2680824

    Examples:
        >>> _replace_vars('{last}, {first} {last}', {'first':'James', 'last':'Bond'})
        'Bond, James Bond'
        >>> _replace_vars('{last}, {first} {last}', {'last':'Bond'})
        'Bond, {first} Bond'
    """
    return string.Formatter().vformat(text, (), _Safe_Dict(param_dict))

class _Safe_Dict(dict):
    """
    Class with all the same functionality of a dictionary but if a key isn't
    present, it just returns '{key}'.
    This helps with _replace_vars().

    Examples:
        >>> d = _Safe_Dict({'last':'Bond'})
        >>> d['last']
        'Bond'
        >>> d['first']
        '{first}'
    """
    def __missing__(self, key):
        return '{' + key + '}'

def _submit_job(job_dir, sub_file, sleep_time, sub_prog):
    """
    Submit 'sub_file' in 'job_dir' using submission program 'sub_prog'.
    Wait 'sleep_time' seconds between each submission.
    """
    print("submitting {}".format(join(job_dir, sub_file)))
    popen('cd ' + job_dir + '; ' + sub_prog + ' ' + sub_file + '; cd -')
    if sleep_time > 0:
        time.sleep(sleep_time)
