"""pocli -- function libary

Copyright (c) 2016, 2017
Florian Kaiser (fek@rzg.mpg.de), Klaus Reuter (khr@rzg.mpg.de)

Initial version based on the program "pyocclient.py" by Florian Kaiser.
"""


import os
import sys
import math
import json
import time
import locale
import argparse
import getpass
import owncloud


def get_ocrc():
    """Return the full path to the pocli <.ocrc> configuration file."""
    home = os.path.expanduser('~')
    rcfile = os.path.join(home, '.ocrc')
    return rcfile


def init_ocrc():
    """Initialize the pocli <.ocrc> configuration file.
    
    By default, a MPCDF datashare compatible configuration will be created.
    """
    config = {}
    config['OC_USER'] = getpass.getuser()
    config['OC_SERVER'] = "https://datashare.mpcdf.mpg.de"
    config['OC_DEBUG'] = False
    rcfile = get_ocrc()
    with open(rcfile, 'w') as fp:
        fp.write(json.dumps(config, sort_keys=True, indent=4, separators=(',', ': ')))
    print("created config file: " + rcfile)


def _client():
    """Construct and return ownCloud client object.
    
    The configuration is read from the configuration file <~/ocrc>.
    The password is read from the environment variable OC_PASSWORD,
    in case this variable is not set the user is prompted interactively.
    """
    config = {}
    rcfile = get_ocrc()
    with open(rcfile, 'r') as fp:
        config = json.loads(fp.read())
    # for the MPCDF datashare service we forbid the use of OC_PASSWORD
    if ('datashare.mpcdf.mpg.de' not in config['OC_SERVER']) and ('OC_PASSWORD' in os.environ):
        password = os.environ['OC_PASSWORD']
    else:
        password = getpass.getpass()
    config['OC_PASSWORD'] = password
    client = owncloud.Client(config['OC_SERVER'], debug=config['OC_DEBUG'])
    client.login(config['OC_USER'], config['OC_PASSWORD'])
    return client


def _filesizeformat(value):
    """Convert an integer representing the size of a file-like object
    in bytes into a human readable form (i.e. 13 KB, 4.1 MB, etc).
    """
    _FILESIZE_BASE = 1024
    _FILESIZE_SUFFIXES = ('B', 'K', 'M', 'G', 'T', 'P', 'E', 'Z')
    if value is None or value == "":
        return ""
    if type(value) != int:
        try:
            value = float(value)
        except:
            return ""
    suffix_index = 0 if value == 0 else int(math.log(value) / math.log(_FILESIZE_BASE))
    if suffix_index == 0:
        scaled_value = value
    elif suffix_index > len(_FILESIZE_SUFFIXES) - 1:
        raise ValueError("number too big")
    else:
        scaled_value = round(float(value) / pow(_FILESIZE_BASE, suffix_index), 2)
    suffix = _FILESIZE_SUFFIXES[suffix_index]
    return "%g %s" % (scaled_value, suffix)


def _print_file_list(l):
    """Print a file list using a pretty format."""
    file_info_str = lambda x: "{:6s} {:10s} {:18s} {:s}".format(x.file_type, _filesizeformat(x.get_size()),
                                x.get_last_modified().strftime('%x %X'), x.path)
    for x in l:
        print(file_info_str(x))


# Code snippet adapted from:
# https://code.activestate.com/recipes/577058-query-yesno/
def _query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return the answer as a string "yes" or "no".
    """
    valid = {"yes":"yes", "y":"yes", "ye":"yes", "no":"no", "n":"no"}
    if default == None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)
    while 1:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return default
        elif choice in valid.keys():
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' (or 'y' or 'n').\n")


# --- routines called by the cli interface (cli.py) below ---


def put(argparse_args):
    """Upload one or more files to an OwnCloud server."""
    if (argparse_args.directory):
        directory = argparse_args.directory
    else:
        directory = '/'
    args = vars(argparse_args)
    file_list = args['files']
    if (len(file_list) > 0):
        client = _client()
        try:
            lst = client.list(directory)
        except:
            print("`%s': remote directory does not exist" % directory)
        else:
            for file_name in file_list:
                if os.path.isfile(file_name):
                    size_mb = float(os.path.getsize(file_name)) / float(1024 * 1024)
                    file_basename = os.path.basename(file_name)
                    if (size_mb > 100.0):
                        print("`%s': large file detected (%.2f MB), transfer may take some time ..." % (file_basename, size_mb))
                    t0 = time.time()
                    client.put_file(os.path.join(directory, file_basename), file_name)
                    t1 = time.time()
                    dt = t1 - t0
                    print("`%s': OK (%.2f MB/s)" % (file_basename, size_mb / dt))
                else:
                    print("`%s': skipping, not a regular file" % file_name)
        client.logout()


def get(argparse_args):
    """Download one or more files from an OwnCloud server."""
    if (argparse_args.directory):
        directory = argparse_args.directory
    else:
        directory = '.'
    args = vars(argparse_args)
    file_list = args['files']
    if (len(file_list) > 0):
        if os.path.isdir(directory):
            client = _client()
            for file_name in file_list:
                try:
                    file_info = client.file_info(file_name)
                except:
                    print("`%s': remote object does not exist" % (file_name,))
                    continue
                else:
                    if file_info.is_dir():
                        print("`%s': skipping, download of remote directories is not supported" % (file_name,))
                        continue
                    else:
                        file_size_mb = float(file_info.get_size()) / float(1024 * 1024)
                        file_basename = os.path.basename(file_name)
                        if (file_size_mb > 100.0):
                            print("`%s': large file detected (%.2f MB), transfer may take some time ..." % (file_basename, file_size_mb))
                        file_target = os.path.join(directory, file_basename)
                        t0 = time.time()
                        client.get_file(file_name, file_target)
                        t1 = time.time()
                        dt = t1 - t0
                        size_mb = float(os.path.getsize(file_target)) / float(1024 * 1024)
                        print("`%s': OK (%.2f MB/s)" % (file_basename, size_mb / dt))
            client.logout()
        else:
            print("`%s': invalid local directory" % directory)


def ls(argparse_args):
    """List directory on OwnCloud server."""
    args = vars(argparse_args)
    directory_list = args['dir']
    if (len(directory_list) == 0):
        directory_list.append('/')
    client = _client()
    for directory in directory_list:
        try:
            lst = client.list(directory)
        except:
            print("`%s': remote directory does not exist" % directory)
        else:
            _print_file_list(lst)
    client.logout()


def rm(argparse_args):
    """Remove remote object from OwnCloud server."""
    args = vars(argparse_args)
    file_list = args['file']
    if (len(file_list) > 0):
        client = _client()
        for file_name in file_list:
            try:
                lst = client.list(file_name)
            except:
                print("`%s': no such remote object" % file_name)
            else:
                file_info = client.file_info(file_name)
                if file_info.is_dir():
                    if (len(lst) > 0):
                        print("`%s': skipping non-empty directory" % file_name)
                        continue
                answer = _query_yes_no("`%s': remove remote object?" % file_name)
                if answer is "yes":
                    client.delete(file_name)
        client.logout()


def mkdir(argparse_args):
    """Make directory on OwnCloud server."""
    args = vars(argparse_args)
    directory_list = args['dir']
    if (len(directory_list) > 0):
        client = _client()
        for directory in directory_list:
            client.mkdir(directory)
        client.logout()


def check(argparse_args):
    """Try to establish a connection to the OwnCloud server configured in the
    configuration file."""
    try:
        _client()
    except:
        raise
    else:
        print("OK!")
