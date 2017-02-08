# Copyright (c) 2015, Formation Data Systems, Inc. All Rights Reserved.
#
import cmd
import os
import pipes
import pkgutil
import shlex
import sys

from argparse import ArgumentParser
from fdscli.services.fds_auth import FdsAuth
from fdscli.services.fds_auth_error import FdsAuthError
from fdscli.utils.fds_cli_configuration_manager import FdsCliConfigurationManager
from requests.exceptions import ConnectionError

class FDSShell( cmd.Cmd ):
    '''Line-oriented command interpreter. IS-A ``cmd.Cmd`` subclass.

    Created on Mar 30, 2015
    
    This is the main wrapper for the FDS CLI tool.  It's main purpose is to 
    obtain user authorization, load the dynamic modules and setup the 
    parsers.
    
    All actual work will take place in the "plugins" or the "services" that
    are added to the server, this simply manages the state and configures
    argparse
    
    @author: nate bever
    '''
    ERROR_AUTH_REQUIRED = "error_auth_required"

    def __init__(self, session, *args ):
        '''
        initialize the CLI session
        '''
        
        cmd.Cmd.__init__(self, *args)
        
        val = FdsCliConfigurationManager().get_value(FdsCliConfigurationManager.TOGGLES, FdsCliConfigurationManager.CMD_HISTORY)
        
        if val == "true" or val is True or val == "True":
            setupHistoryFile()

        self.plugins = []
        self.__session = session
        
        self.prompt ='fds> '

        self.loadmodules()
        

    def formatClassName(self, name):
        '''
        This makes assumptions about the name of the class relative to the name of the 
        plugin.  It basically deletes all "_" and capitalizes each word so that
        my_cool_plugin is expected to declare class MyCoolPlugin
        '''        
        words = name.split( '_' )
        formattedName = ''
        
        for word in words:
            formattedName = formattedName + word.capitalize()
        
        return formattedName 
        

    def loadmodules(self):
        '''
        This searches the plugins directory (relative to the location of this file)
        and will load all the modules it finds there, adding their parsing arguments
        to the argparse setup
        '''
        self.parser = ArgumentParser( add_help=True, description="By default it will attempt to use connection details found in ~/.fdscli.conf.  " +
            "If you would like to use a different configuration file please use -conf_file=<path and filename> as your first argument")
        
        self.subParsers = self.parser.add_subparsers( help="FDS CLI Commands" )

        mydir = os.path.dirname( os.path.abspath( __file__ ) )
        modules = pkgutil.iter_modules([os.path.join( mydir, "plugins" )] )
        sys.path.append(mydir)
        
        for loader, mod_name, ispkg in modules:
            
            if ( mod_name == "abstract_plugin" ):
                continue
            
            loadedModule = __import__( "plugins." + mod_name, globals=globals(), fromlist=[mod_name] )

            clazzName = self.formatClassName( mod_name )
            clazz = getattr( loadedModule, clazzName )
            clazz = clazz()
            self.plugins.append( clazz )
            
            clazz.build_parser( self.subParsers, self.__session )
            

    def login(self):
        '''Authenticates user session. Prompts user for credentials if necessary.

        Returns
        -------
        :type int: 0 if authentication succeeds, 1 otherwise
        '''
        if (self.__session.is_authenticated()):
            return 0

        try:
            self.__session.login()
            print("Connected to: {}\n".format(self.__session.get_hostname()))

        except FdsAuthError as f:
            print(str(f.error_code) + ":" + f.message)
            self.__session.logout()
            return 1

        except Exception as ex:
            print("Unknown error occurred while trying to connect to {}.".format( self.__session._FdsAuth__hostname ))
            print( "\nException reported: \n{}".format( ex ) )
            self.__session.logout()
            return 1

        return 0


    def default(self, line):
        '''
        Default method that gets called when no 'do_*' method
        is found for the command prompt sent in
        '''        
        if (line == FDSShell.ERROR_AUTH_REQUIRED):
            # Causes SystemExit to be raised
            return 1

        try:
            argList = shlex.split( line )
            pArgs = self.parser.parse_args( argList )
            rtn = pArgs.func( vars( pArgs ) )
            return rtn
        
        # a connection error occurs later
        except ConnectionError:
            print("Lost connection to OM.  Please verify that it is up and responsive.")
            self.__session.logout()
            return
            
        # A system exit gets raised from the argparse stuff when you ask for help.  Stop it.    
        except SystemExit:
            return


    def run( self, argv ):
        '''
        Called from main to actually start the CLI tool running
        
        By default Cmd will try to run a do_* argv method if one exists.
        If not, it will call into the loop which ends up in the "default" function
        '''         
        
        # If there are no arguments we will execute as an interactive shell
        if argv is None or len( argv ) == 0:
            # Repeatedly issue a prompt, accept input, parse an initial prefix off the
            # received input, and dispatch to action methods, passing them the remainder
            # of the line as argument.
            self.cmdloop( '\n' )
        # Otherwise just run this one command
        else:
            strCmd = ' '.join( map( pipes.quote, argv ) )

            strCmd = self.precmd( strCmd );
            rtn = self.onecmd( strCmd );
            
            if rtn != 0 and rtn != None:
                raise SystemExit( rtn )
            
            return rtn
        

    def exitCli(self, *args):
        '''
        Just one method to exit the program so we can link a few commands to it
        '''
        print('Bye!')
        sys.exit()
        

    def do_exit(self, *args):
        '''
        Handles the command 'exit' magically.
        '''        
        self.exitCli( *args )
        

    def do_quit(self, *args):
        '''
        Handles the command 'quit' magically
        '''        
        self.exitCli( *args )
        

    def do_bye(self, *args):
        '''
        Handles the command 'bye' magically
        '''
        self.exitCli( *args )
        
    def do_help(self, *args):
        '''Trigger the argparse help.

        This method executes only for line starting with ``help``.
        '''
        self.parser.print_help()

    def precmd(self, line):
        '''Hook method executed just before the command line line is interpreted, but after the
        input prompt is generated and issued.

        Never prompt for credentials when asking argparse for help messages. Use credentials to
        login if available, however. An authentication failure is not fatal in these cases.

        Always login to run commands except for help or quit. Prompt for credentials if necessary
        in these cases.

        Never login for quit command.

        Parameters
        ----------
        :type line: str
        '''

        # Use Case Summary:
        #
        # $ fds -h              default()     login no prompt   argparse parse_args
        # $ fds --help          default()     login no prompt   argparse parse_args
        # $ fds -h help         default()     login no prompt   argparse parse_args
        # $ fds -h volume       default()     login no prompt   argparse parse_args
        # $ fds volume -h       default()     login no prompt   argparse parse_args

        # $ fds help            do_help()     login no prompt   argparse print_help()
        # $ fds help -h         do_help()     login no prompt   argparse print_help()

        # $ fds -help           default()     login no prompt   argparse error
        # $ fds volume -help    default()     login no prompt   argparse error

        # $ fds volume list     default()     login required    argparse parse_args

        if self.__session.is_authenticated() is True:
            pass
        else:
            # Makes sure any available credentials are loaded.
            self.__session.refresh()

            help_arg = False
            do_help = False
            do_quit = False
            argument_list = shlex.split( line )

            if (len(argument_list) > 0):
                if (argument_list[0] == 'help'):
                    do_help = True
                if (argument_list[0] in ['quit', 'exit', 'bye']):
                    do_quit = True

            # The optional arguments '-h' and '--help' are equivalent
            if isinstance(argument_list, list):
                if ('-h' in argument_list or '--help' in argument_list):
                    help_arg = True

            if (do_help is True or help_arg is True):
                # An interpreter help command or an argparse command help.
                # Never prompts user for credentials.
                if self.__session.isset_username() is True:
                    # Use available credentials (from file or command line).
                    auth_result = self.login()
                    if (auth_result == 0):
                        self.loadmodules()
                    else:
                        print "Additional commands or command help may be available when authenticated.\n"
            elif do_quit is True:
                pass
            else:
                # A command, known or otherwise, not related to help.
                # Prompts user for credentials if necessary.
                auth_result = self.login()
                if (auth_result != 0):
                    # Authentication is required and has failed
                    line = FDSShell.ERROR_AUTH_REQUIRED
                else:
                    self.loadmodules()

        # TODO: rewrite command here if -h preceeds another command name
        # Would allow user to see help for command instead of top level.
        return line

def setupHistoryFile():
    '''
    stores and retrieves the command history specific to the user
    '''
         
    import readline
    histfile = os.path.join(os.path.expanduser("~"), ".fdsconsole_history")
    readline.set_history_length(20)
    try:
        readline.read_history_file(histfile)
    except IOError:
        pass
    import atexit
    atexit.register(readline.write_history_file, histfile)

'''
The main entry point to the application.  
Instantiates the CLI object and passes that args in
'''
if __name__ == '__main__':
        
    cmdargs=sys.argv[1:]
    
    auth = FdsAuth()
    
    shell = FDSShell(auth, cmdargs)

    # now we check argv[0] to see if its a shortcut scripts or not    
    if ( len( cmdargs ) > 0 ):

        for plugin in shell.plugins:
            detectMethod = getattr( plugin, "detect_shortcut", None )
            
            # the plugin does not support shortcut argv[0] stuff
            if ( detectMethod is None or not callable( plugin.detect_shortcut ) ):
                continue
            
            tempArgs = plugin.detect_shortcut( cmdargs )
                
            # we got a new argument set
            if ( tempArgs is not None ):
                cmdargs = tempArgs
                break
        # end of for loop
        
    # now actually run the command
    shell.run( cmdargs ) 
