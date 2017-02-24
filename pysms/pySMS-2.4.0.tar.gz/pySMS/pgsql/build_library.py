# -*- coding: utf-8 -*-
"""
Created on Wed Dec 28 07:33:37 2016

@author: doarni
"""

import json
import os
import time
import gzip
import getpass
import datetime
import pySMS.pgsql.load_data as load_data

from colorama import init, Fore
init(autoreset=True)


class structData():
    
    def __init__(self):
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.db = load_data.data_builder()
        self.dict = None
        self.total_kits = 0
        self.total_tray = 0
        self.total_components = 0
        self.total_pieces = 0

    def get_time_elapsed(self, start_time):  # elapsed time
        return str(datetime.timedelta(seconds=(time.time() - start_time)))

    def get_current_time(self):
        return time.time()
        
    def check_for_old_library(self):
        if os.path.isfile(os.sep.join(["C:", "Users", getpass.getuser(),  "Desktop"]) + '\\ci_data_library.json')  == True:
            print(Fore.LIGHTRED_EX + 'A previous library has been found. ' + os.sep.join(["C:", "Users", getpass.getuser(),  "Desktop"]) + '\\ci_data_library.json')
            print(Fore.LIGHTRED_EX + 'Would you like to remove this library?')

            if input('Y/N: ').upper() == 'Y':
                os.system('del /s /q ' + os.sep.join(["C:", "Users", getpass.getuser(),  "Desktop"]) + '\\ci_data_library.json')
            else:
                print(Fore.LIGHTRED_EX + 'ci_data_library.json will be overwritten.')
        
    def close_conn(self):
        self.db.close_pgsql()
        
    def load_data(self):
        self.db.load_pgsql()
        self.db.load_ci_data()
        self.dict = self.db.return_ci_data()

    def build_library(self): #build collection of product type specific dictionaries
        _ids = {'legacy_type': 0,'item_id': 5, 'product_number': 2, 'edi_number': 3, 'description': 4, 'inv_type': 1}
        dict = self.dict  
        library = {}

        print(Fore.LIGHTCYAN_EX + 'Building ci_data_library.json')

        start_time = self.get_current_time()

        for key, val in dict.items():
            print('')    
            print(Fore.LIGHTYELLOW_EX + 'Building book: ' + key)  
            book = {}
            pages = {}
            print(Fore.LIGHTYELLOW_EX + 'Writing book: ' + key)
            for item in val:
                print(Fore.LIGHTCYAN_EX + 'With book ' + key + Fore.LIGHTYELLOW_EX +
                      Fore.LIGHTYELLOW_EX + ' Writing page: ' + Fore.CYAN + str(item[_ids['product_number']]) +
                      Fore.LIGHTYELLOW_EX + ' Legacy Type: ' + Fore.CYAN + str(item[_ids['legacy_type']]) +
                      Fore.LIGHTYELLOW_EX + ' Description: ' + Fore.CYAN + str(item[_ids['description']]))
                pages[str(item[_ids['product_number']])] = {'data_parent': key,
                                                            'inv_type': str(item[_ids['inv_type']]),
                                                            'item_id': str(item[_ids['item_id']]),
                                                            'legacy_type': item[_ids['legacy_type']],
                                                            'edi_number': item[_ids['edi_number']],
                                                            'description': item[_ids['description']]}
            
            book[key] = pages
            print('')
            print(Fore.LIGHTYELLOW_EX + 'Adding book: ' + Fore.CYAN + key + Fore.LIGHTYELLOW_EX + ' to library')
            library[key + '_book'] = book
            time.sleep(3)

        print('')
        print('')
        desktop = os.sep.join(["C:", "Users", getpass.getuser(),  "Desktop"])
        print(Fore.LIGHTGREEN_EX + 'Library Complete.')
        print('Writing ci_data_library.json')
        with open(desktop + '\\ci_data_library.json', 'w')as fp:
            json.dump(library, fp, sort_keys=False, indent=5)

        print(Fore.LIGHTGREEN_EX + 'Converting library.')
        print('Writing ci_data_library.json.gz')

        data_obj = json.dumps(library).encode('utf-8')

        with gzip.open(desktop + '\\ci_data_library.json.gz', 'wb')as f:
            f.write(data_obj)

        print(Fore.LIGHTGREEN_EX + 'Complete.')

        print(Fore.LIGHTYELLOW_EX + "Library Build Report:")

        total_time = self.get_time_elapsed(start_time)

        print(Fore.LIGHTYELLOW_EX + "Total elapsed time: " + Fore.LIGHTMAGENTA_EX + str(total_time))



def main():
    sD = structData()
    sD.check_for_old_library()

    sD.load_data()
    sD.build_library()
    sD.close_conn()
    
if __name__ == '__main__':
    main()    
