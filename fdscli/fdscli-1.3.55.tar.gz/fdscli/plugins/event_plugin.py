# Copyright (c) 2016, Formation Data Systems, Inc. All Rights Reserved.
#
import json
from .abstract_plugin import AbstractPlugin
from fdscli.model.fds_error import FdsError
from fdscli.utils.converters.event.event_converter import EventConverter
from fdscli.services.event.event_client import EventClient
from fdscli.services.fds_auth import FdsAuth
from fdscli.services import response_writer

class EventPlugin(AbstractPlugin):
    '''Provides event service query.
    '''
    def __init__(self):
        AbstractPlugin.__init__(self)

    def build_parser(self, parentParser, session): 
        '''
        @see: AbstractPlugin

        Parameters
        ----------
        parentParser (argparse.Action)
        session (services.FdsAuth)
        '''
        self.session = session
        
        if not session.is_allowed( FdsAuth.VOL_MGMT ):
            return

        self.__event_client = EventClient( self.session )

        msg = ("Query the event service.")
        self.__parser = parentParser.add_parser( "event", description=msg, help=msg)
        self.__subparser = self.__parser.add_subparsers(title="subcommands",
            description='event subcommands',
            help='description:')

        # Add parsers for sub-commands
        self.add_list_command(self.__subparser)

    '''
    @see: AbstractPlugin
    '''   
    def detect_shortcut(self, args):
        
        return None

    def get_event_client(self):
        return self.__event_client

    def add_list_command(self, subparser ):
        '''
        Creates the parser for the ``event list`` sub-command.

        Parameters
        ----------
        :type subparser: ``argparse._SubParsersAction``
        :param subparser: parsers action
        '''
        __parserForList = subparser.add_parser( "list", help="List filtered or unfiltered events.")

        # Optional args
        self.add_format_arg(__parserForList)

        __parserForList.set_defaults(func=self.list_events, format="tabular")

    def list_events(self, args):
        '''
        Parameters
        ----------
        :type args: dict
        '''
        print_json = False
        if "format" in args and args[AbstractPlugin.format_str] == "json":
            print_json = True

        # Get all
        events = self.get_event_client().list_events()

        if isinstance(events, FdsError):
            return

        if (len(events) == 0):
            print("No events found.")
            return

        #print it all out
        if "format" in args  and args[AbstractPlugin.format_str] == "json":

            j_events = []

            for event in events:
                j_event = EventConverter.to_json_string(event)
                j_event = json.loads( j_event )
                j_events.append( j_event )

            response_writer.ResponseWriter.writeJson( j_events )
        else:
            resultList = response_writer.ResponseWriter.prep_events_for_table( self.session, events)
            response_writer.ResponseWriter.writeTabularData( resultList )

