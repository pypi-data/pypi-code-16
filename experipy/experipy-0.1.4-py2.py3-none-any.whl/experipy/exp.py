"""
    experipy.exp
    ~~~~~~~~~~~~

    This module provides the Experiment class for running compositions in the
    grammar, as well as the Exp Namespace for controlling and configuring 
    Experiment behavior.
"""
from __future__ import absolute_import

import shutil
import sys

from datetime   import datetime
from os         import chmod, makedirs, path
from subprocess import call
from time       import time

from .system    import cd, cp, mkdir, rm
from .grammar   import Element
from .utils     import Namespace


Exp = Namespace("Exp",
    runsh   = "run.sh",
    shebang = "#!/bin/bash",
    rundir  = "/tmp",
    defname = "exp",
    out     = "raw.out",
    err     = "raw.err",
    timing  = "harness_time.out",
)


class Experiment(object):
    """Experiment objects perform the generation and execution of runscripts.
    
    Once a composition has been specified in the grammar, wrapping it in an
    Experiment allows the user to generate a shell scripts as a string using
    the make_runscript method. The run and queue methods provide mechanisms for
    executing the generated scripts.

    Parameters
    ----------
    cmd : experipy.Element
        A composition of experipy Elements such as Executable and Group, which
        defines the behavior the user wishes the Experiment to perform.
    expname : str
        A name to be used for identifying the experiment. Defaults to 
        Exp.defname, which defaults to "exp"
    destdir : str
        An optional path to a directory where the results from running the
        experiment should be stored. If None, expname will be used.
    """

    def __init__(self, cmd, expname=Exp.defname, destdir=None):
        if not isinstance(cmd, Element):
            raise TypeError("'{}' is not an instance of Element".format(cmd))

        self.cmd     = cmd
        self.expname = expname

        if not destdir:
            self.destdir = path.abspath(expname)
        else:
            self.destdir = path.abspath(destdir)
    

    def make_runscript(self, preamble=Exp.shebang, rm_rundir=True):
        """Create a string containing a complete shell script.

        Parameters
        ----------
        preamble : str
            The first line(s) of the runscript. Defaults to Exp.shebang, which
            defaults to "#!/bin/bash".
        rm_rundir : bool
            If True, a line deleting the experiment's working directory will
            be added to the end of the script. Defaults to True.

        Returns
        -------
        str
            A run script as described by the composition provided to the 
            Experiment.
        """

        # Name of the temporary directory for the experiment
        rundir = path.join(Exp.rundir, self.expname + "." + str(int(time())))
        
        # Start with the preamble
        scriptstr = preamble + "\n\n"
        
        # Collect experiment input files
        scriptstr += "# Experiment setup\n"

        scriptstr += str(mkdir(rundir, make_parents=True)) + "\n"
        scriptstr += str(cd(rundir)) + "\n"

        for infile in self.cmd.inputs():
            scriptstr += str(cp(path.abspath(infile), ".")) + "\n"
        
        # Execute the experiment components
        scriptstr += "\n# Run experiment\n"
        scriptstr += str(self.cmd) + "\n\n"
        
        # Exfill the experiment output files and clean up the rundir if needed
        scriptstr += "# Collect output files and clean up\n"
        for outfile in self.cmd.outputs():
            scriptstr += str(cp(outfile, self.destdir)) + "\n"
        
        if rm_rundir:
            scriptstr += str(rm(rundir)) + "\n"

        return scriptstr

    
    def run(self, rm_rundir=True):
        """Execute the experiment as a subprocess of the current process.

        Generates a run script, writes that script to the results directory,
        and then executes the script as a subprocess of the current process.
        The time the script takes to execute, including loader time, is 
        recorded. This function blocks until the experiment is complete.

        Parameters
        ----------
        rm_rundir : bool
            If True, the directory created for running the experiment will be
            deleted at the end of the experiment. Defaults to True.
        """

        # Create the results directory, deleting any previous contents
        if path.exists(self.destdir):
            shutil.rmtree(self.destdir)
        makedirs(self.destdir)
        
        # Open the output, error and timing file handles for call
        out = open(path.join(self.destdir, Exp.out), 'w')
        err = open(path.join(self.destdir, Exp.err), 'w')
        timing = open(path.join(self.destdir, Exp.timing), 'w')

        # Write the runscript
        fname  = path.join(self.destdir, Exp.runsh)
        with open(fname, "w") as f:
            f.write(self.make_runscript(rm_rundir=rm_rundir))
        chmod(fname, 0755)

        # Execute call and time the result
        start = datetime.now()
        call(fname, stdout=out, stderr=err)
        runtime = datetime.now() - start
        timing.write(str(runtime)+"\n")

        # Clean up and close file descriptors
        out.close()
        err.close()
        timing.close()
        

    def queue(self, nodes=1, ppn=1, mem="4096m", wtime="480:00:00"):
        """Submit the experiment to a job queuing system as a PBS script.
        
        Generates a script with a PBS script header, writes the script to the 
        results directory, and then submits it to the job queuing system by
        running the command qsub as a subprocess.

        Parameters
        ----------
        nodes : int
            The number of nodes to request in the PBS script. Defaults to 1.
        ppn : int
            The number of processors per node to request in the PBS script.
            Defaults to 1.
        mem : str
            The amount of memory to request in the PBS script. Defaults to 
            "4096m".
        wtime : str
            The amount of wall time to request in the PBS script.
        """
       
        # Write the PBS script preamble
        pbsheader = (Exp.shebang
            + "\n#PBS -N {name}\n"
            + "#PBS -l nodes={nodes}:ppn={ppn},mem={mem}\n"
            + "#PBS -l walltime={wtime}\n"
            + "#PBS -o {qout}\n#PBS -e {qerr}"
            + ""
        ).format(name=self.expname, nodes=nodes, ppn=ppn, mem=mem, wtime=wtime,
            qout=path.join(self.destdir, Exp.out), 
            qerr=path.join(self.destdir, Exp.err)
        )
        
        # Create the results directory, deleting any previous contents
        if path.exists(self.destdir):
            shutil.rmtree(self.destdir)
        makedirs(self.destdir)
        
        # Write the runscript
        fname  = path.join(self.destdir, Exp.runsh)
        with open(fname, "w") as f:
            f.write(self.make_runscript(
                preamble=pbsheader, 
                rm_rundir=rm_rundir
            ))
        
        chmod(fname, 0755)
        
        # Submit to the queue
        call(["qsub", fname])
