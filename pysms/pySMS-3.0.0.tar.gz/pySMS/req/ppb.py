# -*- coding: utf-8 -*-
import os
import sys
import zipfile
from colorama import init, Fore
init(autoreset=True)

class installer():
    def __init__(self):
        self.path = os.path.dirname(os.path.realpath(__file__))
    
    def readZipFile(self, file):   
        with zipfile.ZipFile(file, "r") as f:
            i = 1
            for name in f.namelist():
                print(str(i) + ') ' + name)
                i += 1
            print(Fore.LIGHTYELLOW_EX + 'Files in ' + file + ': ' + Fore.LIGHTCYAN_EX + str(i - 1))
                
    def unzip(self, file, target):
        with zipfile.ZipFile(file,"r") as zip_ref:
            zip_ref.extractall(target)
            
            
    def compileFile(self, file, location):
        print(Fore.LIGHTYELLOW_EX + 'Compiling: ' + Fore.LIGHTCYAN_EX + file)
        os.system("pyinstaller --specpath " + location + " --distpath " + location + "//dist --workpath " + location + "//build " + file)

    def pipInstallUpdateList(self, list, singleItem=False):
        for module in list:
            print(Fore.LIGHTYELLOW_EX + 'Installing: ' + Fore.LIGHTCYAN_EX + module)
            os.system("pip install " + module + " --no-cache-dir")
        for module in list:
            print(Fore.LIGHTYELLOW_EX + 'Updating: ' + Fore.LIGHTCYAN_EX + module)
            os.system("pip install " + module + " --upgrade --no-cache-dir")            
    
    def pipInstallUpdateItem(self, module):
        print(Fore.LIGHTYELLOW_EX + 'Installing: ' + Fore.LIGHTCYAN_EX + module)
        os.system("pip install " + module + " --no-cache-dir")
        print(Fore.LIGHTYELLOW_EX + 'Updating: ' + Fore.LIGHTCYAN_EX + module)
        os.system("pip install " + module + " --upgrade --no-cache-dir")            
     
    def pipInstallWheels(self, location, wheel):
        print(Fore.LIGHTYELLOW_EX + 'Installing: ' + Fore.LIGHTCYAN_EX + wheel)
        os.system("pip install " + location + " --no-cache-dir")     
        
    def writeBatLauncher(self, location, batFileName, pyFileName):
        with open(location + '\\' + batFileName,'w')as f:
            f.write('cd ' + location + ' & python ' + pyFileName)
        f.close()
        
       
if __name__ == '__main__':
    
    import argparse
    inst = installer()
    
    parser = argparse.ArgumentParser(description = '[PPB] Python Program Builder. A simple installer built with Python 3.5.6')
    
    parser.add_argument('-u','--unzip', nargs=2, help='Unzip files from zipfile to directory' , required=False, metavar=('[FILE]', '[DESTINATION]'))
    parser.add_argument('-c','--compile', nargs=2, help='Compile given file to exe using pyinstaller', required=False, type=str,metavar=('[FILE]' ,'[DESTINATION]'))
    parser.add_argument('-p','--parse', nargs=1, help='Parse files in zip file and print to console', required=False, metavar='[FILE]')
    parser.add_argument('-e','--update', nargs='+', help='Install and update a list of modules. use /f to supply a txt file', required=False, metavar='[LIST OF MODULES]')
    parser.add_argument('-w','--wheel', nargs=2, help='Install Wheel', required=False, metavar=('[PATH]', '[WHEEL]'))
    parser.add_argument('-b','--create-bat-file', nargs=3, help='Create batch file to launch python script', required=False, metavar=('[DESTINATION]','[BAT FILE NAME]','[PY FILE NAME]'))
    parser.add_argument('-os','--os-call-process', nargs='+', help='Run OS Command', required=False, metavar=('[COMMAND]', '[INPUT 1] [INPUT 2] [SWITCH1.SWITCH2.ECT]'))
    parser.add_argument('-md','--mkdir', nargs=1, help='Make Directory', required=False, metavar='[DIRECTORY PATH]')    
    parser.add_argument('-rd','--rmdir', nargs=1, help='Remove Directory', required=False, metavar='[DIRECTORY PATH]')    
    parser.add_argument('-del','--del', nargs=2, help='Delete item', required=False, metavar=('[SWITCH1.SWITCH2.SWITCH3.ect]', '[FILE]'))
    
    args = vars(parser.parse_args())
        
    if args['mkdir']:
        os.mkdir(args['mkdir'][0])
        
    if args['rmdir']:
        os.rmdir(args['rmdir'][0])        
    
    if args['del']:
        list = args['del'][0].split('.')
        switches = '/' + ' /'.join(list)
        os.system('del ' + switches + ' ' + args['del'][1])   
    
    if args['unzip']:
        if '.zip' not in args['unzip'][0]:
            print(Fore.LIGHTRED_EX + 'A zip file is required')
            sys.exit()
        else:
            if args['unzip'][1] == os.path.dirname(os.path.realpath(__file__)):
                print(Fore.LIGHTRED_EX + 'Can not unzip files to current directory')
            else:
                print('Unzipping ' + args['unzip'][0] + ' to ' + args['unzip'][1])
                inst.unzip(args['unzip'][0],args['unzip'][1])
    
    if args['compile']:
        inst.compileFile(args['compile'][0], args['compile'][1])
       
    if args['os_call_process']:
        if args['os_call_process'][0].lower() == 'xcopy':
            list = args['os_call_process'][3].split('.')
            switches = ' /'.join(list)
            os.system('xcopy ' + args['os_call_process'][1] + ' ' + args['os_call_process'][2] + ' /' + switches)
        else:
            print(Fore.LIGHTRED_EX + 'No Command Supplied')
            
    if args['parse']:
        print('Files in ' + args['parse'][0] + ':')
        inst.readZipFile(args['parse'][0])

    if args['update']:
        if args['update'][0].lower() == '/f':
            if '.txt' not in args['update'][1]:
                print(Fore.LIGHTRED_EX + 'File supplied not a .txt file')
            else:
                file = args['update'][1]
                list = [line.strip() for line in open(file)]
                for item in list:
                    inst.pipInstallUpdateItem(item)
        else:            
            inst.pipInstallUpdateList(args['update'])
        
    if args['wheel']:
        inst.pipInstallWheels(args['wheel'][0], args['wheel'][1])
        
    if args['create_bat_file']:
        inst.writeBatLauncher(args['create_bat_file'][0],
                              args['create_bat_file'][1],
                              args['create_bat_file'][2])