import sys
import os
from .core import ninja_generate
from .io.read import read_config_files
from .tk import ioTK


def main(f_out, args):
    if os.path.splitext(f_out)[1] == ".yaml":
        args = [f_out] + args
        f_out = "build.ninja"
    else:
        pass

    ioTK.save_text(
            f_out,
            ninja_generate(read_config_files(args))
        )
    print("output =", f_out)
