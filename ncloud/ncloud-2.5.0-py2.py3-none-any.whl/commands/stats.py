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
Subcommands for listing analytics information.
"""
from functools import partial

from ncloud.commands.command import Command, build_subparser
from ncloud.commands.command import LS
from ncloud.formatting.output import print_table
from ncloud.util.api_call import api_call_json
from ncloud.config import STATS


class List(Command):
    @classmethod
    def parser(cls, subparser):
        stats = subparser.add_parser(LS.name, aliases=LS.aliases,
                                     help=List.__doc__,
                                     description=List.__doc__)
        stats.add_argument("--models", action="store_true",
                           help="Show models stats.")
        stats.add_argument("--time", nargs='?', const=0, type=int, help="Show "
                           "stats for models submitted in last n days. "
                           "Default unlimited.")
        stats.add_argument("--tenant-stats", action="store_true",
                           help="Show tenant stats, must be admin.")
        stats.add_argument("--page", default=1, type=int,
                           help="Page number.")
        stats.add_argument("--per-page", default=20, type=int,
                           help="Number of results per page.")
        stats.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, models=False, time=None, tenant_stats=False, page=1,
             per_page=20):
        vals = {}
        if models:
            vals["models"] = "True"
        if time is not None:
            vals["time"] = time
        if not models and time is None:
            vals.update(dict.fromkeys(['usage', 'models', 'ten'], "True"))
            vals["time"] = 0
        if tenant_stats:
            vals["tenant_stats"] = "True"

        vals["page"] = page
        vals["per_page"] = per_page

        return api_call_json(config, STATS, params=vals)

    @staticmethod
    def display_after(config, args, res):
        if res:
            print_table(res)

parser = partial(
    build_subparser, 'stats', ['sta'], __doc__, (List,)
)
