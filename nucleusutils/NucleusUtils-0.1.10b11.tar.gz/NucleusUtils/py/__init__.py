import sys


def check_py_version(*required_version):
    if not required_version <= sys.version_info:
        raise RuntimeError(
            "Required Python-{} but executed with Python-{}".format('.'.join(map(str, required_version)),
                                                                    sys.version.split(' ')[0]))
    return True
