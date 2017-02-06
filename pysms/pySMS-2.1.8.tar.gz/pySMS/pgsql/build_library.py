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

        library_stats = {'counts':
                             {'kit': self.total_kits,
                              'tray': self.total_tray,
                              'component': self.total_components,
                              'piece': self.total_pieces,
                              'pages': 0},
                         'totals':
                             {'items_written': 0,
                              'biomet': 0,
                              'zimmer': 0},
                         'books': [],
                         'errors':
                             {'count': 0,
                              'reasons': []}}

        print(Fore.LIGHTCYAN_EX + 'Building ci_data_library.json')
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

                try:
                    if key not in library_stats['books']:
                        library_stats['books'].append(str(key))
                    else:
                        continue

                    type_of_item = str(key.split('_')[:1])

                    if type_of_item == 'kit':
                        self.total_kits += 1
                    elif type_of_item == 'tray':
                        self.total_tray += 1
                    elif type_of_item == 'component':
                        self.total_components += 1
                    elif type_of_item == 'piece':
                        self.total_pieces += 1


                    library_stats['counts']['pages'] = int(library_stats['counts']['pages']) + 1
                    library_stats['totals'][str(item[_ids['legacy_type']]).lower()] = int(library_stats['totals'][str(item[_ids['legacy_type']]).lower()]) + 1
                    library_stats['totals']['items_written'] = int(library_stats['totals']['items_written']) + 1
                except Exception as e:
                    err = {'msg': 'An error occurred while writing page',
                           'book': key,
                           'traceback': str(e),
                           'page': str(item[_ids['product_number']])}

                    library_stats['errors']['count'] += 1
                    library_stats['errors']['reasons'].append(err)

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

        print(Fore.LIGHTYELLOW_EX + 'Books:')
        for stuff in library_stats['books']:
            print(Fore.LIGHTYELLOW_EX + '> ' + Fore.LIGHTCYAN_EX + stuff)

        print(Fore.LIGHTYELLOW_EX + 'Item Type Counts:')
        for k, v in library_stats['counts'].items():
            print(Fore.LIGHTYELLOW_EX + "Total " + k + " count: " + Fore.LIGHTCYAN_EX + str(v))

        print(Fore.LIGHTYELLOW_EX + 'Total items written: ' + Fore.LIGHTCYAN_EX + str(library_stats['totals']['items_written']))
        print(Fore.LIGHTYELLOW_EX + 'Total legacy zimmer items: ' + Fore.LIGHTCYAN_EX + str(library_stats['totals']['zimmer']))
        print(Fore.LIGHTYELLOW_EX + 'Total legacy biomet items: ' + Fore.LIGHTCYAN_EX + str(library_stats['totals']['biomet']))

        print(Fore.LIGHTYELLOW_EX + "Total errors: " + Fore.LIGHTRED_EX + str(library_stats['errors']['count']))

        if library_stats['errors']['count'] != 0:
            if input('View Errors? Y/N: ').upper() == 'Y':
                for _dict in library_stats['errors']['reasons']:
                    print(Fore.LIGHTRED_EX + _dict['msg'] + ": " +
                          Fore.LIGHTYELLOW_EX + _dict['page'] + ". " +
                          Fore.LIGHTRED_EX + "Book: " + Fore.LIGHTRED_EX + _dict['book'] + "." +
                          Fore.LIGHTRED_EX + " :: " + Fore.RED + _dict['traceback'])


def main():
    sD = structData()
    sD.check_for_old_library()

    sD.load_data()
    sD.build_library()
    sD.close_conn()
    
if __name__ == '__main__':
    main()    
