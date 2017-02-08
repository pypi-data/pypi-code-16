#encoding=utf-8
import sqlite3
class MemDataStore:
    def __init__(self, data_file=":memory:" ):
        self.conn = sqlite3.connect(data_file,check_same_thread=False)
        self.conn.isolation_level = None
        race_common_fields ='''belong varchar(2),
            country varchar(10),location varchar(50),
            race_date varchar(10),race_type varchar(10),
            card_list varchar(500),tote_list varchar(50),
            timeout int'''

        '赛事列表'
        self.conn.execute('''create table if not exists races( id integer primary key,%s);''' %race_common_fields)

        '赌吃数据'
        self.conn.execute( '''create table if not exists wp_eatbet (
            id integer primary key,key varchar(100),
            race_num int,horse_num int,
            location varchar(50),tote_code varchar(10),
            bet_type varchar(10),belong varchar(10),
            win int,place int,discount float,
            lwin float,lplace float);''')

    def connect(self):
        return self.conn.cursor()
