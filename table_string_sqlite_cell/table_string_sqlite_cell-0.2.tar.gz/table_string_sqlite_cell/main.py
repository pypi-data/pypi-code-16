#!/usr/bin/env python

import argparse

import pandas as pd
import sqlalchemy

def main():
    parser = argparse.ArgumentParser('table_name and cell_value to sqlite cell')
    parser.add_argument('--cell_value',
                        required = True
    )
    parser.add_argument('--table_name',
                        required = True
    )

    args = parser.parse_args()
    cell_value = args.cell_value
    table_name = args.table_name

    sqlite_name = 'output.db'
    engine_path = 'sqlite:///' + sqlite_name
    engine = sqlalchemy.create_engine(engine_path, isolation_level='SERIALIZABLE')

    data_dict = dict()
    df = pd.DataFrom(data_dict)
    df['value'] = cell_value
    df.to_sql(table_name, engine)
    return

if __name__ == '__main__':
    main()
