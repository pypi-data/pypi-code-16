from IPython import get_ipython  # For syntax (re-imported by default when a Notebook starts)
import declarativewidgets as dwidgets


# ======================================================================================================================
# Define functions
# ======================================================================================================================
def sync_notebook_to_manager():
    """
    Sync namespace: Notebook ==> Manager.
    :return: None
    """

    mgr.update_namespace(globals())


def sync_manager_to_notebook():
    """
    Sync namespace: Manager ==> Notebook.
    :return: None
    """

    for n, v in mgr.namespace.items():
        globals()[n] = v


def load_gui():
    """
    Load GUI components.
    :return: None
    """

    dwidgets.init()

    imports = '''
        <link rel='import' href='urth_components/iron-form/iron-form.html'
              is='urth-core-import' package='PolymerElements/iron-form'>
        <link rel='import' href='urth_components/iron-collapse/iron-collapse.html'
              is='urth-core-import' package='PolymerElements/iron-collapse'>
        <link rel='import' href='urth_components/paper-input/paper-input.html'
              is='urth-core-import' package='PolymerElements/paper-input'>
        <link rel='import' href='urth_components/iron-label/iron-label.html'
              is='urth-core-import' package='PolymerElements/iron-label'>
        <link rel='import' href='urth_components/paper-button/paper-button.html'
              is='urth-core-import' package='PolymerElements/paper-button'>
        <link rel='import' href='urth_components/iron-icon/iron-icon.html'
              is='urth-core-import' package='PolymerElements/iron-icon'>
        <link rel='import' href='urth_components/paper-material/paper-material.html'
              is='urth-core-import' package='PolymerElements/paper-material'>
        <link rel='import' href='urth_components/paper-header-panel/paper-header-panel.html'
              is='urth-core-import' package='PolymerElements/paper-header-panel'>
        <link rel='import' href='urth_components/iron-collapse/iron-collapse.html'
              is='urth-core-import' package='PolymerElements/iron-collapse'>
        <link rel='import' href='urth_components/paper-collapse-item/paper-collapse-item.html'
              is='urth-core-import' package='Collaborne/paper-collapse-item'>
        '''

    get_ipython().run_cell_magic('HTML', '', imports)


def log_progress(iterable, every=None, size=None, name='Items'):
    """

    :param iterable:
    :param every:
    :param size:
    :param name:
    :return: None
    """

    from ipywidgets import IntProgress, HTML, VBox
    from IPython.display import display

    is_iterator = False
    if size is None:
        try:
            size = len(iterable)
        except TypeError:
            is_iterator = True
    if size is not None:
        if every is None:
            if size <= 200:
                every = 1
            else:
                every = int(size / 200)  # every 0.5%
    else:
        assert every is not None, 'sequence is iterator, set every'

    if is_iterator:
        progress = IntProgress(min=0, max=1, value=1)
        progress.bar_style = 'info'
    else:
        progress = IntProgress(min=0, max=size, value=0)
    label = HTML()
    box = VBox(children=[label, progress])
    display(box)

    index = 0
    try:
        for index, record in enumerate(iterable, 1):
            if index == 1 or index % every == 0:
                if is_iterator:
                    label.value = '{name}: {index} / ?'.format(
                        name=name,
                        index=index
                    )
                else:
                    progress.value = index
                    label.value = u'{name}: {index} / {size}'.format(
                        name=name,
                        index=index,
                        size=size
                    )
            yield record
    except:
        progress.bar_style = 'danger'
        raise
    else:
        progress.bar_style = 'success'
        progress.value = index
        label.value = "{name}: {index}".format(
            name=name,
            index=str(index or '?')
        )


# ======================================================================================================================
# Register
# ======================================================================================================================
# TODO: remove the check?
# Register post execute cell callback
if sync_notebook_to_manager not in get_ipython().events.callbacks['post_execute']:
    get_ipython().events.register('post_execute', sync_notebook_to_manager)

# ======================================================================================================================
# Start up Manager
# ======================================================================================================================

# Initialize a Manager
import simpli

# TODO: rename to 'manager'
global mgr
mgr = simpli.Manager()
sync_notebook_to_manager()

# ======================================================================================================================
# Load GUI
# ======================================================================================================================
load_gui()

# ======================================================================================================================
# Load extensions
# ======================================================================================================================
get_ipython().magic('load_ext autoreload')
get_ipython().magic('autoreload 2')
get_ipython().magic('matplotlib inline')

# ======================================================================================================================
# Start up Notebook Package
# ======================================================================================================================
try:
    from environment import *
except:
    pass
