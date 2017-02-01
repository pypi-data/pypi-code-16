from fdscli.plugins.abstract_plugin import AbstractPlugin
from fdscli.services.volume_service import VolumeService
from fdscli.services.response_writer import ResponseWriter
from collections import OrderedDict

class PresetPlugin(AbstractPlugin):
    '''
    Created on May 6, 2015

    A plugin to handle all of the preset type things we need.  Right now you can
    only list two types of policies, but it's likely this operation list
    will grow enough to warrant a separate plugin very quickly
    
    @author: nate
    '''
    
    def __init__(self):
        AbstractPlugin.__init__(self)    
        
    '''
    @see: AbstractPlugin
    '''
    def build_parser(self, parentParser, session): 
        
        self.session = session
        self.__volume_service = VolumeService(self.session)
        
        self.__parser = parentParser.add_parser( "presets", help="Manage and interact with the various types of presets available to the system." )
        self.__subparser = self.__parser.add_subparsers( help="The sub-commands that are available" )
         
        self.create_list_parser_command( self.__subparser )
    '''
    @see: AbstractPlugin
    '''    
    def detect_shortcut(self, args):
        
        return None
    
    def get_volume_service(self):
        return self.__volume_service
    
    #parsing section
    
    def create_list_parser_command(self, subparser):
        '''
        Create a parser to handle listing all of the preset items

        Parameters
        ----------
        subparser (argparse._SubParsersAction) : parsers action
        '''
        
        __list_parser = subparser.add_parser( "list", help="List the presets available in the system.")
        self.add_format_arg( __list_parser )
        
        __list_parser.add_argument( "-" + AbstractPlugin.type_str, help=("The type of preset that "
            "you would like to list. The default is to list all of them with minimal detail."),
            required=False, choices=["all", "qos", "safeguard", "timeline"], default="all")

        __list_parser.set_defaults( func=self.list_presets, format="tabular" )
    
    #real work section

    def print_timeline_preset(self, preset):
        '''
        Helper to print out the preset policy passed in.  It takes two tables so we need to do this here
        '''
        meta_d = OrderedDict()
        meta_d["ID"] = preset.id
        meta_d["Name"] = preset.name
        results = [meta_d]
        ResponseWriter.writeTabularData(results)
        
        policies = ResponseWriter.prep_snapshot_policy_for_table(self.session, preset.policies)
        ResponseWriter.writeTabularData( policies )

    def list_presets(self, args):
        '''
        Sort through the arguments and list the appropriate presets requested

        Parameters
        ----------
        args (dict) : key/value pairs
        '''
        qos_presets = []
        safeguard_presets = []
        timeline_presets = []

        if (args[AbstractPlugin.type_str] in ["all", "qos"]):
            qos_presets = self.get_volume_service().get_qos_presets()

        if (args[AbstractPlugin.type_str] in ["all", "safeguard"]):
            safeguard_presets = self.get_volume_service().get_safeguard_presets()

        if (args[AbstractPlugin.type_str] in ["all", "timeline"]):
            timeline_presets = self.get_volume_service().get_data_protection_presets()
            
        if args[AbstractPlugin.format_str] == "json":
            return
            
        else:
            
            if len(qos_presets) != 0:
                print("\nQuality of Service preset policies:")
                prepped = ResponseWriter.prep_qos_presets( qos_presets )
                ResponseWriter.writeTabularData( prepped )

            if len(safeguard_presets) != 0:
                print("\nSafeGuard preset policies:")
                prepped = ResponseWriter.prep_safeguard_presets(safeguard_presets)
                ResponseWriter.writeTabularData(prepped)

            if len(timeline_presets) != 0:
                print("\nTimeline preset policies:")
                for timeline_preset in timeline_presets:
                    self.print_timeline_preset(timeline_preset)

