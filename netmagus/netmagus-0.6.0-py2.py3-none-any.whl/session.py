# coding=utf-8
from __future__ import absolute_import, division, print_function, \
    unicode_literals

import contextlib
import importlib
import json
import logging
import os
import shelve
import sys
import traceback

import netmagus.form
import netmagus.rpc


class NetMagusSession(object):
    """
    This class is a wrapper to handle an interactive session between the
    NetMagus backend and a user script.  It serves as a unifed API for user
    script operations to send/receive data with the NetMagus backend.  It
    also serves as a unified API for the NetMagus backend to call and execute
    user scripts.

    The NetMagus backend will call the module as (ex.):
        "python -m netmagus --script user.py --token aBcDeF --input-file
        /some/path/to/aBcDeF.json --loglevel 10

    The "token" is used by NM to desginate all file and RPC interactions tied
    to a given execution.

    This class will be called by the module's __main__.py file to:
     - read JSON from the NetMagus backend via the input-file if it exists
     - read in any previous state tied to the token/session
     - import the user's script/module and execute it's run() method
        - run() method must receive a NetMagusSession object as only arg
        - run() method may return Form or (Form, anyobject)
     - receive a Form (and a state object) as a return from the user's
       run() method
     - store any state object and send JSON response back to NetMagus backend


     The .start method is used to initiate the execution of the user's code
     in the formula.

     The user's code can use various attributes and methods of this session
     object to interact with the NetMagus server and its UI.

     The following attributes exist within each session object:

     nm_input:  holds the data entered by end-user on the NM ui
     user_state: holds any state data from previous formula steps

     The following methods exist within each session object for interaction
     with the NetMagus server:

     rpc_connect: opens a real-time RPC bus to the NM server
     rpc_disconnect: closes the formula's RPC connection to the NM server
     rpc_send:  sends a messsage to the NM server via RPC using this formula's
                current execution token
     rpc_receive:   retrieves any data pending on NM server for this formula's
                    execution token
     rpc_form_query:    sends a form to UI via RPC call and blocks until user
                        submits a response or timeout is exceeded

     The following objects can be sent to the NetMagus server for display in
     the UI:

     rpc_html:  used to send HTML based notices real-time to NM UI for display
                to the end-user
     form:  used to send a form composed of form component objects to ask an
            end-user for input

     The following objects within the sesion can be sent to the NetMagus UI
     inside a form object:

     textarea
     textinput
     radiobutton
     passwordinput
     dropdownmenu
     checkbox

    """

    _log_level_index = {
        0: 0,
        1: logging.DEBUG,
        2: logging.INFO,
        3: logging.WARN,
        4: logging.ERROR,
        5: logging.CRITICAL
    }

    def __init__(self, token, input_file, loglevel, script):
        """
        the launcher will simply parse CLI args and instantiate a new
        NetMagusSession. This will need to receive those CLI args and store
        to internal object state
        """
        self.token = token
        self.input_file = input_file
        self.loglevel = self._log_level_index[int(loglevel)]
        self.script = script
        self.logger = None
        self.nm_input = None
        self.user_state = None

        # Convenience methods for user script writers
        self.rpc_connect = netmagus.rpc.rpc_connect
        self.rpc_disconnect = netmagus.rpc.rpc_disconnect
        self.rpc_form = netmagus.rpc.Form
        self.rpc_html = netmagus.rpc.Html
        self.netopstep = netmagus.form.Form  # for legacy <v0.6.0 compatability
        self.form = netmagus.form.Form
        self.textarea = netmagus.form.TextArea
        self.textinput = netmagus.form.TextInput
        self.radiobutton = netmagus.form.RadioButton
        self.passwordinput = netmagus.form.PasswordInput
        self.dropdownmenu = netmagus.form.DropDownMenu
        self.checkbox = netmagus.form.CheckBox

    def rpc_send(self, message):
        """
        Convenience method to handle the token manipulation for the session.
        See rpc.rpc_send method for full args
        """
        netmagus.rpc.rpc_send(self.token, message)

    def rpc_receive(self):
        """
        Convenience method to handle the token manipulation for the session.
        See rpc.rpc_receive method for full args
        """
        return netmagus.rpc.rpc_receive(self.token)

    def rpc_form_query(self, message, **kwargs):
        """
        Convenience method to handle token manipulation for the session
        :param message: an rpc.Message object to be sent to NetMagus backend
        :param kwargs: see rpc.rpc_form_query for full arg list
        :return:
        """
        return netmagus.rpc.rpc_form_query(self.token, message, **kwargs)

    def start(self):
        """
        Method to start the execution of user code in the user Formula
        :return:
        """
        # if no logging was requested, disabled all output in the logging module
        if not self.loglevel:
            logging.disable(logging.CRITICAL)
        else:
            # Set the logging level here for all steps
            logging.basicConfig(level=self.loglevel)
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(self.loglevel)

        self.__read_response_file()
        self.__read_state_file()
        formula_return = self.__run_user_script()
        self.__write_response_file(formula_return)
        self.__write_state_file(self.user_state)

    def __run_user_script(self):
        try:
            if not os.path.isfile(self.script):
                raise IOError('Path to user script must be a full absolute '
                              'path, not just a file name.')
            sys.path.append(os.path.dirname(self.script))
            module_name = os.path.basename(self.script).split('.')[0]
            self.logger.debug('Importing user module {}'.format(module_name))
            user_module = importlib.import_module(module_name)
            self.logger.debug(
                    '{} imported user module named: {}'.format(
                            type(user_module),
                            user_module))
            formula_return = user_module.run(self)
            if isinstance(formula_return, netmagus.form.Form):
                next_step = formula_return
                self.__fix_formcomponent_indexes(next_step)
                # user must pass full file path back to us for the next
                # script he  wants executed, we add the rest
                next_step.commandPath = ' '.join(
                        [sys.executable, '-m netmagus --script',
                         next_step.commandPath])
            elif isinstance(formula_return, tuple):
                next_step, formula_state = formula_return
                self.__fix_formcomponent_indexes(next_step)
                next_step.commandPath = ''.join(
                        [self.script, next_step.commandPath])
            else:
                raise TypeError(
                        'Formula files should return either Form or tuple('
                        'Form, stateobject)')
            return formula_return
        except ImportError:
            self.logger.critical(
                    'Unable to load the specified python module: {}'.format(
                            self.script))
            raise
        except (Exception, NameError, IOError) as ex:
            self.logger.critical(
                    'Error calling run() method defined in the target file: '
                    '{}'.format(self.script))
            tb = traceback.format_exc()
            logging.exception(ex)
            htmlextrainfo = {
                'html': {
                    'printToUser': True,
                    'outputType': 'html',
                    'title': 'ERROR IN FORMULA',
                    'data': '<h3>This formula has encountered a critical error '
                            'and can not continue.  Please review the '
                            'traceback info and/or contact support for '
                            'assistance.</h3><br><br>Traceback info was: '
                            '<pre>{}</pre>'.format(tb)
                }
            }
            next_step = netmagus.form.Form(currentStep=1,
                                           dataValid=False,
                                           extraInfo=htmlextrainfo)

        return next_step

    def __read_response_file(self):
        """
        Read in the JSON response file from the NetMagus back-end.  These files
        are generated each time the NetMagus backend executes a commandPath to
        launch a task defined in a formula.  Examples would be when a user
        presses the SUBMIT button in the UI, a JSON file is generated by
        NetMagus and stored in a temp file to pass data to the Formula.
        """
        self.logger.debug('Reading JSON data from NetMagus request')
        try:
            with open(self.input_file) as data_file:
                self.nm_input = json.load(data_file)
            os.remove(self.input_file)  # remove file after reading it
        except IOError:
            self.logger.warn('Unable to access input JSON file {}'.format(
                    self.input_file))
        except TypeError:
            self.logger.error('Unable to decode JSON data in {}'.format(
                    self.input_file))

    def __read_state_file(self):
        """
        This method will retrieve any previous state data saved during this
        formula execution and store it internal as self.user_state.
        """
        state_file = self.input_file + '_State'
        with contextlib.closing(
                shelve.open(state_file, protocol=2, writeback=True)) \
                as state_shelve:
            try:
                self.user_state = state_shelve['formula_state']
            except KeyError:
                self.logger.info(
                        'The file {} exists but does not contain previous '
                        'state from a formula execution.  '
                        'Setting state to NONE'.format(state_file))
                self.user_state = None
            except IOError:
                self.logger.info(
                        'No _State file found from previous formula execution '
                        'steps. Setting state to NONE.')
                self.user_state = None

    def __write_response_file(self, response):
        # store the return data into a Response file for NetMagus to
        # continue the op if using file-based exchange
        response_file = self.input_file + 'Response'
        self.logger.debug(
                'Target output JSON file will be: {}'.format(response_file))
        try:
            with open(response_file, 'w') as outfile:
                outfile.write(str(response))
        except IOError:
            self.logger.error(
                    'Unable to open target JSON Response file: {}'.format(
                            response_file))
            raise

    def __write_state_file(self, stateobject):
        """
        store the returned state object into a file for future operation
        steps to retrieve.  Formula creators can return any object in a tuple
        along with their normal Form object fo the next screen in the
        format of (Form, anyobject) to have anyobject saved to disk and passed
        to the next formula execution step where it will be retrieved and stored
        in NetMagusSession.user_state for use by other formula code
        """
        state_file = self.input_file + '_State'
        self.logger.debug(
                'Target output shelve file will be: {}'.format(state_file))
        try:
            with contextlib.closing(shelve.open(state_file, protocol=2,
                                                writeback=True)) as \
                    state_shelve:
                state_shelve['formula_state'] = stateobject
        except IOError:
            self.logger.error(
                    'Unable to open target shelve state file: {}'.format(
                            state_file))
            raise

    @staticmethod
    def __fix_formcomponent_indexes(form_obj):
        """
        This method is a temporary fix to append an index attribute to each
        form component to be sent to NetMagus as JSON.  Eventually this will
        be done in the NetMagus back-end upon receipt according to the order
        of the list of form controls.  For now these are being added here in
        the same fashion before being sent to the NetMagus back-end.
        :param form_obj: a netmagus.NetOpStep object to be serialized and
        sent to NetMagus
        """
        # TODO: REMOVE INDEX INCREMENTING ONCE PROBERT100 FIXES NM
        index_counter = 0
        for item in form_obj.form:
            setattr(item, 'index', index_counter)
            index_counter += 1
