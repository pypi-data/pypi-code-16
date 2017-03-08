# -*- coding: utf-8 -*-
"""
Created on Wed Dec 28 07:33:37 2016

@author: doarni
"""

import os
from pySMS.pgsql.postgres import Postgres as Postgres
from colorama import init, Fore
init(autoreset=True)

class data_builder():
    
    def __init__(self):

        self.path = os.path.dirname(os.path.realpath(__file__))
        self.ci_kit_data_file = self.path + "\\sql\\ci_kit_data.sql"
        self.ci_piece_data_file = self.path + "\\sql\\ci_piece_data.sql"
        self.ci_component_data_file = self.path + "\\sql\\ci_component_data.sql"
        self.ci_tray_data_file = self.path + "\\sql\\ci_tray_data.sql"

        self.ci_kit_data = None
        self.ci_component_data = None
        self.ci_piece_data = None
        self.ci_tray_data = None
        
        self.pgsql = None
        
    def load_pgsql(self):
        self.pgsql = Postgres()
        self.pgsql.load_postgres_data()
        self.pgsql.test_connection()
        self.pgsql.establish_connection()
        
    def close_pgsql(self):
        if self.pgsql == None:
            print(Fore.LIGHTRED_EX + 'Postgres is not connected')
        else:
            self.pgsql.close_connection()
        
    def load_ci_query_text(self):
        kit_query_txt = ""
        tray_query_txt = ""
        component_query_txt = ""
        piece_query_txt = ""
        
        #load kit query text
        with open(self.ci_kit_data_file, 'r')as f:
            kit_query_txt = f.read().replace('\n', ' ')
        kit_query_txt = kit_query_txt.replace('\t', ' ')
        kit_query_txt = kit_query_txt[3:]
        
        #load tray query text
        with open(self.ci_tray_data_file, 'r')as f:
            tray_query_txt = f.read().replace('\n', ' ')
        tray_query_txt = tray_query_txt.replace('\t', ' ')
        tray_query_txt = tray_query_txt[3:]        
        
        #load component query text
        with open(self.ci_component_data_file, 'r')as f:
            component_query_txt = f.read().replace('\n', ' ')
        component_query_txt = component_query_txt.replace('\t', ' ')
        component_query_txt = component_query_txt[3:]

        #load piece query text
        with open(self.ci_piece_data_file, 'r')as f:
            piece_query_txt = f.read().replace('\n', ' ')
        piece_query_txt = piece_query_txt.replace('\t', ' ')
        piece_query_txt = piece_query_txt[3:]
               
        return {"kit": kit_query_txt,
                "tray": tray_query_txt,
                "component": component_query_txt,
                "piece": piece_query_txt}

    def load_ci_data(self):
        dict = self.load_ci_query_text()
        
        print(Fore.LIGHTYELLOW_EX + 'Loading data.')

        print(Fore.LIGHTYELLOW_EX + 'Loading kit data')
        self.ci_kit_data = self.pgsql.execute(dict['kit'])
        print(Fore.LIGHTGREEN_EX + 'Data loaded.\n')

        print(Fore.LIGHTYELLOW_EX + 'Loading component data.')
        self.ci_component_data = self.pgsql.execute(dict['component'])
        print(Fore.LIGHTGREEN_EX + 'Data loaded.\n')

        print(Fore.LIGHTYELLOW_EX + 'Loading piece data.')        
        self.ci_piece_data = self.pgsql.execute(dict['piece'])
        print(Fore.LIGHTGREEN_EX + 'Data loaded.\n')

        print(Fore.LIGHTYELLOW_EX + 'Loading tray data.')       
        self.ci_tray_data = self.pgsql.execute(dict['tray'])       
        print(Fore.LIGHTGREEN_EX + 'Data loaded.\n')
        
    def return_ci_data(self):
        return {"kit_data": self.ci_kit_data,
                "piece_data": self.ci_piece_data,
                "tray_data": self.ci_tray_data,
                "component_data": self.ci_component_data}
