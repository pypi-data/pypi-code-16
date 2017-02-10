# Copyright (c) 2015, Formation Data Systems, Inc. All Rights Reserved.
#

'''
Created on Jan 21, 2016

@author: nate
'''
from fdscli.services.fds_auth import FdsAuth
from fdscli.FDSShell import FDSShell
from mock import patch
from unittest.case import TestCase

def failedLogin():
    raise Exception( "AAAAAHHHH!" )

def mock_get_username():
    '''Returns a username.
    '''
    return 'csx28e11.18.16'

def mock_false():
    return False

def mock_true():
    return True

class testLogin( TestCase ):
    '''
    Test the login functionality.

    The test machine might or might not have a ``~/.fdscli.conf`` file.
    That file holds credentials used to automatically authenticate the user.
    If the file is not present, the system normally prompts the user for credentials.
    We don't want any prompt during the test. Therefore, we mock whether credentials
    are present or not.

    If FdsAuth.isset_username() returns True, credentials are understood to be present.
    '''
    @patch( "fdscli.services.fds_auth.FdsAuth.is_authenticated", side_effect=mock_false )
    @patch( "fdscli.services.fds_auth.FdsAuth.isset_username", side_effect=mock_true )
    @patch( "fdscli.services.fds_auth.FdsAuth.login", side_effect=failedLogin )
    def test_command_with_credentials( self, mockLogin, mockUsername, mockAuth ):
        '''Mock credentials present. Login attempt expected.

        Parameters
        ----------
        :type mockLogin: ``unittest.mock.MagicMock``
        :type mockUsername: ``unittest.mock.MagicMock``
        :type mockAuth: ``unittest.mock.MagicMock``
        '''
        print "Test 'fds volume list' with credentials.\n"
        auth = FdsAuth()
        cli = FDSShell( auth )

        args = ["volume", "list"]

        exception = None

        try:
            rtn = cli.run( args )
        except SystemExit as se:
            exception = se

        # Login attempt expected
        assert mockLogin.call_count == 1
        # Login was mandatory
        assert exception != None, "Expected a SystemExit exception but got none."
        assert isinstance(exception, SystemExit) == True
        assert exception.code == 1

    @patch( "fdscli.services.fds_auth.FdsAuth.is_authenticated", side_effect=mock_false )
    @patch( "fdscli.services.fds_auth.FdsAuth.isset_username", side_effect=mock_true )
    @patch( "fdscli.services.fds_auth.FdsAuth.login", side_effect=failedLogin )
    def test_argparse_help_with_credentials( self, mockLogin, mockUsername, mockAuth ):
        '''Mock credentials present. Login attempt expected.
        '''
        print "Test 'fds volume -h' with credentials.\n"
        auth = FdsAuth()
        interpreter = FDSShell( auth )

        args = ['volume', '-h']
        exception = None
        try:
            result = interpreter.run( args )
        except SystemExit as se:
            exception = se

        # Login attempt expected
        assert mockLogin.call_count == 1
        # Login was not mandatory
        assert exception == None

        args = ['-h']
        exception = None
        try:
            result = interpreter.run( args )
        except SystemExit as se:
            exception = se

        # Login attempt expected
        assert mockLogin.call_count == 2
        # Login was not mandatory
        assert exception == None

        args = ['--help']
        exception = None
        try:
            result = interpreter.run( args )
        except SystemExit as se:
            exception = se

        # Login attempt expected
        assert mockLogin.call_count == 3
        # Login was not mandatory
        assert exception == None

    @patch( "fdscli.services.fds_auth.FdsAuth.is_authenticated", side_effect=mock_false )
    @patch( "fdscli.services.fds_auth.FdsAuth.isset_username", side_effect=mock_false )
    @patch( "fdscli.services.fds_auth.FdsAuth.login", side_effect=failedLogin )
    def test_argparse_help_without_credentials( self, mockLogin, mockUsername, mockAuth ):
        '''Mock credentials not present. No login attempt expected.
        '''
        print "Test 'fds volume -h' with no credentials.\n"
        auth = FdsAuth()
        interpreter = FDSShell( auth )

        args = ['volume', '--help']
        exception = None
        try:
            result = interpreter.run( args )
        except SystemExit as se:
            exception = se

        # No login attempt expected
        assert mockLogin.call_count == 0
        assert exception == None

        args = ['-h']
        exception = None
        try:
            result = interpreter.run( args )
        except SystemExit as se:
            exception = se

        # No login attempt expected
        assert mockLogin.call_count == 0
        assert exception == None

        args = ['--help']
        exception = None
        try:
            result = interpreter.run( args )
        except SystemExit as se:
            exception = se

        # No login attempt expected
        assert mockLogin.call_count == 0
        assert exception == None

    @patch( "fdscli.services.fds_auth.FdsAuth.is_authenticated", side_effect=mock_false )
    @patch( "fdscli.services.fds_auth.FdsAuth.isset_username", side_effect=mock_true )
    @patch( "fdscli.services.fds_auth.FdsAuth.login", side_effect=failedLogin )
    def test_interpreter_help_with_credentials( self, mockLogin, mockUsername, mockAuth ):
        '''Mock credentials present. Login attempt expected.
        '''
        print "Test 'fds help' with credentials.\n"
        auth = FdsAuth()
        interpreter = FDSShell( auth )

        args = ['help']
        exception = None

        try:
            result = interpreter.run( args )
        except SystemExit as se:
            exception = se

        # Login attempt expected
        assert mockLogin.call_count == 1
        # Login was not mandatory
        assert exception == None

    @patch( "fdscli.services.fds_auth.FdsAuth.is_authenticated", side_effect=mock_false )
    @patch( "fdscli.services.fds_auth.FdsAuth.isset_username", side_effect=mock_false )
    @patch( "fdscli.services.fds_auth.FdsAuth.login", side_effect=failedLogin )
    def test_interpreter_help_without_credentials( self, mockLogin, mockUsername, mockAuth ):
        '''Mock credentials not present. No login attempt expected.
        '''
        print "Test 'fds help' with no credentials.\n"
        auth = FdsAuth()
        interpreter = FDSShell( auth )

        args = ['help']
        exception = None

        try:
            result = interpreter.run( args )
        except SystemExit as se:
            exception = se

        # No login attempt expected
        assert mockLogin.call_count == 0
        assert exception == None

    @patch( "fdscli.services.fds_auth.FdsAuth.is_authenticated", side_effect=mock_false )
    @patch( "fdscli.services.fds_auth.FdsAuth.isset_username", side_effect=mock_true )
    @patch( "fdscli.services.fds_auth.FdsAuth.login", side_effect=failedLogin )
    def test_quit_with_credentials( self, mockLogin, mockUsername, mockAuth ):
        '''Mock credentials present. No login attempt expected.
        '''
        print "Test 'fds quit' with credentials.\n"
        auth = FdsAuth()
        interpreter = FDSShell( auth )

        args = ['quit']
        exception = None
        try:
            result = interpreter.run( args )
        except SystemExit as se:
            exception = se

        # No login attempt expected
        assert mockLogin.call_count == 0
        # A quit raises SystemExit
        assert exception != None, "Expected a SystemExit exception but got none."
        assert isinstance(exception, SystemExit) == True

    @patch( "fdscli.services.fds_auth.FdsAuth.is_authenticated", side_effect=mock_false )
    @patch( "fdscli.services.fds_auth.FdsAuth.isset_username", side_effect=mock_false )
    @patch( "fdscli.services.fds_auth.FdsAuth.login", side_effect=failedLogin )
    def test_quit_without_credentials( self, mockLogin, mockUsername, mockAuth ):
        '''Mock credentials not present. No login attempt expected.
        '''
        print "Test 'fds quit' with no credentials.\n"
        auth = FdsAuth()
        interpreter = FDSShell( auth )

        args = ['bye']
        exception = None
        try:
            result = interpreter.run( args )
        except SystemExit as se:
            exception = se

        # No login attempt expected
        assert mockLogin.call_count == 0
        # A quit raises SystemExit
        assert exception != None, "Expected a SystemExit exception but got none."
        assert isinstance(exception, SystemExit) == True

