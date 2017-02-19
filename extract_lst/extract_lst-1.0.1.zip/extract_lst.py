import glob, os, re
path=input("Enter Path: ")
if not path:
    path="C:\\Users\\Sid\\Documents"
#    path="C:\Users\Sidhant\Google Drive\College\Sem 2\Java\K"

#Finds Code snippet indicating it starts with a comment and ends till next "listing" is found.
def find_code(fil):
    start=fil.find("listing")
    if start == -1:
        return None, 0, None
    start_pos=fil.find('\n', start+1)
    str_num=fil[start:start_pos]
    list_num=str_num.split(sep=" ", maxsplit=1)
    if not len(list_num) <= 1:
        number=list_num[1]
    end=fil.find("listing", start+1)
    code=fil[start_pos+1:end]
    #print ("\nCode Starts==========================\n",code,"\nCode ends\n=========================================================")
    return code, end, number


#Finds all desierable code snippets
def find_all_codes(fil, f_name):
    wpath=path+"\\"+f_name
    if not os.path.exists(wpath):
        os.makedirs(wpath)
    codes=[]
    while True:
        code, endpos, file_number=find_code(fil)
        if (endpos>=(len(fil)-10)):
            break
        codes.append(code)
        fil=fil[endpos:]
        write_file(code, wpath, file_number)
    return codes

#Writes particular code snippet to the file, with the file name as of the class containing
#main method. Calls extract_name() .
def write_file(code, wpath, number):
    if code == None:
        return
    try:
        class_name=extract_name(code).lstrip()
        special_char=['<','@','(']
        for i in range(len(class_name)):
            if class_name[i] in special_char:
                class_name=class_name[:i]
                break           
            
        writepath=wpath+"\\"+str(number)+"."+class_name+".java"
        snippet=open(writepath, 'w')
        snippet.write(code)
        snippet.close()
    except AttributeError as error:
        print("Error Encountered- ", str(error), "\t at listing %s" %number)
        
#Extracts the class name from the snippet.
def extract_name(code):
    start=code.find('class')
    end=code.find('class', start+1)
    if end == -1:#If the snippet contains only one Class
        start_pos=code.find(" ", start)
        end_pos=code.find(" ", start_pos+1)
        if ' main' not in code[start:]:
            return
        return code[start_pos:end_pos]  #Returns Class Name      
    #If the cnippet contains more than one Classes
    temp_class=code[start:end]
    #print ("Temp Class Starts**********************\n",temp_class,"\nTemp Class ends************************")
    if ' main' not in temp_class:
        cod=code[end-2:]
        return extract_name(cod) #Desiered Class not found, calls itself with next class        
    else:  
        start_pos=code.find(" ", start)
        end_pos=code.find(" ", start_pos+1)
        return code[start_pos:end_pos] #Desiered Class found and returned

#Entry point for the program, changes current dir to the path given by the user.
#Then, reads and process each file with ".lst" extension.
def read_files():
    os.chdir(path)
    for file in glob.glob("*.lst"):
        folder_name=file[:file.find('.')]
        f = open(file, 'r')
        content = f.read()
        find_all_codes(content, folder_name)
