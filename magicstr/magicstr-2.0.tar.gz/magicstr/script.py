
import os
import sys


if __name__ == '__main__':

    if(len(sys.argv) > 1):
        flag = sys.argv[1]
    else:
        exit()

    url = 'https://docs.google.com/spreadsheets/d/1cWOg2FZpUKjtQEqQdHXp7O9yXuqRLRzXYnlSsklP8-0/edit'
    origin = '../MB_strings/'

    if(flag == '1'):

        print('[Check Correctness]')
        os.system('rm -r ./MB_version1')
        os.system('rm -r ./MB_version2')
        os.system('python AutoNameString.py upload -i ../MB_strings/ -n MB_origin -u ' + url)
        os.system('python AutoNameString.py download -i ../MB_strings/ -n MB_origin -o MB_version1 -u ' + url)
        os.system('python AutoNameString.py upload -i ./MB_version1 -n MB_version1 -u ' + url)
        os.system('python AutoNameString.py download -i ./MB_version1 -n MB_version1 -o MB_version2 -u ' + url)

        os.system('python checker.py ../MB_strings ./MB_version1 -1 -2 -3')
        os.system('python checker.py ./MB_version1 ./MB_version2 -1 -2 -3')
        
    elif(flag == '2'):

        if(len(sys.argv) > 3):
            name_1 = sys.argv[2]
            name_2 = sys.argv[3]
        else:
            name_1 = 'MB_origin'
            name_2 = 'MB_version1'

        print('[Check Google Sheets Correctness]')
        os.system('rm -r ./MB_version1')
        os.system('rm -r ./MB_version2')
        os.system('python AutoNameString.py download -n ' + name_1 + ' -o MB_version1 -u ' + url)
        os.system('python AutoNameString.py download -n ' + name_2 + ' -o MB_version2 -u ' + url)
        os.system('python checker.py ./MB_version1 ./MB_version2 -1 -2 -3')

    elif(flag == '3'):
        print(flag)
