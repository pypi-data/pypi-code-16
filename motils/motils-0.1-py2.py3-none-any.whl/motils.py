
# Should work in python2, 3
# A set of tools, functions, aliases and more used in RecBlast.

import os
import re
import tarfile
import zipfile
from time import strftime


def file_to_string(file_name):
    """Reads a file (file_name) and returns the text in it as a string."""
    with open(file_name, 'r') as f:
        text = f.read()
    # delete original file
    os.remove(file_name)
    return text


def remove_commas(file_name, new_file_name=None):
    """Replaces commas with newlines in a file."""
    if not new_file_name:
        new_file_name = "{}_nocommas".format(file_name)

    with open(file_name, 'r') as f:
        text = f.read()
        text = replace(text, ',', '\n')
    with open(new_file_name, 'w') as f:  # now writing
        f.write(text)
    return new_file_name

def zip_files(file_list, output_path):
    """Writing a file_list to zip at output_path"""
    bname = os.path.basename  # for efficiency
    with zipfile.ZipFile(output_path, mode='w') as zf:
        # adding all fasta files
        for file_name in file_list:
            zf.write(file_name, bname(file_name))
    return output_path


# debugging function
def debug(debug_string, to_debug):
    """
    Receives a string and prints it, with a timestamp.
    :param debug_string: a string to print
    :param to_debug: boolean flag: True means print, False - ignore.
    :return:
    """
    if to_debug:
        print("DEBUG {0}: {1}".format(strftime('%H:%M:%S'), debug_string))


def create_folder_if_needed(path):
    """
    Receives a path and creates a folder when needed (if it doesn't already exist).
    """
    if os.path.exists(path):
        print("{} dir exists".format(path))
    else:
        print("{} dir does not exist. Creating dir.".format(path))
        os.mkdir(path)


def file_len(file_name):
    """Return the file length in lines."""
    with open(file_name) as f:
        for i, l in enumerate(f):
            pass
    return i + 1


def targz_folder(folder, archive_name=None):
    """
    Receives a folder path and an optional archive_name and performs tar + gz on the folder.
    """
    if not archive_name:
        archive_name = "{}.tar.gz".format(folder)
    with tarfile.open(archive_name, "w:gz") as tar:
        tar.add(folder, arcname=os.path.basename(folder))
    return archive_name


def write_bash_script(command_line, write_folder, script_name="run_script.sh"):
    """
    Writing a bash script, and giving it run permissions.
    Receive command line, write folder and an optional script name.
    """
    script_path = join_folder(write_folder, script_name)  # script location
    with open(script_path, 'w') as script:
        script.write("#! /bin/bash\n")
        script.write("# The script is designed to run the following command:\n")
        script.write(command_line)
    # run permissions for the script:
    os.chmod(script_path, 0751)
    return script_path


def merge_two_dicts(x, y):
    """Given two dicts, merge them into a new dict as a shallow copy."""
    z = x.copy()
    z.update(y)
    return z


def is_number(s):
    """The function determines if a string is a number or a text. Returns True if it's a number. """
    try:
        int(s)
        return True
    except ValueError:
        return False


def exists_not_empty(path):
    """Receives a file path and checks if it exists and not empty."""
    if os.path.exists(path) and os.stat(path).st_size > 0:
        return True
    else:
        return False


# for efficiency
strip = str.strip
split = str.split
replace = str.replace
re_search = re.search
re_sub = re.sub
re_match = re.match
upper = str.upper
lower = str.lower
join_folder = os.path.join
