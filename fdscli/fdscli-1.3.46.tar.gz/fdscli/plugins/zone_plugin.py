import json
import re
import netifaces

from fdscli.model.virtualzones.zone import Zone
from fdscli.services.response_writer import ResponseWriter
from fdscli.plugins.abstract_plugin import AbstractPlugin
from fdscli.services.node_service import NodeService
from fdscli.model.fds_error import FdsError
from fdscli.services.fds_auth import FdsAuth
from fdscli.services import zone_service
import collections
from fdscli.services import response_writer
from fdscli.utils.converters.virtualzones.zone_converter import ZoneConverter

class ZonePlugin( AbstractPlugin):
    '''
    Created on Sep 8, 2016

    A plugin to handle all the parsing for VAMG zone creation
    and to route those options to the appropriate zone
    management calls

    @author: chaithra, Neil
    '''


    def __init__(self):
        AbstractPlugin.__init__(self)

    '''
    @see: AbstractPlugin
    '''
    def build_parser(self, parentParser, session):

        self.session = session

        self.__zone_service = zone_service.ZoneService( self.session )
        self.__node_service = NodeService( self.session )
       
        self.__parser = parentParser.add_parser( "zone", help="Create, edit, delete and manipulate virtual AM groups" )
        self.__subparser = self.__parser.add_subparsers( help="The sub-commands that are available")

        self.create_create_command(self.__subparser)
        self.create_activate_command(self.__subparser)
        self.create_deactivate_command(self.__subparser)
        self.create_delete_command(self.__subparser)
        self.create_list_command(self.__subparser)

    '''
    @see: AbstractPlugin
    '''
    def detect_shortcut(self, args):
        return None

    def get_zone_service(self):
        return self.__zone_service

    def get_node_service(self):
        '''
        Re-use the same node service for everything
        '''
        return self.__node_service

    # builds the parsers

    def create_create_command(self, subparser):
        '''
        Create a parser for the creation of a VAMG
        '''
        helpDesc = """This command allows a user to create a Virtual AM Zone on the local domain.
                      A Virtual AM Zone is a virtual entity consisted of two different AM services within
                      the same local domain, and is represented by a Virtual IP address. Once activated, the zone
                      will register the VIP on a AM service, sorted by AM priority, and clients may access the zone
                      using the VIP. Should an AM fail for some reason, the backup AM will take over the VIP
                      and provide high-availability to the system. There is currently a limit of 99 zones per local domain.
                    """
        __create_parser = subparser.add_parser( "create", description=helpDesc, help=helpDesc)
        self.add_format_arg( __create_parser )

        __create_parser.add_argument( "-" + AbstractPlugin.zone_name, help="The name of the Virtual AM Group (VAMG) you are creating.", required=True)
        __create_parser.add_argument( "-" + AbstractPlugin.zone_id, help="The id of the VAMG you are creating. (1-99). If this is not specified, an ID will be generated.", required=False, type=int)
        __create_parser.add_argument( "-" + AbstractPlugin.zone_type, help="The type of the VAMG you are creating. This can currently be set to VAMG.", default='Virtual AM Group')
        __create_parser.add_argument( "-" + AbstractPlugin.zone_iface, help="Interface name on which to create the VIP",required=True)
        __create_parser.add_argument( "-" + AbstractPlugin.zone_vip, help="The virtual IP address of the VAMG you are creating.", required=True)
        __create_parser.add_argument( "-" + AbstractPlugin.zone_service_ids, help="Comma separated list of AM service IDs to be included in this VAMG, sorted from high to low priority. Currently, you can provide only two AM service IDs",required=True)
        __create_parser.set_defaults( func=self.create_zone, format="tabular")

    def create_activate_command(self, subparser):
        '''
        Activate a VAMG zone
        '''
        __activate_parser = subparser.add_parser("activate", help="Activate an already created Virtual AM zone.")
        self.add_format_arg(__activate_parser)
        __activate_parser.add_argument("-" + AbstractPlugin.zone_ids,
                                     help="Comma separated list of virtual AM groups that you are activating.", required=True)
        __activate_parser.set_defaults(func=self.activate_zones, format="tabular")

    def create_deactivate_command(self, subparser):
        '''
        Activate a VAMG zone
        '''
        __deactivate_parser = subparser.add_parser("deactivate", help="Deactivate an already activated Virtual AM zone.")
        self.add_format_arg(__deactivate_parser)
        __deactivate_parser.add_argument("-" + AbstractPlugin.zone_ids,
                                     help="Comma separated list of virtual AM groups that you are deactivating.", required=True)
        __deactivate_parser.set_defaults(func=self.deactivate_zones, format="tabular")

    def create_delete_command(self, subparser):
        '''
        Delete a VAMG zone
        '''
        __delete_parser = subparser.add_parser("delete", help="Delete an existing Virtaul AM zone.")
        self.add_format_arg(__delete_parser)

        __delete_parser.add_argument("-" + AbstractPlugin.zone_id, help="The id of the VAMG zone you are deleting.", required=True)
        __delete_parser.set_defaults(func=self.delete_zone, format="tabular")

    def create_list_command(self, subparser):
        '''
        Configure the parser for the zome list command
        '''
        __listParser = subparser.add_parser("list", help="List all the zones in the system")
        __listParser.add_argument("-" + AbstractPlugin.zone_id,
                                  help="Specify a particular zone to list by zone ID", default=None)
        self.add_format_arg(__listParser)
        __listParser.set_defaults(func=self.list_zones, format="tabular")


    '''
    So we can mock this
    '''
    def get_node_list(self):
        return self.get_node_service().list_nodes()

    '''
    Validator
    '''
    def validate_zone_input(self, zone, zone_service_ids):
        # Do some simple argument checks
        # zone name check
        if (' ' in zone.name):
            print("Error: Zone names may not contain white spaces")
            return False

        # zone ID checks
        if int(zone.zid) < 0 or int(zone.zid) > 99:
            print("Error: Zone IDs must be [1-99]")
            return False

        # AM UUID checks
        ids_args = zone_service_ids
        ids = ids_args.split( ',' )
        if ids.__len__() != 2:
            print("Error: Currently, this command requires exactly 2 AM service IDs to be provided")
            return False
        zone.amList = ids

        # Make sure entered UUIDs are legit
        nodes = self.get_node_list()
        for amChk in ids:
            found = False
            for node in nodes:
                amList = node.services["AM"]
                for actualAM in amList:
                    if actualAM.id == amChk:
                        found = True
                        break
                if found:
                    break
            if not found:
                print "Error: The specified service UUID: " + amChk + " is not an valid AM service UUID."
                return False
        
        # Make sure no UUIDs repeat
        for i,elem in enumerate(zone.amList):
            if zone.amList.count(elem) > 1:
                print "Error: The AM UUID: " + str(elem) + " is specified more than once."
                return False

        # VIP checks
        m = re.search("[0-9]+\.[0-9]+\.[0-9]+\.([0-9]+)", zone.zvip)
        if not m:
            print("Error: Please enter IP address in IPv4 format")
            return False
        if not ((int(m.group(1)) > 0) and (int(m.group(1)) < 255)):
            print("Error: Please enter a valid IP address.")
            return False

        # Everything seems ok
        return True

    def generate_zone_obj(self, args):
        zone = Zone()
        
        if args[AbstractPlugin.zone_id] is not None:
            zone.zid = args[AbstractPlugin.zone_id]
        else:
            # 0 means auto-generate
            zone.zid = 0
            
        zone.name = args[AbstractPlugin.zone_name]
        zone.ztype = args[AbstractPlugin.zone_type]
        zone.zvip = args[AbstractPlugin.zone_vip]
        if (args[AbstractPlugin.zone_iface] is not None):
            zone.iface = args[AbstractPlugin.zone_iface]
        else:
            zone.iface = None

        return zone


    def create_zone(self, args):
        '''
        Takes the arguments, constructs and send command to VAMG the creation call
        '''
        if (args[AbstractPlugin.zone_name] is None \
            or args[AbstractPlugin.zone_type] is None or args[AbstractPlugin.zone_vip] is None \
            or args[AbstractPlugin.zone_service_ids] is None):
            print("Required arguments are not supplied. See \"zone create -h\" for more information")
            return

        zone = self.generate_zone_obj(args)

        if self.validate_zone_input(zone, zone_service_ids=args[AbstractPlugin.zone_service_ids]):
            self.get_zone_service().create_zone( zone )
        else:
            return 1
        
        self.list_zones(args)
        return 0

    def activate_zones(self, args):
        '''
        Takes the arguments, constructs and send command to VAMG the creation call
        '''
        if args[AbstractPlugin.zone_ids] is None:
            print("Zone ID(s) is missing. See \"zone activate -h\" for more information")
            return

        id_args = args[AbstractPlugin.zone_ids]
        ids_list = ''.join(id_args.split())
        response = self.get_zone_service().activate_zones(ids_list)
        if isinstance(response, FdsError):
            print response.message
        else:
            print("Zone(s) activated")

    def deactivate_zones(self, args):
        '''
        Takes the arguments, constructs and send command to VAMG the creation call
        '''
        if args[AbstractPlugin.zone_ids] is None:
            print("Zone ID(s) is missing. See \"zone deactivate -h\" for more information")
            return

        id_args = args[AbstractPlugin.zone_ids]
        ids = ''.join(id_args.split())
        response = self.get_zone_service().deactivate_zones(ids)
        if isinstance(response, FdsError):
            print response.message
        else:
            print("Zone(s) deactivated")

    def delete_zone(self, args):
        '''
        Takes the arguments, constructs and send command to VAMG the creation call
        '''
        if args[AbstractPlugin.zone_id] is None:
            print("Zone ID is missing. See \"zone delete -h\" for more information")
            return

        response = self.get_zone_service().delete_zone(args[AbstractPlugin.zone_id])
        if isinstance(response, FdsError):
            print response.message
        else:
            print("Zone deleted")

    def list_zones(self, args):
        '''
        Retrieve a list of zones in accordance with the passed in arguments
        '''
        response = []
        just_one_zone = False

        if AbstractPlugin.zone_id in args and args[AbstractPlugin.zone_id] is not None:
            response = self.get_zone_service().get_zone(args[AbstractPlugin.zone_id])
            response = [response]
            just_one_zone = True
        else:
            response = self.get_zone_service().list_zones()


        if not isinstance(response, collections.Iterable):
            response = [response]


        if len(response) > 0 and (
            isinstance(response[0], FdsError) or (hasattr(response[0], "error") and hasattr(response[0], "message"))):
            return 1

        if len(response) == 0:
            print("No zones found.")
            return


        if "format" in args and args[AbstractPlugin.format_str] == "json":

            j_zones = []

            for zone in response:
                j_zone = ZoneConverter.to_json(zone)
                j_zone = json.loads(j_zone)
                j_zones.append(j_zone)

            response_writer.ResponseWriter.writeJson(j_zones)
        else:

            response = response_writer.ResponseWriter.prep_zone_for_table(self.session, response)
            response_writer.ResponseWriter.writeTabularData(response)

