# coding: utf-8

import subprocess


def launch_external_program(command, verbose=False):
    """Run external command."""
    try:
        if verbose:
            result = subprocess.check_call(command)
        else:
            # stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            result = subprocess.check_call(
                command
            )

    except subprocess.CalledProcessError:
        return False

    if result == 0:
        return True
    else:
        return False
