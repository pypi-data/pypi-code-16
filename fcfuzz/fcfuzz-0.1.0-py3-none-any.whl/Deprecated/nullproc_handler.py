## Imports
import os
import sys
import subprocess
import glob
import pwn as pt
from string import find

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~{ GLOBALS }~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
HOME_DIR = os.path.expandvars('${HOME}')

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~{ Classes }~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
## Handle a process and store relevant info
class process(object):
    '''Process help page

        The process class is meant to hold all of the relevent data for a program.
        This class currently requires a fully qualified path to the target to be supplied,
        there are likely ways around that but they are low on the priorities list for now.

        Members include:
        - path :: The filepath
        - proc :: A hook into the process (hopefully done right)
        - cores :: A collection of core dumps
        - crashing_strings :: A collection of crashing strings, not always helpful
        - customMenuTraversals :: A collection of custom menu traversals.
        - baseaddr :: The base address of the program, useful for offset calculation
        - assembly :: The assembly for the program, this will likely change a bit in the future
        - gadgets :: A collection of ROPgadgets
        - eip_dist :: The distance to EIP using a bruteforce method, None if that fails

        Member methods:
        - printasm() :: prints the program assembly. Frustrating adds random newlines at present
        - show_gadgets() :: prints out the gadgets. Searching coming soon (hopefully)
        - show_poprets() :: shows the pop x rets, the most commonly useful of the gadgets.

    '''
    
    ## Initialize the class
    def __init__(self, path):
        '''Process Class Constructor
            This constructs the object.
        '''
        # Prevent creation on invalid path
        try:
            _ = open(path,'rb')

            # Obtain the raw bytes
            r_bytes = _.read()
            _.close()
        except IOError: 
            print 'ERROR: could not open process with path [\'' + path + '\']'
            #raise IOError()
            raise Exception('InvalidPathException: Double check the provided\
                file path and try again')

        # Open devnull pipe for subprocess error
        devnull = open(os.devnull,'w')
        
        
        # Member vars
        self.path = path
        self.cores = []                      
        self.crashing_strings = [] 
        self.customMenuTraversals = []
        self.baseaddr = self._getbase()
        self.assembly = self._getasm()
        self.gadgets = self._get_gadgets()
        self.path_dir = self._get_path_dir()    
        self.raw_bytes = r_bytes
        self.eip_dist = self._brute_eip_dist()
        self.rip_dist = None

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~{ Private Methods }~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
    
    def _getbase(self):
        '''_getbase
            This method will get the base of libc to be used in calculations (eventually).
            
           [!!] THIS METHOD IS INTERNAL AND NOT MEANT TO BE CALLED BY THE USER
        '''

    def _getasm(self): 
        '''_getasm
            This function utilizes objdump to grab in all of the assembly
            for the specified binary. The parsing and better handling is
            done elsewhere and not yet implemented (fully, in anycase).

            [!!] THIS METHOD IS INTERNAL AND NOT MEANT TO BE CALLED BY THE USER
        '''
        path = self.path
        try:
            _ = open(path)
            _.close()
            os.system('objdump -M intel -D ' + path + ' > ~/tmpdmp')
            try:
                f = open(os.path.expandvars('${HOME}/tmpdmp'))
                dump = f.readlines()
                f.close()
                os.remove(HOME_DIR + '/tmpdmp')
                assembly = []
                for line in dump:
                    assembly.append(line)
                assembly = self._strip_newlines(assembly)
                return assembly
            except IOError:
                print 'ERROR: could no open assembly dump'
        except IOError:
            print 'ERROR: could not open file: ' + path
            raise IOError()

    def _get_gadgets(self): 
        '''_get_gadgets
            This function (currently) uses ROPgadget to search through the
            specified binary and return a list of all gadgets (minus the
            fluff from the tool). I HOPE to eventually replace this with my
            own rop gadget finding implementation to provide better, more
            granular support. That is a far off project for now though.
            
            [!!] THIS METHOD IS INTERNAL AND NOT MEANT TO BE CALLED BY THE USER
        '''
        devnull = open(os.devnull,'w')
        gadfile = open(os.path.expandvars('${HOME}/gadgetstmp'),'w')
        path = self.path
        ropgen = ['/usr/local/bin/ROPgadget','--binary',path]
        subprocess.call(ropgen, stdout=gadfile, stderr=devnull)
        gadfile.close()
        try:
            gadfile = open(os.path.expandvars('${HOME}/gadgetstmp'),'r')
            gadgets_raw = gadfile.readlines()
            gadfile.close()
            gadgets = []
            for entry in gadgets_raw:
                gadgets.append(entry)
            os.remove(HOME_DIR + '/gadgetstmp')
            devnull.close()
            gadgets = self._fix_gadgets(gadgets)
            gadgets = self._strip_newlines(gadgets)
            return gadgets
        except IOError:
            print 'ERROR: could not open tmp gadgets file for parsing'
            return None

    def _fix_gadgets(self, gadgets): 
        '''_fix_gadgets
            This method fixes the list of gadgets provided by ROPgadget
            by parsing out the useless info. What is left should be the
            useful bits. I have plans to expand this to allow the list
            to be searchable but that may involve moving this to its own
            class.

            [!!] THIS METHOD IS INTERNAL AND NOT MEANT TO BE CALLED BY THE USER.

        '''
        gadgets_fixed = []
        for idx,g in enumerate(gadgets):
            if (find(g,'Gadgets') != -1):
                continue
            if (find(g,'gadget') != -1):
                continue
            if (find(g,'==') != -1):
                continue
            if (find(g,'Unique') != -1):
                continue
            if g == '\n':
                continue
            if (gadgets[gadgets.index(g)+1][0:1] != '0x'):
                g_new = g + gadgets[gadgets.index(g)+1]
                gadgets.remove(gadgets[gadgets.index(g)+1])
                gadgets_fixed.append(g_new)
                continue
            gadgets_fixed.append(g)
        return gadgets_fixed
    
    ## Small utility function to strip newlines out of list items
    def _strip_newlines(self,LIST):
        '''FOR INTERNAL USE ONLY
            this function is not meant to be called by the user
        '''
        for item in LIST:
            item.replace('\n','') 
            if item == '\n':
                LIST.remove(item)
        return LIST
   
    def _find_baseaddr(self):
        '''FOR INTERNAL USE ONLY
            this function is not meant to be called by the user
        '''
        tmp_path = HOME_DIR + '/lddtmp'
        ldd_comm = ['ldd',self.path]
        rm_comm = ['rm',tmp_path]
        tmp_out = open(tmp_path,'w')
        subprocess.call(ldd_comm, stdout=tmp_out)
        tmp_out.close()
        tmp_out.open(tmp_path,'r')
        raw_lines = tmp_out.readlines()
        tmp_out.close()
        os.remove(HOME_DIR + '/lddtmp')
        for line in lines:
            if line.find('libc') == 1:
                target = line
                parts = target.split(' ')
                libc_base_raw = parts[3]
                libc_base = libc_base_raw.split('(')[1].split(')')[0]
                return libc_base
        print 'ERROR: Problem finding libc'
        return None

    ## FIXME: This function is meant to parse the assembly into various
    ## independent functions.
    def _parse_asm(self):
        print 'TODO' 
        functions = []
        for line in self.assembly:
            print 'nothing'
   
    ## FIXME: This function will attempt to enumerate traversals through menus in the
    ## form of input strings/sequences.
    def _enum_menu_strings(self):
        print 'TODO'

    ## Returns just the directory from the provided path
    def _get_path_dir(self):
        p = self.path
        path_dir = self.path[0:self.path.rfind('/')+1]
        return path_dir

    def _brute_eip_dist(self):
        '''_brute_eip_dist
            This function makes an attempt to brute force a binary with the De Bruijn
            sequence and uses the returned core (if generated) to calculate the distance
            to eip. This will ONLY work for binaries that take the vulnerable buffer as
            their first input, as such menued applications will not work for this. In
            addition this tends to only work on applications in which stack-protection
            is left off.

            [!!] THIS METHOD IS INTERNAL AND NOT MEANT TO BE CALLED BY THE USER
        '''
        path = self.path
        path_dir = self.path_dir
        p = pt.process(path)
        try:
            os.remove(path_dir + 'core')
            os.remove(HOME_DIR + '/tmpcore')
        except OSError:
            pass
        p.sendline(pt.cyclic(10000))
        try:
            _ = open('core')
            _.close()
            os.system('cp core ' + HOME_DIR + '/tmpcore')
            os.system('gdb -q -c ' + HOME_DIR + '/tmpcore' + ' -batch > ~/tmpcoredmp')
            os.remove(HOME_DIR + '/tmpcore')
            _ = open(HOME_DIR + '/tmpcoredmp')
            lines = _.readlines()
            addr_raw = '' 
            crashaddr = int(lines[len(lines)-1].split('  ')[1].split(' ')[0],16)
            dist_eip = pt.cyclic_find(crashaddr) - 4
            return dist_eip
        except IOError:
            print 'ERROR: Failure to generate core from simple method'
            print '       Program likely has a menu of some sort'
            return None

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~{ Public Methods }~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

    def show_gadgets(self):
        '''show_gadgets
            This function is meant to display all of the gadgets in an organized 
            fashion. This is a small thing to just make sure you get lines printed
            rather than unreadable madness
        '''
        for g in self.gadgets:
            print g

    def show_poprets(self):
        '''poprets

           This function is meant to show the locations of pop x rets in the binary.
           It should show the number of pops and the address for later use with a
           gadget.
        '''
        print 'TODO'

    def printasm(self):
        for line in self.assembly:
            print line

    def create_chain(self, targets=[],argc=[], argv=[]):
        '''create_chain
            This function attempts to create and launch a crafted ROP attack. I will
            be moving this into its own module soon as I have a lot of features planned
            for it
        '''
        print 'TODO'
