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
Subcommands for performing batch predictions on datasets using deployed models.
"""
from __future__ import print_function
from functools import partial
import os

from ncloud.config import BATCH_PREDICTIONS
from ncloud.util.api_call import api_call, api_call_json
from ncloud.formatting.time_zone import utc_to_local
from ncloud.commands.command import (BaseList, Command, Results, print_table,
                                     build_subparser, SHOW, STOP,
                                     PREDICT)
from ncloud.completers import BatchPredictionCompleter


class Predict(Command):
    """
    Use a trained model to predict a dataset of examples.
    """
    @classmethod
    def parser(cls, subparser):
        batch_predict = subparser.add_parser(
            PREDICT.name, aliases=PREDICT.aliases,
            help=Predict.__doc__, description=Predict.__doc__
        )
        batch_predict.add_argument("model_id", help="ID of trained model.")
        batch_predict.add_argument(
            "dataset_id",
            help="ID of dataset of examples."
        )
        batch_predict.add_argument(
            "-f", "--extra-files",
            help="Zip of extra files to include in the deployment."
        )

        batch_predict.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, model_id, dataset_id, extra_files=None):
        vals = {"model_id": model_id, "dataset_id": dataset_id}

        files = None
        if extra_files is not None:
            files = [('extra_files', (os.path.basename(extra_files),
                     open(extra_files, "rb")))]
        return api_call_json(config, BATCH_PREDICTIONS, method="POST",
                             data=vals, files=files)


class Stop(Command):
    """
    Stop a batch prediction given a batch ID.
    """
    @classmethod
    def parser(cls, subparser):
        stop_batch_predict = subparser.add_parser(
            STOP.name, aliases=STOP.aliases,
            help=Stop.__doc__, description=Stop.__doc__
        )
        stop_batch_predict.add_argument(
            "batch_id",
            help="ID of batch prediction to stop."
        )
        stop_batch_predict.set_defaults(func=cls.arg_call)

    @staticmethod
    def arg_names():
        return ['batch_id']

    @staticmethod
    def call(config, batch_id):
        delete_path = os.path.join(BATCH_PREDICTIONS, str(batch_id))
        return api_call(config, delete_path, method="DELETE")


class Show(Command):
    """
    Show batch prediction details for a given batch ID.
    """
    @classmethod
    def parser(cls, subparser):
        batch_show = subparser.add_parser(
            SHOW.name, aliases=SHOW.aliases,
            help=Show.__doc__, description=Show.__doc__
        )
        batch_show.add_argument(
            "batch_id",
            help="ID of batch to show details of."
        )

        batch_show.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, batch_id):
        show_path = os.path.join(BATCH_PREDICTIONS, batch_id)
        res = api_call_json(config, show_path)

        for tm in ["start_time"]:
            if tm in res and res[tm] is not None:
                res[tm] = utc_to_local(res[tm])

        return res


class List(BaseList):
    """
    List all batch predictions.
    """
    @classmethod
    def parser(cls, subparser):
        batch_list = super(List, cls).parser(
            subparser, List.__doc__, List.__doc__)
        batch_list.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config):
        vals = List.BASE_ARGS
        return api_call_json(config, BATCH_PREDICTIONS, params=vals)

    @staticmethod
    def display_after(config, args, res):
        if res:
            predictions = res['predictions']

            for tm in ["start_time"]:
                for prediction in predictions:
                    if tm in prediction and prediction[tm] is not None:
                        prediction[tm] = utc_to_local(prediction[tm])

            print_table(predictions)


BatchResults = Results(
    "batch",
    BatchPredictionCompleter,
    BATCH_PREDICTIONS
)
parser = partial(
    build_subparser, 'batch', ['b'], __doc__,
    (List, Show, Stop, Predict, BatchResults)
)
