#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


from cliff import lister

from pankoclient import utils

EVENTS_LIST_COLS = ['event_type', 'generated', 'message_id', 'traits']


class CliEventList(lister.Lister):
    """List events"""

    def get_parser(self, prog_name):
        parser = super(CliEventList, self).get_parser(prog_name)
        parser.add_argument("-q", "--query", metavar="<QUERY>",
                            help="key[op]data_type::value; list. data_type "
                                 "is optional, but if supplied must be "
                                 "string, integer, float or datetime.")
        parser.add_argument("-l", "--limit", type=int, metavar="<LIMIT>",
                            help="Number of resources to return "
                                 "(Default is server default)")
        parser.add_argument("--marker", metavar="<MARKER>",
                            help="Last item of the previous listing. "
                                 "Return the next results after this value,"
                                 "the supported marker is message_id.")
        parser.add_argument("--sort", action="append",
                            metavar="<SORT_KEY:SORT_DIR>",
                            help="Sort of resource attribute, "
                                 "e.g. generated:desc")
        return parser

    def take_action(self, parsed_args):
        query = utils.cli_to_array(parsed_args.query)
        events = utils.get_client(self).events.list(
            query=query, sorts=parsed_args.sort,
            limit=parsed_args.limit, marker=parsed_args.marker)
        return utils.list2cols(EVENTS_LIST_COLS, events)
