import logging
import itertools
import subprocess
import time

logging.basicConfig()
log = logging.getLogger("multirun")
log.setLevel(logging.INFO)

def parse_var(var_string):
    if var_string is None:
        return None
    groups_strings = var_string.split("|")
    value_set = [x.split("&") for x in groups_strings]
    return value_set
    
def generate_all_values(var_values):
    """
    var_values is a list of value_set, one for each var
    value_set can be set to None
    value_set is a list of groups; a group is a list of values
    """
    
    nb_groups = None
    var_set = []
    for num_var, value_set in enumerate(var_values):
        if value_set is None:
            continue
        var_set.append(num_var)
        if nb_groups is None:
            nb_groups = len(value_set)
        elif nb_groups != len(value_set):
            raise ValueError("var %i as a number of groups incompatible with previous var")
        
    set_var_values = [var_values[i] for i in var_set]
        
    result = []
    for group_list in zip(*set_var_values):
        for vars_val in itertools.product(*group_list):
            full_vars_val = [""] * len(var_values)
            for var_num, vv in zip(var_set, vars_val):
                full_vars_val[var_num] = vv
            result.append(full_vars_val)
        
    return result
    
MAX_NB_VARS = 5

def define_parser(parser):
    for num_var in range(MAX_NB_VARS):
        parser.add_argument("--var%i"%num_var)
    parser.add_argument("cmd")
    
def do_run(args):
    var_values = []
    for num_var in range(MAX_NB_VARS):
        var_values.append(parse_var(getattr(args, "var%i"%num_var)))
    
    for vals in generate_all_values(var_values):
        cmd = args.cmd.format(*vals)
        print "[%s] LAUNCHING: %s"%(time.strftime("%c"), cmd)
        subprocess.call(cmd, shell = True)
        print "[%s] FINISHED: %s"%(time.strftime("%c"), cmd)

def command_line():
    import argparse
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    define_parser(parser)
    args = parser.parse_args()
    do_run(args)
    
if __name__ == "__main__":
    command_line()
