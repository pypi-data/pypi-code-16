#encoding=utf-8
import sqlite3
class MemDataStore:

    def __init__(self, data_file=":memory:" ):
        self.data_file = data_file
        self.conn = sqlite3.connect(self.data_file,check_same_thread=False)
        self.conn.isolation_level = None
        cursor = self.conn.cursor()
        cursor.execute('''create table if not exists summary_trans_hist(
         id integer primary key, country varchar(10),
         race_type varchar(10),location varchar(50), volume float,
         key varchar(100),  profit float, tax float ,
         tote_name varchar(10), belong varchar(10), up_line varchar(20))''')

        cursor.execute('''create table if not exists trans_hist(
         id integer primary key,
         location varchar(50), race_type varchar(10),
         race_num int,horse_num int,
         win float, place float, discount float,lwin float, lplace float,
         bet_type varchar(10),position int, win_dividend float,
         place_dividend float, profit float);''')

        def connect(self):
            return self.conn.cursor()
