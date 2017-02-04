import jupyter_core.paths as jpaths
import glob
import os
import sys
import re

def valid_conf_file(file_name):
# replace with canonical config validation checker
    if not os.path.isfile(file_name):
        return False
    if os.path.splitext(file_name)[1]=='.py':
        return True
    if os.path.splitext(file_name)[1]=='.json':
        return True
    

canonical_names_regex = re.compile(r"jupyter_(\w*_|)config")

def valid_local_conf_file(file_path):
    file_name = os.path.splitext(os.path.split(file_path)[1])[0]
    return valid_conf_file(file_path) and canonical_names_regex.match(file_name)
    
def search_jupyter_paths(search_term=''):
    
    conf_path_list = []
    for dir in jpaths.jupyter_config_path():
        conf_path_list.extend(glob.glob(dir+"/**", recursive=True))
        
    conf_file_list = [f for f in conf_path_list if valid_conf_file(f)]
    local_path_list = glob.glob(os.getcwd()+"/**", recursive=True)
    
    conf_file_list.extend([f for f in local_path_list if valid_local_conf_file(f)])
    
    # go through files, 
    # if search term found in file
    # print name, line_no, content 
    conf_file_list.reverse()
    for file_name in conf_file_list:
        if len(search_term)>0:
            print_indexed_content(file_name=file_name, search_term=search_term)
        else:
            print(file_name)
        
def print_indexed_content(file_name='', search_term=''):
    with open(file_name,"r") as f:
        if search_term in f.read():
            f.seek(0)
            line_numbers_match = []
            for line_no, text in enumerate(f,1):
                if search_term in text:
                    line_numbers_match.append((line_no,text.strip()))
            output = ["{}: {}".format(x,y) for x,y in line_numbers_match]
            print(file_name + "\n" + "\n".join(output),"\n")

def main():
    if len(sys.argv)==1:
        search_jupyter_paths()
    elif len(sys.argv)==2:
        search_jupyter_paths(sys.argv[1])
    else:
        raise RuntimeError("You can only pass in a single string at this time.")

if __name__ == "__main__":
    main()
