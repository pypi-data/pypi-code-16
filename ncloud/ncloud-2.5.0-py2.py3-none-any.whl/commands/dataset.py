# ----------------------------------------------------------------------------
# Copyright 2015-2016 Nervana Systems Inc.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ----------------------------------------------------------------------------
"""
Subcommands for managing datasets used for batch predictions.
"""
from __future__ import print_function
from builtins import str

import os
import queue
from functools import partial
from collections import OrderedDict

from ncloud.commands.command import (BaseList, Command, Results,
                                     string_argument, build_subparser,
                                     SHOW, UL, LN, RM)
from ncloud.util.api_call import api_call, api_call_json
from ncloud.config import DATASETS
from ncloud.util.file_transfer import parallel_upload, upload_file
from ncloud.formatting.output import print_table
from ncloud.formatting.time_zone import utc_to_local
from ncloud.completers import DatasetCompleter, DirectoriesCompleter


class List(BaseList):
    """
    List available datasets.
    """
    @classmethod
    def parser(cls, subparser):
        dataset_list = super(List, cls).parser(
            subparser, List.__doc__, List.__doc__)
        dataset_list.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config):
        vals = List.BASE_ARGS
        return api_call_json(config, DATASETS, params=vals)

    @staticmethod
    def display_after(config, args, res):
        if res:
            print_table(res['datasets'])


class Show(Command):
    """
    Show dataset details for a given dataset ID.
    """
    @classmethod
    def parser(cls, subparser):
        dataset_show = subparser.add_parser(SHOW.name, aliases=SHOW.aliases,
                                            help=Show.__doc__,
                                            description=Show.__doc__)
        dataset_show.add_argument(
            "dataset_id", help="ID of dataset to show details of."
        ).completer = DatasetCompleter
        dataset_show.add_argument("-r", "--rename",
                                  type=string_argument,
                                  help="Rename a dataset.")

        dataset_show.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, dataset_id, rename=None):
        show_path = os.path.join(DATASETS, dataset_id)
        if rename:
            vals = {"operation": "replace", "name": rename}
            res = api_call_json(config, show_path, method="PATCH", data=vals)
        else:
            res = api_call_json(config, show_path)

        for tm in ["created_at", "last_modified"]:
            if tm in res and res[tm] is not None:
                res[tm] = utc_to_local(res[tm])

        return res


class Upload(Command):
    """
    Upload a custom dataset to Nervana Cloud.
    """
    @classmethod
    def parser(cls, subparser):
        dataset_upload = subparser.add_parser(UL.name, aliases=UL.aliases,
                                              help=Upload.__doc__,
                                              description=Upload.__doc__)
        dataset_upload.add_argument(
            "directory",
            help="Directory path of the data. Uploads "
                 "all visible files recursively."
        ).completer = DirectoriesCompleter
        dataset_upload.add_argument("-n", "--name",
                                    help="Colloquial name of the dataset. "
                                         "Default name will be given if not "
                                         "provided.")
        # this is now a no-op; it will be the default option passed
        # to ncloud ds u
        dataset_upload.add_argument("-r", "--raw", action="store_true",
                                    help="Deprecated (ignored)", default=True)
        dataset_upload.add_argument("--follow-symlinks", action="store_true",
                                    help="follow symlinks while recursively "
                                         "enumerating files in the directory "
                                         "to upload.")
        dataset_upload.add_argument(
            "-i", "--dataset-id", default=None, type=str,
            help="Add data to an existing dataset "
                 "with this id.  This will replace identically-named files."
        ).completer = DatasetCompleter

        dataset_upload.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, directory, name=None, raw=True, dataset_id=None,
             follow_symlinks=False):
        vals = {"preprocess": False}
        if name:
            vals["name"] = name

        if dataset_id is None:
            create_dataset = api_call_json(config, DATASETS, method="POST",
                                           data=vals)
            if "id" not in create_dataset:
                print("Could not create dataset.")
                return

            dataset_id = str(create_dataset["id"])
            print("Created dataset with ID {}.".format(dataset_id))

        upload_queue = queue.Queue()

        if os.path.isdir(directory):
            def walk_generator():
                return os.walk(directory, followlinks=follow_symlinks)

            total_files = len([f for _, _, filelist in walk_generator()
                               for f in filelist if f[0] != '.'])

            for dirpath, _, filenames in walk_generator():
                filenames = [f for f in filenames if f[0] != '.']
                reldir = os.path.relpath(dirpath, directory)
                reldir = reldir if reldir != "." else ""
                for filename in filenames:
                    relfile = os.path.join(reldir, filename)
                    filepath = os.path.join(directory, relfile)
                    upload_queue.put((dataset_id, relfile, filepath))

            success, failed = parallel_upload(config, upload_queue,
                                              total_files)
        else:
            total_files = 1
            success, failed = 0, 0
            filename = os.path.basename(directory)
            try:
                upload_file(config, dataset_id, filename, directory)
                success = 1
            except SystemExit:
                failed = 1
        # a regular dict has inconstent behavior across python 2 and 3
        output = OrderedDict([
            ("id", dataset_id),
            ("success", success),
            ("failed", failed),
            ("total_files", total_files)
        ])
        return output

    @staticmethod
    def display_after(config, args, res):
        print_table(res)


class Link(Command):
    """
    Link a dataset not residing in the Nervana Cloud.
    """
    @classmethod
    def parser(cls, subparser):
        dataset_link = subparser.add_parser(LN.name, aliases=LN.aliases,
                                            help=Link.__doc__,
                                            description=Link.__doc__)
        dataset_link.add_argument("directory",
                                  help="Network path of the data root "
                                       "directory.")
        dataset_link.add_argument("-n", "--name",
                                  help="Colloquial name of the dataset. "
                                       "Default name will be given if not "
                                       "provided.")
        dataset_link.add_argument("-r", "--raw", action="store_true",
                                  help="Deprecated (ignored)", default=True)
        dataset_link.add_argument("-e", "--region",
                                  help="Region in which dataset resides.  "
                                       "For S3, defaults to us-west-1")

        dataset_link.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, directory, name=None, raw=False, region=None):
        vals = {"location_path": directory, "preprocess": False}

        if name:
            vals["name"] = name

        if region:
            vals["region"] = region

        res = api_call_json(config, DATASETS, method="POST", data=vals)
        return res

    @staticmethod
    def display_after(config, args, res):
        print_table(res)


class Remove(Command):
    """
    Remove a linked or uploaded dataset.
    """
    @classmethod
    def parser(cls, subparser):
        dataset_remove = subparser.add_parser(RM.name, aliases=RM.aliases,
                                              help=Remove.__doc__,
                                              description=Remove.__doc__)
        dataset_remove.add_argument(
            "dataset_id", help="ID of dataset to remove."
        ).completer = DatasetCompleter

        dataset_remove.set_defaults(func=cls.arg_call)

    @staticmethod
    def arg_names():
        return ['dataset_id']

    @staticmethod
    def call(config, dataset_id):
        res = api_call(config, DATASETS + dataset_id, method="DELETE")
        return res

    @staticmethod
    def display_after(config, args, res):
        print_table(res)


DatasetResults = Results(
    "dataset",
    DatasetCompleter,
    DATASETS
)
parser = partial(
    build_subparser, 'dataset', ['ds', 'd'], __doc__,
    (List, Show, Upload, Link, Remove, DatasetResults)
)
