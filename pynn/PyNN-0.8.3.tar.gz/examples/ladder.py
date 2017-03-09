"""

Andrew Davison, UNIC, CNRS
April 2013

"""

from pyNN.utility import init_logging, normalized_filename
from importlib import import_module
import numpy
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('simulator_name')
parser.add_argument("--debug", action="store_true")
args = parser.parse_args()

init_logging(None, debug=args.debug)

sim = import_module("pyNN.%s" % args.simulator_name)

simtime = 100.0
n_cells = 5

sim.setup()

cell_type = sim.IF_cond_exp(tau_m=10.0,
                            i_offset=0.1*i)

cells = sim.Population(n_cells, cell_type,
                       label="cells")

cells.record(['spikes', 'v'])


sim.run(100.0)

filename = normalized_filename("Results", "ladder", "pkl",
                               args.simulator_name)
cells.write_data(filename, annotations={'script_name': __file__})

sim.end()