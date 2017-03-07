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
Command line interface for Nervana's deep learning cloud.
"""
from builtins import object
from collections import namedtuple
from datetime import datetime
import inspect
import logging
import os
import requests

from ncloud.completers import DirectoriesCompleter
from ncloud.formatting.output import print_table
from ncloud.formatting.time_zone import utc_to_local
from ncloud.vendor.python.argparse import ArgumentTypeError
from ncloud.util.api_call import api_call, api_call_json
from ncloud.util.sys_commands import create_all_dirs


logger = logging.getLogger()


# command constants
Cmd = namedtuple('Cmd', ['name', 'aliases'])
LS = Cmd('ls', ('list', 'l'))
SHOW = Cmd('show', ('s',))
UL = Cmd('ul', ('upload', 'u'))
LN = Cmd('ln', ('link', 'k'))
RM = Cmd('rm', ('remove',))
ADD = Cmd('add', ('a',))
MODIFY = Cmd('modify', ('m',))
TRAIN = Cmd('train', ('t',))
START = Cmd('start', ())
STOP = Cmd('stop', ())
RESULTS = Cmd('results', ('res', 'r'))
IMPORT = Cmd('import', ('i',))
DEPLOY = Cmd('deploy', ('d',))
PREDICT = Cmd('predict', ('p',))
UNDEPLOY = Cmd('undeploy', ('ud', 'u'))
ADDGRP = Cmd('addgrp', ('addgroup', 'ag'))
RMGRP = Cmd('rmgrp', ('removegroup', 'rmg', 'rg'))
PWRST = Cmd('pwrst', ('pwreset', 'pr'))
HIST = Cmd('history', ('hist', 'h'))


def string_argument(string):
    if len(string) > 255:
        raise ArgumentTypeError('"%s" must be less than 255 characters.' %
                                string)
    return string


def iso_8601_argument(date):
    try:
        return datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        msg = "Not a valid date: {}. Need YYYY-MM-DD format.".format(date)
        raise ArgumentTypeError(msg)


class Choices(object):
    """class used to specify what choices for a
       command arg should be allowed
    """
    def __init__(self, choices):
        self.choices = choices

    def __iter__(self):
        yield self

    def __contains__(self, key):
        return key in self.choices

    def __repr__(self):
        # can't have brackets with argparse in add_argument
        # see https://bugs.python.org/issue14046
        # return str(self.choices)
        return ', '.join([str(x) for x in self.choices])


class Command(object):

    # used in multiple inheritance, like List --> BaseList --> Command
    BASE_ARGS = []

    @classmethod
    def parser(cls, subparser):
        raise NotImplementedError("provide a subparser for your command")

    @classmethod
    def arg_names(cls, startidx=1):
        return inspect.getargspec(cls.call).args[startidx:]

    @staticmethod
    def call():
        raise NotImplementedError("provide an implementation for your command")

    @staticmethod
    def display_before(config, args):
        pass

    @staticmethod
    def display_after(config, args, res):
        if res is not None:
            print_table(res)

    @classmethod
    def arg_call(cls, config, args):
        arg_dict = vars(args)
        arg_vals = [arg_dict[name] for name in cls.arg_names()]
        # used with multiple inheritance args in the .call() funcs
        cls.BASE_ARGS = {name: arg_dict[name] for name in cls.BASE_ARGS}
        cls.display_before(config, args)
        res = cls.call(config, *arg_vals)

        cls.display_after(config, args, res)

        # reset the base args, if any
        cls.BASE_ARGS = []


class BaseList(Command):
    """Provides universal functionality to listing various objects
    """
    BASE_ARGS = {'count': 10, 'offset': None, 'asc': None}

    @classmethod
    def parser(cls, subparser, help_text, desc):
        list_objects = subparser.add_parser(LS.name, aliases=LS.aliases,
                                            help=help_text, description=desc)
        list_objects.add_argument("-n", "--count", type=int, default=10,
                                  help="Show up to n objects. Without the "
                                       "--asc flag, returns most recent "
                                       "objects. For unlimited set n=0. Can "
                                       "be used alongside the offset arg to "
                                       "implement pagination of objects "
                                       "returned. Ex: `ncloud m ls -o 25 "
                                       "-n 10` would return objects 16-25, "
                                       "and `ncloud m ls -o 25 -n 10 --asc` "
                                       "would return objects 25-34.")
        list_objects.add_argument("-o", "--offset", type=int,
                                  help="Where in the object pagination to "
                                       "start next. Represents an object id "
                                       "to return the next newest X results, "
                                       "where X = count. Used as a way to "
                                       "paginate object listings.")
        list_objects.add_argument("--asc", action="store_true",
                                  help="Displays objects in ascending "
                                       "order instead of the default "
                                       "descending order.")
        return list_objects


class Results(Command):
    """
    Model results: Retrieve results files -- model weights, callback outputs
    and neon log.
    Dataset results: Retrieve the original dataset in various formats.
    Batch prediction results: Retrieve metadata and output files.
    Interactive session results: Retrieve log files.
    """
    def __init__(self, object_name, object_id_completer, url_path):
        """
            object_name: used to say what kind of results we are fetching
            url_path: used to determine what endpoint to hit
            object_id_completer: used to autocomplete object ids when hitting
                                 tab to see what you can get results for
        """
        self.object_name = object_name
        self.url_path = url_path
        self.object_id_completer = object_id_completer

    def parser(self, subparser):
        results_parser = subparser.add_parser(RESULTS.name,
                                              aliases=RESULTS.aliases,
                                              help=Results.__doc__,
                                              description=Results.__doc__)
        results_parser.add_argument(
            "object_id",
            help="ID of {} to retrieve results of.".format(self.object_name)
        ).completer = self.object_id_completer
        results_parser.add_argument(
            "-d", "--directory",
            help="Location to download files {directory}/results_files. "
                 "Defaults to current directory."
        ).completer = DirectoriesCompleter
        results_parser_mode = results_parser.add_mutually_exclusive_group()
        results_parser_mode.add_argument(
            "-u", "--url", action="store_true", help="Obtain URLs to "
            "directly download individual results.")
        results_parser_mode.add_argument(
            "-o", "--objects", action="store_true", help="Download objects "
            "directly to specified directory.")
        results_parser_mode.add_argument(
            "-z", "--zip", action="store_true", help="Retrieve a zip file "
            "of results.")
        results_parser_mode.add_argument(
            "-t", "--tar", action="store_true", help="Retrieve a tar file "
            "of results.")
        results_parser.add_argument(
            "-f", "--filter", action='append', help="Only retrieve files "
            "with names matching <filter>.  Note - uses glob style syntax. "
            "Multiple --filter arguments will be combined with logical or.")

        results_parser.set_defaults(
            func=self.arg_call, url_path=self.url_path)

    @staticmethod
    def call(config, object_id, filter=None, zip=None, tar=None,
             url=None, objects=None, directory=None, url_path=None):
        object_id = str(object_id)

        vals = {}
        results_path = os.path.join(url_path, object_id, "results")
        if filter:
            vals["filter"] = filter

        results = None
        if url or objects:
            vals["format"] = "url"
            results = api_call_json(config, results_path, params=vals)
            if objects:
                directory = directory if directory else '.'
                for result in results["result_list"]:
                    obj = requests.get(result["url"], stream=True)
                    local_file = os.path.join(directory, result["filename"])
                    create_all_dirs(local_file)
                    with open(local_file, 'wb') as f:
                        for chunk in obj.iter_content(chunk_size=1024):
                            if chunk:
                                f.write(chunk)
                return
        elif zip or tar:
            if zip:
                ext = "zip"
                stream = False
            else:
                ext = "tar"
                stream = True
            vals["format"] = ext
            results = api_call(config, results_path, params=vals,
                               stream=stream)
            if results:
                directory = directory if directory else '.'
                if not os.path.exists(directory):
                    os.makedirs(directory)
                filename = (
                    'results_%d_%s.%s' % (
                        int(object_id),
                        datetime.strftime(datetime.today(), "%Y%m%d%H%M%S"),
                        ext
                    )
                )

                with open(os.path.join(directory, filename), 'wb') as f:
                    if stream:
                        for chunk in results.iter_content(chunk_size=1024):
                            if chunk:
                                f.write(chunk)
                        return
                    else:
                        f.write(results)
        else:
            # default to listing results
            vals["format"] = "list"
            results = api_call_json(config, results_path, params=vals)
            if results and 'result_list' in results:
                result_list = results['result_list']
                for result in result_list:
                    result['last_modified'] = \
                        utc_to_local(result["last_modified"])

        return results

    @staticmethod
    def display_after(config, args, res):
        if res and 'result_list' in res:
            if args.url:
                print("Public URLs will expire 1 hour from now.")
            print_table(res['result_list'])


class NoRespCommand(Command):
    @staticmethod
    def display_after(config, args, res):
        if not res:
            print_table({"error": "Error: no response from Helium"})
        else:
            print_table(res)


def build_subparser(name, aliases, hlp, classes, subparser):
    parser = subparser.add_parser(name, aliases=aliases, help=hlp,
                                  description=hlp)
    subsubparser = parser.add_subparsers(title=name + ' operations')
    for cls in classes:
        cls.parser(subsubparser)
