"""
Usage:
    cfgen FILE [list] [OPTIONS]

Commands:
    list          list variables and their values

Options:
    --force   overwrite existing file

metaconfig cache
.cfgen.cache
<variable_name> = <value>

metaconfig file
cfgen.metaconfig
<variable_name> = <shell_command>

*.template
jinja template
"""

# terminology
#
# metaconfig - file where variables are defined
# metaconfig cache - file where values for variables are cached
# target template - file where template of the target config is defined
# target config - file to be generated from target template
#
# file path: /home/joe/Documents/file1.txt
# directory path: /home/joe/Documents/
# directory name: Documents
# file name: file1.txt
# stem: file1
# extension: .txt

from __future__ import print_function

from collections import OrderedDict
import os
import subprocess
import sys

import docopt
import future.utils
import jinja2
from jinja2.loaders import FileSystemLoader

_prg_name = "cfgen"
_metaconfig_file_name = _prg_name + ".metaconfig"
_target_template_file_extension = ".template"
_metaconfig_cache_file_name = "." + _prg_name + ".cache"
_metaconfig_caching_file_name = _prg_name + ".caching"


def main():
    args = docopt.docopt(__doc__)
    target_file = args["FILE"]
    if args["list"]:
        cmd_list(target_file)
    else:
        cmd_write(target_file)


def cmd_list(target_file_name):
    values = load_all(target_file_name)

    for name, value in values.items():
        print(name, value)


def cmd_write(target_file_name):
    if os.path.exists(target_file_name):
        raise ValueError(target_file_name + " already exists")
    expressions, values = load_all(target_file_name)
    values = evaluate_expressions(expressions, values)
    rendered = render_template(target_file_name, values)
    with open(target_file_name, "w") as f:
        print(rendered, end="", file=f)
    # cache at the end of successful write
    cache_values(values, _metaconfig_cache_file_name, _metaconfig_caching_file_name)


def render_template(target_file_name, values):
    env = jinja2.Environment(loader=FileSystemLoader("/"),
                             undefined=jinja2.runtime.StrictUndefined)
    template_file_name = get_target_template_file_name(target_file_name)

    return env.get_template(lookup_template_file(template_file_name)).render(values)


def lookup_template_file(template_file_name):
    template_file_path = None
    directory_path = ""
    for directory_name in get_current_path_elements():

        directory_path += os.sep + directory_name

        template_file_path_candidate = directory_path + os.sep + template_file_name
        if os.path.isfile(template_file_path_candidate):
            # last one will win
            template_file_path = template_file_path_candidate
            
    if not template_file_path:
        raise ValueError("Template file not found " + template_file_name)
    
    return template_file_path


def load_all(target_file_name):
    expressions = load_metaconfigs()
    values = load_metaconfig(_metaconfig_cache_file_name)

    return expressions, values


def cache_values(definitions, cache_file_name, caching_file_name):
    # read what needs to be cahed
    if os.path.exists(caching_file_name):
        with open(caching_file_name) as f:
            caching_var_names = f.read().splitlines()
        
        # cache
        with open(cache_file_name, "w") as f:
            for name, value in definitions.items():
                if name in caching_var_names:
                    print(name + " = " + value, file=f)


def load_metaconfigs():
    """ Loads all metaconfig files and returns merged variable to expression dictionary """
    definitions = OrderedDict()
    directory_path = ""
    for directory_name in get_current_path_elements():

        directory_path += os.sep + directory_name

        metaconfig_file_path = directory_path + os.sep + _metaconfig_file_name
        definitions.update(load_metaconfig(metaconfig_file_path))

    return definitions


def load_metaconfig(file_path):
    """ Loads a single metaconfig file and returns variable to expression dictionary """
    definitions = OrderedDict()
    if os.path.isfile(file_path):
        with open(file_path) as f:
            for line in [l.strip(os.linesep).strip() for l in f.readlines()]:
                # skip comments
                if line.startswith("#"):
                    continue
                # skip empty lines
                if not line:
                    continue
                # parse line
                try:
                    var_name, var_expression = parse_metaconfig_line(line)
                    definitions[var_name] = var_expression
                except ValueError as e:
                    future.utils.raise_from(
                        ValueError("Cannot parse metaconfig; file=" + file_path), e)

    return definitions


def evaluate_expressions(expressions, values):
    for var_name, var_expression in expressions.items():
        if not var_name in values:
            values[var_name] = evaluate_expression(var_expression, values)

    return values


def evaluate_expression(var_expression, eval_env):
    """ Evaluates given expression """
    try:
        completed_process = subprocess.check_output(var_expression,
                                                    env=eval_env,
                                                    shell=True,
                                                    universal_newlines=True)

        return get_string(completed_process).rstrip()
    except:
        e = sys.exc_info()[1]
        future.utils.raise_from(
            ValueError("Cannot evaluate expression " + var_expression), e)


def parse_metaconfig_line(line):
    """ Parses line and return key=value tuple """
    delimiter_pos = line.find("=")
    if delimiter_pos == -1:
        raise ValueError("'=' not found in metaconfig line " + line)
    var_name = line[:delimiter_pos].strip()
    if len(var_name) == 0:
        raise ValueError("variable name not found in metaconfig line " + line)
    var_expr = line[delimiter_pos + 1:].strip()
    return var_name, var_expr


def get_current_path_elements():
    # first element is empty, remove it
    return os.getcwd().split(os.sep)[1:]


def get_target_template_file_name(target_file_name):
    return target_file_name + _target_template_file_extension


def get_string(value):
    """ Returns string representation of the value or empty string if None """
    if value:
        return str(value)
    else:
        return ""


if __name__ == '__main__':
    main()
