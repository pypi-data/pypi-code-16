import sys, os, os.path, collections
import tarfile, json
from fnmatch import fnmatch
import io

import colorama
from tabulate import tabulate

import bag as bag
from bag import Bag, MongoConnectionInfo
import dependencies


silent=False

class MoveOp:
    def __init__(self, source, destination):
        self.source = source
        self.destination = destination
        
    def __eq__(self, other):
        return self.source == other.source
        
    def __hash__(self):
        return self.source.__hash__()
        
def move_ops (instructions, relative_path=''):
    """ensure move operation from package/unpackage instructions are unique.
    Consider that move operations are considered equal if they share the source. That is you can't pack
    the same file into two different places neighter you can unpack the same file in multiple places.
    A move operation from successive instruction in the list will overrid any previous one.
    """
    
    ops = set()
    for i in instructions:
        ops = ops.difference(i.file_op())   # abort any previous discovered move operation on same source
        ops = ops.union(i.file_op())

    return ops

class PackageInstruction:
    def __init__(self, source_folder, filter, destination_folder):
        self.source_folder = os.path.normpath(source_folder)
        self.destination_folder = os.path.normpath(destination_folder)
        self.filter = filter
    

    def accept_file(self, file_name):
        """Use the filter regular exception to check if the received filename is ineresting or not"""
        file_name = os.path.basename(file_name)
        return fnmatch (file_name, self.filter)
    
    def file_op(self, relative_path=""):
        """
        This function recursivelly create and yield MoveOp to command a move from a source folder to a destination one given a filter on files to consider.
        
        yield MoveOp corresponding to a move operation of files. 
        Source path is absolute and obtained chaining
            source_path + relative_path
        where relative_path is the path traversed untill now by this recursive function
        Destination path is obtained chaining 
            destination_path + relative_path
            
        """
        ops = []
        path = os.path.join(self.source_folder , relative_path)
        # a first filter on file from current folder to get candidate to be packed.
        acceptable_generic_files =  [f for f in os.listdir(path) if self.accept_file(f)]
        
        # for each regular file, move and append on the package
        for file_name in [real_file for real_file in acceptable_generic_files if not os.path.isdir(os.path.join(path,real_file))]:
            accepted_file = (os.path.join(relative_path , file_name))
            ops.append(MoveOp(   os.path.join(self.source_folder, accepted_file), 
                                 os.path.join(self.destination_folder, accepted_file))
                       )
            
        # recursivelly process inner folders except special files of course
        folders = [folder for folder in os.listdir(path)  if os.path.isdir(os.path.join(path,folder)) and folder not in ['.','..']  ]

        for folder_name in folders:
            ops += self.file_op(os.path.join(relative_path, folder_name))
            
        return ops
        

def pack(source, destination, filter = '*'):
    """sugar to build MoveOp using a verb"""
    return PackageInstruction(source, filter, destination)
    
unpack = pack


        
    

def gz_package(package_instructions, shelf=None, mem=None):
    """
    Builds a tar.gz package using the received instructions at path indicated by shelf.
    In the proposed methafor, place the package on the shelf following the received instructions.
    """
    
    package = tarfile.open ( shelf, 'w:bz2', fileobj=mem)
        
    repath_log = []
    for op in move_ops(package_instructions):
        package.add( op.source, op.destination)
        repath_log.append( (op.source, op.destination) )
    package.close()
    
    # print the operation log
    if not silent:
        print (tabulate(repath_log, headers= ['', 'saved in']))
    
def gz_unbox(unbox_instructions, package_path=None, mem=None):
    """
    Unpack files from the received package 
    and move them according to the unboxing instructions received
    """
    
    has_common_prefix = os.path.commonprefix
    unbox_log = []
    with tarfile.open(package_path, 'r:bz2', mem) as package:
        for instruction in unbox_instructions:
            source = instruction.source_folder
            for m in [member for member in package.getmembers() if has_common_prefix([source, member.path]) == source]:
                new_path = instruction.destination_folder + m.path[len(source):]
                unbox_log.append ( (m.path, new_path) )
                m.path = new_path
        
        
        package.extractall()
        
    # print the operation log
    print (tabulate(unbox_log, headers= ['', 'unboxed in']))
    return [move[1] for move in unbox_log]
    
def load_metadata(file_path='meta.json') :
    """Load metadata from a json file on disk in the form of a dictionary."""
    with open(file_path) as data_file:    
        meta = json.load(data_file)
    
    return meta
     
def charge(instructions=None, metainfo=None, json=None, file =None, db_connection_info=MongoConnectionInfo()):
    if(json):
        charge_json(json, db_connection_info=db_connection_info)
    elif(instructions and metainfo):
        charge_low_level(instructions, metainfo, db_connection_info=db_connection_info )
    elif(file):
        charge_json_file(file, db_connection_info=db_connection_info)
   
def charge_low_level(instructions, metainfo, db_connection_info=MongoConnectionInfo()):
    package_content = io.BytesIO()
    connected_bag = Bag(db_connection_info)
    if connected_bag.check(metainfo):
        raise bag.YetInBag(metainfo)
    gz_package(package_instructions = instructions, mem = package_content)
    connected_bag.charge(package_content.getvalue(), metainfo)
    
    if not silent:
        print ("package was " + str(int(len(package_content.getvalue()) / 1024)) + "kB") 

def charge_json_file(path, db_connection_info=MongoConnectionInfo()):
    f = open(path, "r")
    charge_json(f.read(), db_connection_info=db_connection_info)
    f.close()
    
    
def charge_json(json_text, db_connection_info=MongoConnectionInfo()):
    jobject = json.loads(json_text)
    box_instructions_json = jobject["__BOX_INSTRUCTIONS__"]
    instructions = []
    for json_instruction in box_instructions_json:
        instructions.append( pack(json_instruction['FROM'], json_instruction['TO'], json_instruction['FILTER']))
    try:
        del jobject["__BOX_INSTRUCTIONS__"]
        del jobject["__UNBOX_INSTRUCTIONS__"]
    except KeyError:
        pass
        
    charge(instructions, jobject, db_connection_info=db_connection_info)
    
def deliver_one(instructions, meta_request, db_connection_info=MongoConnectionInfo()):
    
    connected_bag = Bag(db_connection_info)
    package = connected_bag.take(meta_request)
    package_content = io.BytesIO(package)
    return gz_unbox(unbox_instructions = instructions, mem = package_content)
    
def deliver(instructions, meta_requests, db_connection_info=MongoConnectionInfo()):
    """deliver artifacts defined by each of meta_requests then apply unbox instructions to each."""
    created_files = []
    connected_bag = Bag(db_connection_info)
    
    if isinstance(meta_requests, dict):
        print ('metarequest is a dict, let make a list!')
        meta_requests = [meta_requests]

    direct_requirements = [dependencies.Requirement(r) for r in meta_requests]
    meta_request = [dr.meta_request() for dr in direct_requirements]
    meta_requests, gr =connected_bag.requirements_discover( direct_requirements)
    print(
        'results from bag: ' + str(meta_requests) + '   ' + str(gr)
    )
    
    if isinstance(meta_requests, list):
        for r in meta_requests:
            print("REQUIRE> "+ str(r))
            created_files += deliver_one(instructions, r, db_connection_info=db_connection_info)
    else:
        print("REQUIRE FAILS> "+ str(meta_requests))
    
    return [s.replace('\\','/') for s in created_files], gr

def deliver_json(json_text, db_connection_info=MongoConnectionInfo()):
    jobject = json.loads(json_text)
    unbox_instructions_json = jobject["__UNBOX_INSTRUCTIONS__"]
    instructions = []
    for json_instruction in unbox_instructions_json:
        instructions.append( pack(json_instruction['FROM'], json_instruction['TO'], json_instruction['FILTER']))
    try:
        del jobject["__BOX_INSTRUCTIONS__"]
        del jobject["__UNBOX_INSTRUCTIONS__"]
    except KeyError:
        pass
    try:    
        files, gr = deliver(instructions, jobject["DEPENDENCIES"], db_connection_info=db_connection_info)
        print ("deliver log" )
        for f in files:
            print (str(f))
    except KeyError:
        print('no dependencies detected, nothing to deliver')
        return bag.no_dependencies()
    
    print()
    print("dependencies graph")
    print (bag.to_dot_string(gr))

    return   files, gr
            


if __name__ == '__main__':
    import time
    import cli

    start_time = time.time()
    
    arguments = cli.parser.parse_args(sys.argv[1:])
    print(dir(arguments))
    arguments.func(arguments)
    
    end_time = time.time()
    print( """Executed in """ + str(int( (end_time - start_time)) ) + " s")
