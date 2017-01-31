from os                 import path

from experipy.utils     import Namespace
from experipy.grammar   import Executable

from .environment       import Env

########## Constants and helper functions ##########

Ram = Namespace("Ramulator",
    path = "multicore_ramulator",
    exe  = "ramulator",
)

def ramulator_path():
    return path.join(Env.projdir, Ram.path)

def config_path(cfg):
    return path.join(ramulator_path(), "configs", 
        "{}-config.cfg".format(cfg)
    )

def stat_file(cfg):
    return "{}.stats.txt".format(cfg.lower())

####################################################

def ramulator(t1_cfg, t2_cfg, *traces, **kwargs):
    """Returns an Executable describing a ramulator run"""
    opts = [
        config_path(t1_cfg), config_path(t2_cfg), "--mode=cpu",
        "--stats_1 {}".format(stat_file(t1_cfg)),
        "--stats_2 {}".format(stat_file(t2_cfg)),
    ]

    outfiles = kwargs.get("outputs", [])
    outfiles.extend([stat_file(t1_cfg), stat_file(t2_cfg)])

    if "t1_limit" in kwargs:
        opts.append("--t1_limit {}".format(kwargs["t1_limit"]))

    return Executable(path.join(ramulator_path(), "ramulator"),
        opts + list(traces), 
         outputs=outfiles
    )
