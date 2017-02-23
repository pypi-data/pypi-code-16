
import sys
import os
import xml.etree.ElementTree as ET

level = [[0], [0], [0]]

def escape_check(input_str):                                                                                                                                                                            
   
    flag = 0 
    if(len(input_str) != 0 and input_str[0] == '"' and input_str[-1] == '"'):
        input_str = input_str[1:-1]
        flag = 1

    ### 0. 'true' and 'false' will transform into 'TRUE' and 'FALSE' automatically in google sheet.    
    if(input_str == '-true-'):
        return 'true'
    elif(input_str == '-false-'):
        return 'false'
 
    ### 1. remove 7 spaces before the string to avoid symbols missing in google sheet.
    if(input_str.find('       ') == 0):
        input_str = input_str[7:]

    ### 2. single ['] and ["] should be escaped.
    ### chr(92) = '\'
    block = input_str.split("'")
    input_str = block[0]
    for i in range(1, len(block)):
        if(len(input_str) == 0 or input_str[-1] != chr(92)):
            input_str += chr(92)
        input_str += "'" + block[i]
    
    block = input_str.split('"')
    input_str = block[0]
    for i in range(1, len(block)):
        if(len(input_str) == 0 or input_str[-1] != chr(92)):
            input_str += chr(92)
        input_str += '"' + block[i]
    
    if(flag == 1):
        input_str = '"' + input_str + '"'

    return input_str


def check_strings_file(file1, file2):
    
    global level

    print('[#] check : "' + file1 + '" and "' + file2 + '"')

    name_string = {}
    tree1 = ET.parse(file1)
    root1 = tree1.getroot()        
    for child in root1:
        tag_attrib = '' + str(child.tag) + ' ' + str(child.attrib)
        if(name_string.get(tag_attrib) == None):
            name_string[tag_attrib] = {}
            name_string[tag_attrib]['file2'] = '[[[Not exist]]]'
        name_string[tag_attrib]['file1'] = child.text

    tree2 = ET.parse(file2)
    root2 = tree2.getroot()
    for child in root2:
        tag_attrib = '' + str(child.tag) + ' ' + str(child.attrib)
        if(name_string.get(tag_attrib) == None):
            name_string[tag_attrib] = {}
            name_string[tag_attrib]['file1'] = '[[[Not exist]]]'
        name_string[tag_attrib]['file2'] = child.text
   
    flag = 0 
    for key in name_string.keys():

        text1 = name_string[key]['file1']
        text2 = name_string[key]['file2']

        if(level[0] == 1):
            if('"' + text1 + '"' == text2):
                continue
            elif('"' + text2 + '"' == text1):
                continue

        if(level[1] == 1):
            if(escape_check(text1) == text2):
                continue
            elif(escape_check(text2) == text1):
                continue
                     
        if(level[0] == 1 and level[1] == 1):
            if('"' + escape_check(text1) + '"' == text2):
                continue
            elif('"' + escape_check(text2) + '"' == text1):
                continue

        if(level[2] == 1):
            if(text1 == '[[[Not exist]]]' and (text2 == '' or text2 == '""')):
                continue
            elif(text2 == '[[[Not exist]]]' and (text1 == '' or text1 == '""')):
                continue
            
        if(text1 != text2):
        
            print('\033[1;31m\n' + key)
            print('file1: ' + text1.encode('utf-8'))
            print('file2: ' + text2.encode('utf-8'))
        #    print('file1: ' + escape_check(text1.encode('utf-8')) + '\033[1;m')
            flag = 1            

    if(flag == 1):
        return 1
    return 0
    
def check_file_content(dir_name, dir1, dir2):

    dir_list1 = os.listdir(dir1 + '/' + dir_name)
    dir_list2 = os.listdir(dir2 + '/' + dir_name)
    
    flag = 0
    for name in dir_list1:
        file1 = dir1 + '/' + dir_name + '/' + name
        file2 = dir2 + '/' + dir_name + '/' + name
 
        if(name == 'strings.xml'):
            flag += check_strings_file(file1, file2)
        #    print('do nothing.')
        else:
            print('[#] check : "' + file1 + '" and  "' + file2 + '"\033[1;31m')
            a = os.system('diff -r ' + file1 + ' ' + file2)
            if(a != 0):
                flag += 1
            print('\033[1;m')

    if(flag > 0):
        return 1
    return 0

if __name__ == '__main__':

    if(len(sys.argv) > 2):
        dir1 = sys.argv[1]
        dir2 = sys.argv[2]
        if(dir1[-1] == '/'):
            dir1 = dir1[:-1]
        if(dir2[-1] == '/'):
            dir2 = dir2[:-1]
    else:
        exit()

    if('-1' in sys.argv):
        level[0] = 1
    if('-2' in sys.argv):
        level[1] = 1
    if('-3' in sys.argv):
        level[2] = 1

    dir_list1 = os.listdir(dir1)
    dir_list2 = os.listdir(dir2)
    total_dir = []
    for name in dir_list1:
        total_dir.append(name)

    for dir_name in dir_list2:
        if((dir_name not in total_dir) == True):
            total_dir.append(dir_name)

    start_string = 'Start checking ' + dir1 + ' and ' + dir2

    print('\n\033[1;34m     ' + '#' + '-'*(len(start_string) + 2) + '#')
    print('     | ' + start_string + ' |')
    print('     #' + '-'*(len(start_string) + 2) + '#' + '\n\033[1;m')

    
    final_flag = 0
    for dir_name in total_dir:
       
        flag1 = 0
        if((dir_name in dir_list1) == True):
            flag1 = 1
        
        flag2 = 0
        if((dir_name in dir_list2) == True):
            flag2 = 1

        if(flag1 == 1 and flag2 == 1):
            print('[#] dir1 and dir2 both have: ' + dir_name )
            if(check_file_content(dir_name, dir1, dir2) == 0):
                print('\033[1;32m[+] OK!\n\033[1;m')
            else:
                print('\033[1;31m\n[-] Not good!\n\033[1;m')
                final_flag = 1
        else:
            if(flag1 == 1):
                print('\033[1;31m[-] only appear in dir1: ' + dir_name + ' \033[1;m')
            if(flag2 == 1):
                print('\033[1;31m[-] only appear in dir2: ' + dir_name + ' \033[1;m')
            print('\033[1;31m[-] Not good!\n\033[1;m')
            final_flag = 1

    if(final_flag == 0):
        print('\033[1;32m[+] Final result: ' + dir1 + ' and ' + dir2 + ' are totally the same.\n\033[1;m')
    else:
        print('\033[1;31m[-] Final result: There is something different.\n\033[1;m')

