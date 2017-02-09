"""Export parsed Mixpanel data to csv or a database."""

import os
import sqlalchemy
import sys
import re

from mixtract.__init__ import config


def to_csv(project_dataframe):
    """Export Mixpanel data to csv.

    Keyword argument:
    project_dataframe -- Pandas dataframe containing the Mixpanel data.

    to_csv creates a csv file, one for each event, in data/parsed/.
    """
    data_dir = os.path.join(os.getcwd(), 'data/parsed/')
    if not os.path.isdir(data_dir):
        os.makedirs(data_dir, exist_ok=True)

    for _, row in project_dataframe.iterrows():
        event_name = row['event']
        event_dataframe = row['dataframe']
        csv_filename = (data_dir + project_dataframe.df_name
                        + '_' + _sanitize(event_name) + '_parsed.csv')
        event_dataframe.to_csv(csv_filename)

    return None


def _sanitize(string):
    string = string.lower().replace(' ', '_')
    return re.sub(r'[!@#$%^&*()/\;:{}[]|]+=<>?', '_', string)


def to_mysql(project_dataframe):
    """Export Mixpanel data to MySQL.

    Keyword argument:
    project_dataframe -- Pandas dataframe containing the mixpanel data.

    to_mysql exports the Mixpanel data to MySQL. Each event is converted
    to its own table. If the tables already exist, then the data is appended.
    """
    _export_to_db(project_dataframe, 'mysql')


def to_postgresql(project_dataframe):
    """Export Mixpanel data to PostgreSQL.

    Keyword argument:
    project_dataframe -- Pandas dataframe containing the mixpanel data.

    to_mysql exports the Mixpanel data to PostgreSQL. Each event is converted
    to its own table. If the tables already exist, then the data is appended.
    """
    _export_to_db(project_dataframe, 'postgresql')


def to_oracle(project_dataframe):
    """Export Mixpanel data to Oracle SQL.

    Keyword argument:
    project_dataframe -- Pandas dataframe containing the mixpanel data.

    to_mysql exports the Mixpanel data to Oracle SQL. Each event is converted
    to its own table. If the tables already exist, then the data is appended.
    """
    _export_to_db(project_dataframe, 'oracle')


def to_mssql(project_dataframe):
    """Export Mixpanel data to Microsoft SQL.

    Keyword argument:
    project_dataframe -- Pandas dataframe containing the mixpanel data.

    to_mysql exports the Mixpanel data to Microsoft SQL. Each event is
    converted to its own table. If the tables already exist, then the
    data is appended.
    """
    _export_to_db(project_dataframe, 'mssql')


def _export_to_db(project_dataframe, database):
    con = _db_connector(*_db_auth_info(database))
    for _, row in project_dataframe.iterrows():
        event_name = _sanitize(row['event'])
        event_dataframe = row['dataframe']

        print('Creating database table {event}...'.format(event=event_name))

        event_dataframe.to_sql(
                event_name, con, if_exists='append')
    return None


def _db_auth_info(database):
    db_info = {}
    try:
        for item in config[database]:
            db_info = {**db_info, **item}
    except KeyError:
        print(("The configuration file does not include a "
              "{database} section").format(database=database))
        sys.exit(1)

    try:
        db_user = db_info['db_user']
    except KeyError:
        print(("No db_user for {database} found in the "
              "configuration file.").format(database=database))
        sys.exit(1)

    try:
        db_pass = db_info['db_pass']
    except KeyError:
        print(("No db_pass for {database} found in the "
              "configuration file.").format(database=database))
        sys.exit(1)

    try:
        db_host = db_info['db_host']
    except KeyError:
        print(("No db_host for {database} found in the "
              "configuration file.").format(database=database))
        sys.exit(1)

    try:
        db_port = db_info['db_port']
    except KeyError:
        print(("No db_port for {database} found in the "
              "configuration file.").format(database=database))
        sys.exit(1)

    try:
        db_name = db_info['db_name']
    except KeyError:
        print(("No db_name for {database} found in the "
              "configuration file.").format(database=database))
        sys.exit(1)

    return (db_user, db_pass, db_host, db_port, db_name, database)


def _db_connector(db_user, db_pass, db_host, db_port, db_name, database):
    if db_user == '':
        engine_str = "{database}:///{db_name}".format(
                database=database, db_name=db_name)
    else:
        engine_str = ("{database}://{db_user}:{db_pass}@{db_host}:{db_port}"
                      "/{db_name}").format(
                              database=database, db_user=db_user,
                              db_pass=db_pass, db_host=db_host,
                              db_port=db_port, db_name=db_name)
    return sqlalchemy.create_engine(engine_str).connect()
