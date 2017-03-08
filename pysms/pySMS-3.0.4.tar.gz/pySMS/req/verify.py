# -*- coding: utf-8 -*-
"""
Created on Thu Dec 15 15:35:33 2016

@author: doarni
"""
import os
from time import sleep
from colorama import init, Fore

init(autoreset=True)

i_path_ = os.path.dirname(os.path.realpath(__file__))

def return_modpath():
    os.chdir(i_path_)
    os.chdir('..')
    return os.getcwd()
    
i_path = return_modpath()
os.chdir('..')



global_file_dict = {'html_files': ['adjustment.html',
                                   'casepage.html',
                                   'login.html',
                                   'main.html',
                                   'orderpage.html',
                                   'orderpageline.html',
                                   'userpage.html'],        
                    'pyi_path_files': ['adjustStock.py',
                                      'loginPage.py',
                                      'mainPage.py',
                                      'prodChooser.py',
                                      'siteSettings.py',
                                      'stockTab.py',
                                      'stockTabMutate.py',
                                      'stockTabTable.py',
                                      'userSettings.py'],        
                    'jsoni_path_files': ['adjustStock.json',
                                        'loginPage.json',
                                        'mainPage.json',
                                        'prodChooser.json',
                                        'siteSettings.json',
                                        'stockTab.json',
                                        'stockTabMutate.json',
                                        'stockTabTable.json',
                                        'userSettings.json'],
                    'paths': {'main': i_path,
                              'excel': {'path': i_path + '\\excel',
                                         'ui': i_path + '\\excel\\ui'},
                              'html': {'path': i_path + '\\html',
                                        'pathdata': i_path + '\\html\\pathdata',
                                        'json': i_path + '\\html\\pathdata\\json'},
                              'pgsql': {'path': i_path + '\\pgsql',
                                        'sql': i_path + '\\pgsql\\sql'},
                              'req': {'path': i_path + '\\req'},
                              'ui': {'path': i_path + '\\ui'}},
                    'critical_files': {'main': ['__init__.py',
                                                'configparse.py',
                                                'hook.py',
                                                'keys.py',
                                                'livery.py',
                                                'messagebox.py',
                                                'prompts.py',
                                                'selenium.py',
                                                'chromedriver.exe'],
                                        'excel': ['loadFile.py',
                                                  'parseFile.py'],
                                        'html': ['get.py',
                                                 'build.py',
                                                 'parse.py',
                                                 'writeconfig.py'],
                                        'pgsql': ['build_library.py',
                                                  'cipher.py',
                                                  'load_data.py',
                                                  'postgres.py']}}


class Verify():
    
    def check_for_req_files():
        err_files = {}        
         
        def verFiles(_list, dir_name, key):
            os.chdir(dir_name)
            v_list = []
            unv_list = []
            list = [f for f in os.listdir(os.getcwd()) if os.path.isfile(os.path.join(os.getcwd(), f))]
            for req_f in _list:
                if req_f in list:
                    v_list.append(req_f)
                else:
                    unv_list.append(req_f)
            err_files[key] = {'unverified': unv_list, 'verified': v_list}

        os.chdir('..')
        
        verFiles(global_file_dict['html_files'], 'html', 'html')
        verFiles(global_file_dict['pyi_path_files'], 'pathdata', 'py')
        verFiles(global_file_dict['jsoni_path_files'], 'json', 'json')
        
        os.chdir(i_path_)
        
        return err_files
        
        
    def check_file_structure():
        
        v_list = []
        unv_list = []
        
        #checking for path structures
        for key,val in global_file_dict['paths'].items():
            if key == 'main':
                if os.path.exists(val) != True:
                    unv_list.append(val)
                else:
                    v_list.append(val)
            else:
                for k,v in val.items():
                    print(Fore.LIGHTYELLOW_EX +  'Verfiying ' + Fore.LIGHTCYAN_EX + '[' + Fore.LIGHTMAGENTA_EX + key + '' + Fore.LIGHTCYAN_EX + ']' + Fore.LIGHTYELLOW_EX + ' path: ' + Fore.LIGHTCYAN_EX + v)
                    sleep(0.1)

                    if os.path.exists(v) != True:
                        unv_list.append(v)
                        print(Fore.LIGHTYELLOW_EX + 'Path: ' + Fore.LIGHTCYAN_EX + v + Fore.LIGHTRED_EX + ' failed\n')
                        sleep(0.1)

                    else:
                        print(Fore.LIGHTYELLOW_EX + 'Path: ' + Fore.LIGHTCYAN_EX + v + Fore.LIGHTGREEN_EX + ' passed\n')
                        v_list.append(v)
                        sleep(0.1)

        
        return {'passed': v_list, 'failed': unv_list}
        
    def check_critical_files():
        
        crit_files_checked_out = []
        crit_files_not_checked_out = []
        
        def get_file_list(diri_path):
            return [f for f in os.listdir(diri_path) if os.path.isfile(os.path.join(diri_path, f))]
        
        def check_files(list, key):
            for file in global_file_dict['critical_files'][key]:
                if file in list:
                    print(Fore.LIGHTYELLOW_EX + 'File: ' + Fore.LIGHTCYAN_EX + file + Fore.LIGHTGREEN_EX + ' Verified')
                    print(Fore.LIGHTYELLOW_EX + 'Checking out: ' + Fore.LIGHTCYAN_EX + file)
                    sleep(0.1)
                    crit_files_checked_out.append(file)
                    print(Fore.LIGHTCYAN_EX + file + ' ' + Fore.LIGHTYELLOW_EX + 'Checked out\n')
                elif file not in list:
                    print(Fore.LIGHTYELLOW_EX + 'File: ' + Fore.LIGHTCYAN_EX + file + Fore.LIGHTRED_EX + ' Missing')
                    print(Fore.LIGHTCYAN_EX + file + ' ' + Fore.LIGHTRED_EX + 'was not checked out\n')
                    sleep(0.1)
                    crit_files_not_checked_out.append(file)
                    pass 
                
        check_files(get_file_list(global_file_dict['paths']['main']), 'main')
        check_files(get_file_list(global_file_dict['paths']['excel']['path']), 'excel')
        check_files(get_file_list(global_file_dict['paths']['html']['path']), 'html')
        check_files(get_file_list(global_file_dict['paths']['pgsql']['path']), 'pgsql')
        
        return {'checked_out': crit_files_checked_out, 'missing': crit_files_not_checked_out }
        
    def report(fdict, structdict, critdict):
        v_files = []
        unv_files = []
        
        missingi_paths = []
        vi_paths = []
        
        missing_crit_files = []
        v_crit_files = []
        
        print(Fore.LIGHTCYAN_EX + 'Verification report\n')
        sleep(0.1)

        #Print file Report
        print(Fore.LIGHTCYAN_EX + 'File Report:')
        for k, v in fdict.items():
            print('')
            if len(v['unverified']) != 0:
                print(Fore.LIGHTYELLOW_EX + 'Unverified ' + str(k) + ' files:')
                sleep(0.1)

                for f in v['unverified']:                
                    print(Fore.LIGHTRED_EX + f)
                    unv_files.append(f)
                    sleep(0.1)

            else:
                print(Fore.LIGHTYELLOW_EX + 'Verified ' + str(k) + ' files:')
                sleep(0.1)

                for f in v['verified']:        
                    v_files.append(f)
                    print(Fore.LIGHTGREEN_EX + f)
                    sleep(0.1)

        
        print('')
        #Print file struct report
        print(Fore.LIGHTCYAN_EX + 'Directory Structure Report:')
        sleep(0.1)

        for k, v in structdict.items():
            if k == 'failed':
                if len(v) != 0:
                    for fpath in v:
                        print(Fore.LIGHTRED_EX + 'Missing Path: ' + Fore.LIGHTCYAN_EX + fpath )
                        missingi_paths.append(fpath)
                        sleep(0.1)

            else:
                for fpath in v:
                    print(Fore.LIGHTYELLOW_EX + 'Path: ' + Fore.LIGHTCYAN_EX + fpath + Fore.LIGHTYELLOW_EX + ' Exists')
                    vi_paths.append(fpath)
                    sleep(0.1)

                    
        print('')
        #Print crit file report
        print(Fore.LIGHTCYAN_EX + 'Critical Files Report:')
        sleep(0.1)

        for k, v in critdict.items():
            if k == 'missing':
                if len(v) != 0:
                    for file in v:
                        print(Fore.LIGHTRED_EX + 'Missing Critical File: ' + Fore.LIGHTCYAN_EX + file )
                        missing_crit_files.append(file)
                        sleep(0.1)

            else:
                for file in v:
                    print(Fore.LIGHTYELLOW_EX + 'File: ' + Fore.LIGHTCYAN_EX + file + Fore.LIGHTYELLOW_EX + ' Exists')
                    v_crit_files.append(file)
                    sleep(0.1)

                    
        sleep(1)            
        #Cleanup report. Clean Print.
        print('\n\n')            
        print(Fore.LIGHTYELLOW_EX + 'Total Errors: ' + Fore.LIGHTRED_EX + str( len(unv_files) + len(missingi_paths) + len(missing_crit_files)))
        
        print('')
        print(Fore.LIGHTYELLOW_EX + 'Verified files: ' + Fore.LIGHTRED_EX + str( len(v_files) ))
        print(Fore.LIGHTYELLOW_EX + 'Unverified files: ' + Fore.LIGHTRED_EX + str( len(unv_files) ))

        print('')
        print(Fore.LIGHTYELLOW_EX + 'Verified Directories: ' + Fore.LIGHTRED_EX + str( len(vi_paths) ))
        print(Fore.LIGHTYELLOW_EX + 'Missing Directories: ' + Fore.LIGHTRED_EX + str( len(missingi_paths) ))

        print('')
        print(Fore.LIGHTYELLOW_EX + 'Verified Critical Files: ' + Fore.LIGHTRED_EX + str( len(v_crit_files) ))
        print(Fore.LIGHTYELLOW_EX + 'Missing Critical Files: ' + Fore.LIGHTRED_EX + str( len(missing_crit_files) ))
        
        print('')
        if len(missing_crit_files) != 0:
            print(Fore.LIGHTRED_EX + 'These files are missing and are critical to this programs functionality:')
            for file in missing_crit_files:
                print(Fore.LIGHTMAGENTA_EX + file)
        
        print('\n\n')            

def report():
    os.chdir(i_path_)
    fdict = Verify.check_for_req_files()
    structdict = Verify.check_file_structure()
    critdict = Verify.check_critical_files()
    
    Verify.report(fdict, structdict, critdict)
    
if __name__ == '__main__':
    
    
    
    import argparse
    
    parser = argparse.ArgumentParser(description = 'Build program latest version')
    parser.add_argument('-v','--verify', action='store_true', help='Verify file Structure', required=False)

    args = vars(parser.parse_args())
    
    if args['verify']:
        os.chdir(i_path_)
        
        report()

