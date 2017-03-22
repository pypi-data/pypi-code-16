import pwn as pt    # Advanced analyses and exploit string generation
import angr         # Advanced analyses
import os           # Calls to system
import sys          # argv and argc use
import re           # regular Expressions

__proc = process('/bin/bash')

# Analyze Source File for common mistakes:
def source_fuzz():
    print "Please enter the FULL name of the source file:"
    _src_name = raw_input()
    f = open(_src_name)
    lines = f.readlines()
    line_num = 1
    for line in lines:
        if line.contains("gets("):
            print "[UNSAFE CALL DETECTED]: gets() detected at line " + line_num
            print "Please remove gets in favor of literally almost any other function"
            line_num += 1
        if line.contains(""):
            
            print "[IMPROPER READ BOUNDS] at line " + line_num + ", please adjust to " + prop_bounds

# Set the target process
def _setProcess(_target):
    p = process(_target)


# The bluntest instrument here, simply tries to cause a crash
def try_crash():

    # Cyclic crash
    for i in range (9999999999):
        crashstr = pt.cyclic(i)


# This function is used to determine whether a core has been
# generated. This fuzzer hinges on this functionality and
# works closely with gdb. If cores are not enabled by default
# the calling function should have tried to enable them.
def det_core():
    # FIXME
    
    

# This function merely cleans old cores and attempts to ensure
# that core generation is enabled for this run
def core_cleanEnable():
    os.system('rm ./core*')
    os.system('ulimit -c unlimited')
    return


# Defines functionality designed around 
# bruteforcing EIP assuming no menus.
# This is like piping the input directly
# into the program and hoping for the best.
def raw_brute(bfsize = -1):
    
    # If passed with numeric arg, will start
    # assuming buffer size of _at least_ 
    # bfsize. Useful for large buffer and
    # saving time if you already know the
    # buffer size.
    if (bfsize != -1):
        
    
        os.system("ulimit -c unlimited")
        blen = bfsize

        for bflen in range(bfsize * bfsize):
            a_buf = pt.cyclic(bflen)
            det_core()


# Defines the menu module for calling
# the fuzzer as a standalone tool.
# Not meant for use seperately but it
# _should_ work, in theory should you
# import it anyway.
def menu():

    print "FC2 Fuzzer, created by nullp0inter"
    print "=============[ MENU ]============="
    print "[1]: Attempt to bruteforce EIP*"
    print "[2]: Attempt to bruteforce menu-[i]"
    print "[3]: Attempt to bruteforce menu-[ni]"
    print "[4]: Read source for vulnerable functions"

    choice = raw_input("Choose a menu option: ")
    
    switch(



if __name__ == '__main__':
    
    print "CHECK OK"
    
    if (sys.argc < 2):
        print "Enter the path of a target binary:"
        bin_path = raw_input()
        _setProcess(bin_path)
    
    _setProcess(argv[1])
    
