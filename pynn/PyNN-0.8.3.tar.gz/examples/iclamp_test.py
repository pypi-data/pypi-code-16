
import matplotlib.pyplot as plt
from neuron import h

h('create soma')

amp1 = h.Vector([0.0, 0.5, 1.0, 0.5, 0.0])
t1 = h.Vector([0.0, 2.0, 5.0, 7.0, 10.0])
amp2 = h.Vector([0.0, 1.0, 2.0, 1.0, 0.0])
t2 = h.Vector([10.0, 12.0, 15.0, 17.0, 20.0])

rec = h.Vector()

iclamp = h.IClamp(0.5, sec=h.soma)
iclamp.delay = 0
iclamp.dur = 1e9

rec.record(iclamp._ref_i)
#rec.record(h.soma(0.5)._ref_v)

amp1.play(iclamp._ref_amp, t1)
#amp2.play(iclamp._ref_amp, t2)

#amp1.append(amp2)
#t1.append(t2)

h.finitialize()
while h.t < 9.9:
    h.fadvance(0.1)
amp1.append(amp2)
t1.append(t2)
while h.t < 20.0:
    h.fadvance(0.1)



plt.plot(rec)
plt.show()
