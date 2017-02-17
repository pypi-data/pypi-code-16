from neurodynex.brunel_model import LIF_spiking_network
from neurodynex.tools import plot_tools, spike_tools
import brian2 as b2
import numpy as np
import matplotlib.pyplot as plt


if __name__ == "__main__":
    poisson_rate = 35*b2.Hz
    g = 7.8
    CE = 5000

    delta_t = 0.1 * b2.ms
    delta_f = 5. * b2.Hz
    T_init = 100 * b2.ms
    k = 9

    f_max = 1./(2. * delta_t)
    N_samples = 2. * f_max / delta_f
    T_signal = N_samples * delta_t
    T_sim = k * T_signal + T_init

    print("Start simulation. T_sim={}, T_signal={}. N_samples={}".format(T_sim, T_signal, N_samples))
    b2.defaultclock.dt = delta_t
    stime = T_sim + (10 + k) * b2.defaultclock.dt  # add a few extra samples (solves rounding issues)
    rate_monitor, spike_monitor, voltage_monitor, monitored_spike_idx = \
        LIF_spiking_network.simulate_brunel_network(
            N_Excit=CE, poisson_input_rate=poisson_rate, g=g, sim_time=stime)

    plot_tools.plot_network_activity(rate_monitor, spike_monitor, voltage_monitor,
                                     spike_train_idx_list=monitored_spike_idx, t_min=0*b2.ms)
    plot_tools.plot_network_activity(rate_monitor, spike_monitor, voltage_monitor,
                                     spike_train_idx_list=monitored_spike_idx, t_min=T_sim - 80*b2.ms)
    spike_stats = spike_tools.get_spike_train_stats(spike_monitor, window_t_min=150.*b2.ms)
    plot_tools.plot_ISI_distribution(spike_stats, hist_nr_bins=77, xlim_max_ISI=100*b2.ms)

    #     # Power Spectrum
    pop_freqs, pop_ps, average_population_rate = \
        spike_tools.get_population_activity_power_spectrum(
            rate_monitor, delta_f, k, T_init, subtract_mean_activity=True)

    plot_tools.plot_population_activity_power_spectrum(pop_freqs, pop_ps, 1000*b2.Hz, average_population_rate)
    plt.show()

    freq, mean_ps, all_ps, mean_firing_rate, all_mean_firing_freqs = \
        spike_tools.get_averaged_single_neuron_power_spectrum(
            spike_monitor, sampling_frequency=1./delta_t, window_t_min=100.*b2.ms,
            window_t_max=T_sim,  subtract_mean=False, nr_neurons_average=200)
    print("plot_spike_train_power_spectrum")
    plot_tools.plot_spike_train_power_spectrum(freq, mean_ps, all_ps, 1000 * b2.Hz,
                                               mean_firing_freqs_per_neuron=all_mean_firing_freqs,
                                               nr_highlighted_neurons=2)
    plt.show()

    print("done")
