import argparse
import arrow
import sys


def parse():
    parser = argparse.ArgumentParser(
        description='Extract Mixpanel data and export to csv or database.')

    parser.add_argument('target', metavar='target', type=str,
                        help='csv, mysql, postgresql, oracle, mssql')
    parser.add_argument('start', metavar='start', type=str,
                        help='Start date for the range of data retrieval')
    parser.add_argument('end', metavar='end', type=str,
                        help='End date for the range of data retrieval')
    parser.add_argument('--project', metavar='name', type=str,
                        help='Specify the name of the project.')
    parser.add_argument('--serialize', dest='serialize',
                        action='store_const', const=True, default=False,
                        help='Serialize the data as a  Pandas dataframe.')

    args = parser.parse_args()

    # Check if the command-line arguments are valid
    if args.target not in {'csv', 'mysql', 'postgresql', 'oracle', 'mssql'}:
        print(("Error: target must be csv, mysql, "
              "postgresql, oracle, or mssql."))
        sys.exit(1)

    try:
        arrow.get(args.start)
    except:
        print(('Error: start date must be of the form YYYY-MM-DD, '
              'YYYY/MM/DD, or YYYY.MM.DD.'))
        sys.exit(1)

    try:
        arrow.get(args.end)
    except:
        print(('Error: end date must be of the form YYYY-MM-DD, '
              'YYYY/MM/DD, or YYYY.MM.DD.'))
        sys.exit(1)

    return args
