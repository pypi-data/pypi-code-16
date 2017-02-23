from os.path import join, dirname, realpath

from .support import establish_filepath, get_home_dir

# ======================================================================================================================
# Set up Simpli
# ======================================================================================================================
# Store user-home directory in a variable
HOME_DIR = get_home_dir()

# Make a hidden directory in the user-home directory
SIMPLI_DIR = join(HOME_DIR, '.Simpli')
SIMPLI_JSON_DIR = join(SIMPLI_DIR, 'json', '')
establish_filepath(SIMPLI_JSON_DIR)

# Link default and nbpackage JSONs
from .default_tasks import link_json

link_json(join(dirname(realpath(__file__)), 'default_tasks.json'))
link_json(join(dirname(realpath(__file__)), 'nbpackage_tasks.json'))

from .manager import Manager


# ======================================================================================================================
# Set up Jupyter widget
# ======================================================================================================================
def _jupyter_nbextension_paths():
    """
    Required function to add things to the nbextension path.
    :return: list; List of 1 dictionary
    """

    # section: the path is relative to the simpli/ directory (if viewing from the repository: it's simpli/simpli/)
    # dest: Jupyter sets up: server(such as localhost:8888)/nbextensions/dest/
    # src: Jupyter sees this directory (not all files however) when it looks at dest (server/nbextensions/dest/)
    # require: Jupyter loads this file; things in this javascript will be seen
    # in the javascript namespace
    to_return = {'section': 'notebook',
                 'src': 'static',
                 'dest': 'simpli',
                 'require': 'simpli/main'}

    return [to_return]


def _jupyter_server_extension_paths():
    """
    Required function to add things to the server extension path.
    :return: list; List of 1 dictionary
    """

    to_return = {'module': 'simpli'}
    return [to_return]


# TODO: understand better
def load_jupyter_server_extension(nbapp):
    """
    Function to be called when server extension is loaded.
    :param nbapp: NotebookWebApplication; handle to the Notebook web-server instance
    :return: None
    """

    # Print statement to show extension is loaded
    nbapp.log.info('\n\n********* Simpli on *********\n')
