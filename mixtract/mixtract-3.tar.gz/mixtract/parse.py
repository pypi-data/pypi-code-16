"""Parse JSONL files to extract a relational dataset."""

import json
import pandas as pd
import pickle
import os
import sys


def dataframe(project_name, serialize=False):
    """Return a nested Pandas dataframes containing the Mixpanel data.

    Keyword arguments:
    project_name -- Specify the project to parse through.
    serialize -- Specify whether the Pandas dataframe should be
    serialized as a pickle file. Defaults to False.

    dataframe parses through the Mixpanel JSONL files to build Pandas
    dataframes, containing the entirety of the fetched Mixpanel data
    for the project. The raw data is assumed to be stored in ./data/raw.
    The return value is a Pandas dataframe with two columns, event
    and dataframe, and each event dataframe contains the data
    corresponding to the properties of the event.

    Note that it is possible to extract the schema from the returned
    Pandas dataframe. If the Pandas dataframe for a project has already
    been computed, run schema_from_dataframe instead of schema
    to avoid duplicate work.
    """
    data_dir = os.path.join(os.getcwd(), 'data/raw/')
    project_path = data_dir + project_name + '.jsonl'
    print("Building dataframes for {project}...".format(project=project_name))

    events = {}

    with open(project_path, 'r') as jsonl:
        print('Parsing through the raw data...')

        for line in jsonl:
            j = json.loads(line)

            if j['event'] not in events:
                print('Event {event} discovered.'.format(event=j['event']))
                events[j['event']] = []

            events[j['event']].append(j['properties'])

    event_dataframe = []
    for event in events:
        event_dataframe.append(
                {'event': event, 'dataframe': pd.DataFrame(events[event])})

    project_dataframe = pd.DataFrame(event_dataframe)
    project_dataframe.df_name = project_name

    if serialize:
        serialize_dir = os.path.join(os.getcwd(), 'data/serialized')

        if not os.path.isdir(serialize_dir):
            os.makedirs(serialize_dir, exist_ok=True)

        pickled_path = serialize_dir + '/' + project_name + '_dataframe.p'

        with open(pickled_path, 'wb') as p:
            print("Saving the dataframe as a serialize file... ", end='')
            pickle.dump(project_dataframe, p)
            print("Saved at: {pickled}.".format(pickled=pickled_path))

    return project_dataframe


def load_serialized_dataframe(project_name):
    """Load project dataframe from a serialized file.

    Keyword argument:
    project_name -- name of the project whose dataframe is to be loaded.

    load_serialized_dataframe is a wrapper on pickle.load. Beyond
    loading the serialized file into memory, it also defines the
    df_name attribute of the dataframe, which does not persist through
    a serialization-deserialization process. df_name is set to be
    the string passed through as project_name.
    """

    try:
        pickled_path = os.path.join(os.getcwd(), 'data/serialized/')
        pickled = pickled_path + project_name + '_dataframe.p'
        with open(pickled, 'rb') as f:
            project_dataframe = pickle.load(f)
    except FileNotFoundError:
        print(("The parsed dataframe for {project_name} "
              "is not found in {file_path}").format(
                  project_name=project_name, file_path=pickled_path))
        sys.exit(1)

    project_dataframe.df_name = project_name
    return project_dataframe


def schema_from_dataframe(project_dataframe, serialize=False):
    """Return a dict of events / properties dicts for a project.

    Keyword arguments:
    project_dataframe -- Pandas dataframe containing the whole data.
    serialize -- Specify whether the dict should be serialized as
    a pickle file. Defaults to False.

    schema_from_dataframe parses through the project dataframe
    to extract event / properties schema, without going through
    the raw data file again.
    """
    events = {}

    for _, row in project_dataframe.iterrows():
        events[row['event']] = list(row['dataframe'].columns)

    if serialize:
        serialize_dir = os.path.join(os.getcwd(), 'data/serialized')

        if not os.path.isdir(serialize_dir):
            os.makedirs(serialize_dir, exist_ok=True)

        project_name = project_dataframe.df_name
        pickled_path = serialize_dir + '/' + project_name + '_schema.p'

        with open(pickled_path, 'wb') as p:
            print("Saving the schema as a serialize file... ", end='')
            pickle.dump(events, p)
            print("Saved at: {pickled}.".format(pickled=pickled_path))

    return events
