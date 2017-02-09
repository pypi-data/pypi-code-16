import arrow
import os

import mixtract.argparser as argparser
import mixtract.extract as extract
import mixtract.parse as parse
import mixtract.export as export


def execute():
    # Command-line UI
    args = argparser.parse()

    # Extract data from Mixpanel
    secret_key_dict = extract.secret_key(args.project)
    extract.write_to_file(secret_key_dict, arrow.get(args.start),
                          arrow.get(args.end))

    # Parse raw data and export to database.
    if args.project is not None:
        project_dataframe = parse.dataframe(args.project, args.serialize)
        _send_to_database(args.target, project_dataframe)
    else:
        for project in os.listdir(os.getcwd() + '/data/raw/'):
            project_name = project[:-6]
            project_dataframe = parse.dataframe(project_name, args.serialize)
            _send_to_database(args.target, project_dataframe)

    print("Done!")


def _send_to_database(target, dataframe):
    if target == 'csv':
        export.to_csv(dataframe)
    if target == 'mysql':
        export.to_mysql(dataframe)
    if target == 'postgresql':
        export.to_postgresql(dataframe)
    if target == 'oracle':
        export.to_oracle(dataframe)
    if target == 'mssql':
        export.to_mssql(dataframe)
