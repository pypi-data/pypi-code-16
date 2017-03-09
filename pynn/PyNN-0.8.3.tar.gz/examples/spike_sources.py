"""
A demonstation of the different types of spike generator available in PyNN.


Usage: spike_sources.py [-h] [--plot-figure] simulator

positional arguments:
  simulator      neuron, nest, brian or another backend simulator

optional arguments:
  -h, --help     show this help message and exit
  --plot-figure  Plot the simulation results to a file.

"""


import numpy as np
from pyNN.utility import get_simulator, normalized_filename, ProgressBar
from pyNN.utility.plotting import Figure, Panel, isi_histogram

sim, options = get_simulator(("--plot-figure", "Plot the simulation results to a file.",
                              {"action": "store_true"}))

sim.setup()

source_types = [(sim.SpikeSourcePoisson, {"rate": 100.0}),
                (sim.SpikeSourceGamma, {"beta": 100.0, "alpha": 2.0}),
                (sim.SpikeSourcePoissonRefractory, {"rate": 100.0, "tau_refrac": 5.0})]

populations = [sim.Population(100, cell_type(**parameters), label=cell_type.__name__)
               for cell_type, parameters in source_types]
all = sum(populations[1:], populations[0])
all.record('spikes')

sim.run(1000.0)

data = [population.get_data().segments[0]
        for population in populations]

if options.plot_figure:
    # perhaps better to plot histograms of interspike intervals
    #panels = [Panel(segment.spiketrains, xlabel="Time (ms)", xticks=True, markersize=0.1)
    #          for segment in data]
    panels = [Panel(isi_histogram(segment), xticks=True, yticks=True,
                    data_labels=[segment.description.split('\n')[0]])
              for segment in data]
    panels[0].options['ylabel'] = "Count"
    panels[-1].options['xlabel'] = "Inter-spike interval (ms)"
    figure_filename = normalized_filename("Results", "spike_sources", "png", options.simulator)
    Figure(title="Spike trains with Poisson and Gamma statistics",
           annotations="Simulated with %s" % options.simulator.upper(),
           *panels
    ).save(figure_filename)
    print(figure_filename)

sim.end()