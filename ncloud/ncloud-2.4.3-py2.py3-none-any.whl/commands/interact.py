# ----------------------------------------------------------------------------
# Copyright 2015 Nervana Systems Inc.
# ----------------------------------------------------------------------------
"""
Subcommands for launching and managing interactive environments.
"""
import logging
from functools import partial
import os
import sys
import json
import time

import requests

from ncloud.commands.command import (BaseList, Command, Results,
                                     build_subparser, SHOW, START, STOP)
from ncloud.util.api_call import api_call_json, api_call
from ncloud.config import INTERACT
from ncloud.formatting.output import print_table
from ncloud.completers import InteractiveSessionCompleter

logger = logging.getLogger()


class Show(Command):
    """
    Show interactive session details.
    """
    @classmethod
    def parser(cls, subparser):
        interact = subparser.add_parser(SHOW.name, aliases=SHOW.aliases,
                                        help=Show.__doc__,
                                        description=Show.__doc__)
        interact.add_argument(
            "id", type=int,
            help="id of the interactive session to show details of."
        ).completer = InteractiveSessionCompleter
        interact.add_argument("-l", "--console-log", action="store_true",
                              help="Show console log from session runtime.")
        interact.add_argument('-L', "--console-log-follow",
                              action="store_true",
                              help="Show console log data as the " +
                                   "output grows; similar to tail -f " +
                                   "on a UNIX-based machine.")

        interact.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, id, console_log=False, console_log_follow=False):
        show_path = os.path.join(INTERACT, 'info', str(id))

        console_log |= console_log_follow

        if not console_log:
            return api_call_json(config, show_path)

        vals = {}
        show_path += "/launcher.log"

        # make the initial request of the object!
        # we will get back data in the format of:
        # {'results': FILE_DATA_HERE, 'offset': END_OF_FILE_HERE}
        # so we can fetch from the end of the file!
        # keep things in the same session so we can
        # make use of keep-alive
        sess = requests.session()
        # give some leeway for an interactive session that maybe didn't yet
        # start or a log not yet fully uploaded to s3
        log_maybe_finished = False
        while True:
            try:
                result, status_code = api_call(config, show_path,
                                               params=vals,
                                               stream=console_log_follow,
                                               session=sess,
                                               return_status_code=True)
                log_data = json.loads(result)
                # continue to print out the file data and request
                # the next part of the file!
                results = log_data['results']
                # where we will fetch next; might be reset
                offset = log_data['offset']

                # only print if we actually have more data
                if results:
                    print(results)
                # wait 2.5 sec before fetching more data again
                # if 200 status code, else break if 202
                if (log_maybe_finished and status_code == 202) or \
                        not console_log_follow:
                    break
                log_maybe_finished = status_code == 202
                time.sleep(2.5)
                vals['offset'] = offset
            except KeyboardInterrupt:
                # once the user terminates the program, exit gracefully
                sys.exit(0)


class Start(Command):
    """
    Launch an interactive ipython notebook environment.
    """
    @classmethod
    def parser(cls, subparser):
        interact = subparser.add_parser(START.name, aliases=START.aliases,
                                        description=Start.__doc__,
                                        help=Start.__doc__)
        interact.add_argument("-d", "--dataset-id",
                              help="ID of dataset to mount in notebook.")
        interact.add_argument("-f", "--framework-version",
                              help="Neon tag, branch or commit to use.")
        interact.add_argument("-i", "--resume-model-id",
                              help="Start training a new model using the state"
                                   " parameters of a previous one.")
        interact.add_argument("-g", "--gpus", default=1,
                              help="Number of GPUs to train this model with.")
        interact.add_argument("-u", "--custom-code-url",
                              help="URL for codebase containing custom neon "
                                   "scripts and extensions.")
        interact.add_argument("-c", "--custom-code-commit", default="master",
                              help="Commit ID or branch specifier for custom "
                                   "code repo.")
        interact.add_argument("-n", "--name",
                              help="Name of this interactive ipython "
                                   "notebook. If not supplied, one will be "
                                   "provided for you.")

        interact.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, gpus=1, dataset_id=None, framework_version=None,
             custom_code_url=None, resume_model_id=None,
             custom_code_commit=None, name=None):

        vals = {"gpus": gpus}
        if framework_version:
            vals["framework_version"] = framework_version

        if dataset_id:
            vals["dataset_id"] = dataset_id

        if resume_model_id:
            vals["resume_model_id"] = resume_model_id

        if custom_code_url:
            vals["custom_code_url"] = custom_code_url

        if custom_code_commit:
            vals["custom_code_commit"] = custom_code_commit

        if name:
            vals["name"] = name

        return api_call_json(config, INTERACT, method="POST", data=vals)

    @staticmethod
    def display_after(config, args, res):
        if 'uuid' in res:
            res['url'] = config.get_default_host() \
                               .rstrip('/') + '/interact/' + res['uuid']
            del res['uuid']

            print_table(res)


class Stop(Command):
    """
    Stop an interactive environment.
    """
    @classmethod
    def parser(cls, subparser):
        interact = subparser.add_parser(STOP.name, aliases=STOP.aliases,
                                        help=Stop.__doc__,
                                        description=Stop.__doc__)
        interact.add_argument("id", nargs="+",
                              help="id or list of IDs of sessions to stop")
        interact.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, id):

        res = []
        for stop in id:
            try:
                res.append(api_call_json(config, INTERACT+"/{}"
                           .format(stop), method="Delete"))
            except Exception:
                pass

        return res


class List(BaseList):
    """
    List interactive sessions.
    """
    @classmethod
    def parser(cls, subparser):
        interact = super(List, cls).parser(
            subparser, List.__doc__, List.__doc__)
        interact.add_argument('-a', "--all", action="store_true",
                              help="Show sessions in all states.")
        interact.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, all=False):
        vals = List.BASE_ARGS
        if not all:
            vals["filter"] = ["Ready", "Launching", "Scheduling"]

        res = api_call_json(config, INTERACT, method="GET", params=vals)

        if 'sessions' in res:
            # adjust content for display, show full URL rather than uuid
            res = res['sessions']
            for r in res:
                r['url'] = config.get_default_host().rstrip('/') + \
                           '/interact/' + r['uuid']
                del r['uuid']

        return res


InteractResults = Results(
    "interact",
    InteractiveSessionCompleter,
    INTERACT
)
parser = partial(
    build_subparser, 'interact', ['i'], __doc__, (
        Start, List, Stop, Show, InteractResults)
)
