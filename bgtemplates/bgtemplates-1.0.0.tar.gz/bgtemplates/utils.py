"""
Module with general utilities used by bgtemplates
"""
import os
import shlex
import shutil
import subprocess
import logging
from types import SimpleNamespace


def remove_file(f):
    """
    Remove file without raising an error if the file does not exist

    Args:
        f (str): path to the file
    """
    try:
        os.remove(f)
    except OSError:
        pass


def launch_cmd(cmd):
    """
    Executes a command as a subprocess

    Args:
        cmd (str): command to be executed

    Returns:
        CompletedProcess.

    Raises:
        CalledProcessError.

    """
    logging.debug('Executing command {}'.format(cmd))

    with subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
        try:
            stdout, stderr = process.communicate()
        except:
            process.kill()
            process.wait()
            raise
        retcode = process.poll()
        if retcode:
            logging.debug('Error in subprocess with cmd {}'.format(cmd))
            raise subprocess.CalledProcessError(retcode, process.args,
                                                output=stdout, stderr=stderr)
    out = SimpleNamespace()
    out.stdout = stdout
    out.stderr = stderr
    return out


def path_to_executable(executable):
    """
    Returns the path to an executable

    Args:
        executable (str): name of executable

    Returns:
        str. Path to the executable

    """
    return shutil.which(executable)


def is_executable(executable):
    """
    Checks whether a command is executable or not

    Args:
        executable (str): command

    Returns:
        bool.

    """
    return False if shutil.which(executable) is None else True
    # alternative implementation
    #return os.path.exists(executable) and os.access(executable, os.X_OK)


def install_developer_mode(pip_path, project_path):
    """
    Install a project in developer

    Args:
        pip_path (str): path to the pip bin
        project_path (str): path to the project folder with the :file:`setup.py`

    """
    logging.info('Installing project in development mode: $ pip install -e {}'.format(project_path))
    cmd = ' '.join([pip_path, 'install', '-e', project_path])
    try:
        launch_cmd(cmd)
    except Exception:
        logging.warning('Error installing the project')


def which(program):
    fpath, fname = os.path.split(program)
    if fpath:
        if is_executable(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_executable(exe_file):
                return exe_file
