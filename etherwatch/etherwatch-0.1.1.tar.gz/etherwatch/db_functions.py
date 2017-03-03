# /usr/bin/env python

# Standard library
import sqlite3

# Database

# Create
class DatabaseFunctions:
    @staticmethod
    def create_database(db='ether.db'):
        conn = sqlite3.connect(db)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS ether
             (timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, price real)''')
        c.close()

    # Insert
    @staticmethod
    def log_price_datetime(price, db='ether.db'):
        conn = sqlite3.connect(db)
        c = conn.cursor()
        c.execute('INSERT INTO ether (price) VALUES (?)',  (price,) )
        conn.commit()
        c.close()

    # Get
    @staticmethod
    def get_price_log(db='ether.db'):
        conn = sqlite3.connect(db)
        c = conn.cursor()
        for row in c.execute('SELECT * FROM ether'):
            print(row)
        c.close()

    # Log
    @staticmethod
    def log_positions(eth_price):
        DatabaseFunctions.log_price_datetime(eth_price)
