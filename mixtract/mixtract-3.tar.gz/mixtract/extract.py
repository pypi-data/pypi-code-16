"""Extract Mixpanel data as JSONL files."""
import os
import sys
import requests
from requests.auth import HTTPBasicAuth

from mixtract.__init__ import API_VERSION, config


def secret_key(project_name=None):
    """Return the Mixpanel API secret key.

    Keyword argument:
    project_name -- Name of the project. Defaults to None.

    secret_key returns a dict of project name / secret key
    pairs. If no project name is given, it retrieves secret
    keys for all projects specified in the configuration
    YAML file.
    """
    secret_keys = {}

    try:
        for item in config['secret_keys']:
            secret_keys = {**secret_keys, **item}
    except KeyError:
        print("The configuration file does not include a secret_keys section.")
        sys.exit(1)

    if project_name is not None:
        try:
            return {project_name: secret_keys[project_name]}
        except KeyError:
            print(("The Mixpanel API secret key for {project_name} "
                  "is not found in the configuration file.").format(
                      project_name=project_name))
            sys.exit(1)
    else:
        return secret_keys


def write_to_file(secret_key_dict, start_date, end_date):
    """Retrieve Mixpanel data as JSONL file.

    Keyword arguments:
    secret_key_dict -- dict of project name / secret key key-value pairs.
    start_date -- start of the date range to collect information.
    end_date -- end of the date range (not inclusive).

    write_to_file queries the Mixpanel API and saves the
    resulting JSON strings on data/raw/{project_name}.jsonl
    """
    for project in secret_key_dict:
        print("Retrieving Mixpanel data for {project}".format(
            project=project))

        data_dir = os.path.join(os.getcwd(), 'data/raw/')
        if not os.path.isdir(data_dir):
            os.makedirs(data_dir, exist_ok=True)

        filename = data_dir + project + '.jsonl'

        print("The raw JSON data will be stored at: {filename}".format(
            filename=filename))

        with open(filename, 'w') as f:
            date = start_date
            total_line_counter = 0

            while date < end_date:
                date_string = str(date.date())
                print("Retrieving data for {date_string}...".format(
                    date_string=date_string), end='')
                r = _mixpanel_request(secret_key_dict[project], date_string)

                date_line_counter = 0
                for line in r.iter_lines():
                    date_line_counter += 1
                    total_line_counter += 1
                    f.write(line.decode('utf-8') + '\n')

                _print_line_counter(date_line_counter)

                date = date.shift(days=+1)

        print("Done retrieving data for {project}.".format(
            project=project), end='')
        _print_line_counter(total_line_counter, newline=False)
        print("on {filename}.".format(filename=filename))

    return None


def _mixpanel_request(api_secret_key, date_string):
    api_path = ("https://data.mixpanel.com/api/{version}/export?"
                "from_date={from_date}&to_date={to_date}")
    api_path = api_path.format(
            version=API_VERSION,
            from_date=date_string,
            to_date=date_string)

    r = requests.get(api_path, auth=HTTPBasicAuth(api_secret_key, ''))
    r.raise_for_status()
    return r


def _print_line_counter(counter, newline=True):
    print(counter, end='')
    if counter <= 1:
        print(' line', end='')
    else:
        print(' lines', end='')
    if newline:
        print(' written.')
    else:
        print(' written.', end='')
