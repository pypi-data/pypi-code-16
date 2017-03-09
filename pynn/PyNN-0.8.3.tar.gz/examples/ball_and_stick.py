"""
A simple network model made up of ball-and-stick neuron models.

Currently only works with pyNN.neuron, to be generalized in future.

"""

from neuron import h
from nrnutils import Mechanism, Section, DISTAL, alias, uniform_property
import pyNN.neuron as sim
from pyNN.random import NumpyRNG, RandomDistribution
from pyNN.space import Grid2D


class BallAndStickNeuron(object):
    """
    A neuron with a soma and a single dendrite. The dendrite has only
    passive properties, the soma has an integrate-and-fire mechanism.
    
    There is a single synapse in the dendrite.
    """
    
    def __init__(self, **parameters):
        
        # define ion channel parameters
        leak = Mechanism('pas', e=-65, g=parameters['g_leak'])
        
        # create cable sections
        self.soma = Section(L=30, diam=30, Ra=50.0, mechanisms=[leak])
        self.dendrite = Section(L=600, diam=2, Ra=50.0, nseg=5, mechanisms=[leak],
                                parent=self.soma, connection_point=DISTAL)
        
        # insert spike reset mechanism
        self.spike_reset = h.ResetRefrac(0.5, sec=self.soma)
        self.spike_reset.vspike = 40  # (mV) spike height

        # synaptic input
        self.dendrite.add_synapses('ampa', 'Exp2Syn',
                                   locations=[0.5], #0.2, 0.8],
                                   e=0.0, tau1=0.1, tau2=5.0)

        self.parameter_names = ('g_leak', 'v_thresh', 'v_reset', 't_refrac')
        for name, value in parameters.items():
            setattr(self, name, value)

        # needed for PyNN
        self.source_section = self.soma
        self.source = self.spike_reset
        self.rec = h.NetCon(self.source, None)
        self.spike_times = h.Vector(0)
        self.traces = {}
        self.recording_time = False
    
    g_leak = uniform_property(["soma", "dendrite"], "pas.g")
    v_thresh = alias('spike_reset.vthresh')
    v_reset  = alias('spike_reset.vreset')
    t_refrac = alias('spike_reset.trefrac')

    def memb_init(self):
        """needed for PyNN"""
        for sec in (self.soma, self.dendrite):
            for seg in sec:
                seg.v = self.v_init


class BallAndStickNeuronType(sim.NativeCellType):
    default_parameters = {'g_leak': 0.0002, 'v_thresh': -50.0,
                          'v_reset': -65.0, 't_refrac': 5.0}
    default_initial_values = {'v': -65.0}
    receptor_types = ['dendrite.ampa']
    model = BallAndStickNeuron


# -- Build network ----------------------------------------    

sim.setup(timestep=0.1, min_delay=0.5)

n_cells = 100
rng = NumpyRNG(seed=873864267)
v_init = RandomDistribution('uniform', [-65, -55], rng=rng)

neurons = sim.Population(n_cells, BallAndStickNeuronType(),
                         structure=Grid2D(),
                         initial_values={'v': v_init})
connections = sim.Projection(neurons, neurons, sim.FixedProbabilityConnector(0.5),
                             synapse_type=sim.StaticSynapse(weight=0.001, delay=0.5),
                             receptor_type="dendrite.ampa")

# -- Instrument network -----------------------------------

current_source = sim.DCSource(amplitude=0.18, stop=50.0)
current_source.inject_into(neurons[0:10])
neurons.record('spikes')
sample = neurons[(0, 99)]
sample.record(['v', 'dendrite(0.5).v'])


# -- Run simulation and retrieve data ---------------------

sim.run(100.0)
data = neurons.get_data().segments[0]
sim.end()


# -- Plotting ---------------------------------------------

from pyNN.utility.plotting import Figure, Panel

vm_soma = data.filter(name="v")[0]
vm_dend = data.filter(name="dendrite(0.5).v")[0]

Figure(
    Panel(vm_soma, vm_dend, ylabel="Membrane potential (mV)", data_labels=["Soma", "Dendrite"]),
    Panel(data.spiketrains, xlabel="Time (ms)"),
    title="Ball and stick network",
).save("ball_and_stick.png")


    
