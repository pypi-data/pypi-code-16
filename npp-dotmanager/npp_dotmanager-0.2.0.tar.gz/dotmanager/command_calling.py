import subprocess
import shlex


def call_command(command):
    """Executes a shell command through the subprocess module. Returns
    a tuple (stdout, stderr)."""
    process = subprocess.Popen(shlex.split(command),
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               universal_newlines=False,)
    return process.communicate()
