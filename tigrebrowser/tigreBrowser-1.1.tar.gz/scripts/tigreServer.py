#!/usr/bin/python
import sys
import os
import webbrowser
from optparse import OptionParser, OptionGroup
from threading import Thread
import pkg_resources

try: # Python >=3.0
    from configparser import RawConfigParser
    from http.server import CGIHTTPRequestHandler, HTTPServer
    from tkinter import *
    from tkinter.filedialog import askopenfilename
    from tkinter.messagebox import *
except ImportError: # Python <3.0
    from ConfigParser import RawConfigParser
    from CGIHTTPServer import CGIHTTPRequestHandler
    from BaseHTTPServer import HTTPServer
    from Tkinter import *
    from tkFileDialog import askopenfilename
    from tkMessageBox import *

# Config file for server
CONFIG_FILE = 'tigreBrowser.cfg'
DEFAULT_CONFIG_FILE = pkg_resources.resource_filename('tigreBrowser', 'cgi/tigreBrowser/tigreBrowser.cfg')
CGI_DIR = pkg_resources.resource_filename('tigreBrowser', 'cgi')
BROWSER_DIR = '/tigreBrowser'

def start_server(port):
    """Starts a CGI HTTP server at the given port.
    CGI scripts (.cgi file extension) are executed in the BROWSER_DIR
    directory.
    """
    class Handler(CGIHTTPRequestHandler):
        cgi_directories = [BROWSER_DIR]
        def is_cgi(self):
            """The pathname is considered a CGI file if the CGIHTTPRequestHandler
            returns true for is_cgi(), the file is executable and the file
            extension of the file is .cgi.
            """
            path = self.path
            match = False

            for x in self.cgi_directories:
                i = len(x)
                if path[:i] == x and (not path[i:] or path[i] == '/'):
                    self.cgi_info = path[:i], path[i+1:]
                    match = True

            if match:
                name = self.path.split('?', 2)[0]
                file = self.translate_path(name)
                if not self.is_executable(file):
                    return False
                if not file.endswith('.cgi'):
                    return False
                return True
            return False

    os.chdir(CGI_DIR)
    httpd = HTTPServer(("", port), Handler)
    print("Result browser running on http://localhost:" + str(port) + "/" + BROWSER_DIR.strip('/') + "/tigreBrowser.cgi")

    try:
        httpd.serve_forever()
    except (KeyboardInterrupt, SystemExit):
        print("\nTerminating result browser")

def read_config_file(config_file):
    """Reads the config file.
    Returns port setting from the config file.
    """
    config = RawConfigParser()
    if not config.read(config_file):
        print("Could not find config file '%s'" % config_file)
        return 9999

    try:
        port = config.getint('server', 'port')
    except (Exception,):
        e = sys.exc_info()[1]
        print("Error in config file: %s" % e)
        sys.exit(1)
    return port

def read_commandline_options(config_file):
    """Reads command-line options.
    If database file is given as an option, the gui doesn't have to run.
    Also, this function passes the database file as an environment variable
    to the actual browser.
    """
    usage = "These options override the options set in the '%s' config file\n" % config_file + "usage: %prog [options]"
    parser = OptionParser(usage)
    group_server = OptionGroup(parser, 'Server options')
    group_browser = OptionGroup(parser, 'Result browser options')

    group_server.add_option('-p', '--port', dest='port', type='int',
                            action='store', help='server port', default=None)

    group_browser.add_option('-d', '--database', dest='database_file',
                             type='string', action='store',
                             help='database file for the result browser',
                             default=None)

    parser.add_option_group(group_server)
    parser.add_option_group(group_browser)
    (options, args) = parser.parse_args()

    run_gui = True
    if options.database_file:
        os.environ['RESULT_BROWSER_DATABASE'] = os.path.join(os.getcwd(), options.database_file)
        run_gui = False

    return options.port, run_gui

def get_database_file_error(database_file):
    """Check if the database file is OK for the browser (i.e. the file exists
    and the file is not writable)

    Returns an error string describing the issue with the database file
    or None if there are no issues.
    """
    if not os.path.isfile(database_file):
        return "Database file not found"
    if os.access(database_file, os.W_OK):
        return "Database file must not have write permissions"

class TigreBrowser(Frame):
    """GUI config window for tigreServer and tigreBrowser.
    Creates a window with database file selection and controls to start
    or stop the server.
    """
    def __init__(self, port, master=None):
        """Creates a new window.
        """
        Frame.__init__(self, master)
        self.root = master
        self.root.protocol("WM_DELETE_WINDOW", sys.exit)
        self.thread = None
        self.port = port
        self.pack()
        self.__create_widgets()

    def __create_widgets(self):
        """Creates all widgets.
        """
        self.title = Label(self, text="tigreBrowser", font="Helvetica 20", anchor=NW, justify=LEFT, pady=10)
        self.title.pack({"side": "top"})

        self.file_frame = Frame(self, pady=10)
        self.file_frame.pack()

        self.label = Label(self.file_frame, text="Select a database file")
        self.label.pack({"side": "left"})

        self.open = Button(self.file_frame, text="Open database file", command=self.__open_db)
        self.open.pack({"side": "right"})

        self.button_frame = Frame(self)
        self.button_frame.pack()

        self.start = Button(self.button_frame, text="Start server", command=self.__start_server, state=DISABLED)
        self.start.pack({"side": "left"})

        self.stop = Button(self.button_frame, text="Stop server", command=self.__stop_server, state=DISABLED)
        self.stop.pack({"side": "right"})

    def __open_db(self):
        """Opens a file dialog for user to select the database file.
        Shows an error in case on an error.
        Adds a label indicating the filename after the selection is done.
        Also, passes the database file to tigreBrowser using an environment variable.
        """
        database_file = askopenfilename(filetypes=[("SQLite database files", "*.sqlite"), ("All files", "*")])
        if not database_file:
            return
        message = get_database_file_error(database_file)
        if message:
            showerror("Error!", message)
            return
        os.environ['RESULT_BROWSER_DATABASE'] = database_file
        self.start.config(state=NORMAL)

        self.filename = Label(self, text=database_file, pady=5)
        self.filename.pack()

    def __start_server(self):
        """Starts the CGI HTTP server as a new thread.
        Adds a label indicating the URL of tigreBrowser.
        """
        print("Starting server")
        self.thread = Thread(target=start_server, args=(self.port, ))
        self.thread.start()
        self.start.config(state=DISABLED)
        self.open.config(state=DISABLED)
        self.stop.config(state=NORMAL)
        url = "http://localhost:" + str(port) + "/" + BROWSER_DIR.strip('/') + "/tigreBrowser.cgi"
        l = Label(self, text="Result browser running on:")
        l.pack()
        button = Button(self, text=url, command=lambda: webbrowser.open(url), fg="blue", activeforeground="blue", bd=0, font=("Helvetica", 11, "underline"))
        button.pack()

    def __stop_server(self):
        """Stops the server and exits the application.
        Note: there is no way to just kill the thread running the server.
        Therefore one must exit the whole application.
        """
        print("Stopping server")
        self.start.config(state=NORMAL)
        self.open.config(state=NORMAL)
        sys.exit()

def create_gui(port):
    """Creates and starts the server GUI.
    """
    root = Tk()
    app = TigreBrowser(port, master=root)
    root.title("TigreBrowser")
    app.mainloop()
    root.destroy

if __name__ == "__main__":
    if os.path.isfile(CONFIG_FILE):
        myconfig = CONFIG_FILE
        os.environ['TIGREBROWSER_CONFIG'] = os.path.join(os.getcwd(), myconfig)
    else:
        myconfig = DEFAULT_CONFIG_FILE
    port_cfg = read_config_file(myconfig)
    port_cli, run_gui = read_commandline_options(myconfig)
    port = port_cli or port_cfg

    if run_gui:
        create_gui(port)
    else:
        start_server(port)
