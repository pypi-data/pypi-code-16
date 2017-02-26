"""
.. moduleauthor:: Chris Dusold <PySpeedup@chrisdusold.com>


"""

import random
import numpy
#import matplotlib.pyplot as plt
#import time

def halfIteration(function, fDomain, fRange=None, threshold=.01):
    """A function that takes a mapping and uses a local search to find
    a half iteration approximation and returns a function that will
    reproduce the results."""
    if fRange is not None:
        hDomain=(min(fDomain[0],fRange[0]),max(fDomain[-1],fRange[-1]))
        step = float(min(fDomain[1]-fDomain[0],fRange[1]-fRange[0],(hDomain[1]-hDomain[0])/10.))
    else:
        step = float(min(fDomain[1]-fDomain[0],(fDomain[1]-fDomain[0])/10.))
        d = [fDomain[0]+step*x for x in range(int((fDomain[-1]-fDomain[0])/step)+1)]
        f=[function(x) for x in d]
        hDomain = (min(fDomain[0],min(f)),max(fDomain[-1],max(f)))
    step
    d = [hDomain[0]+step*x for x in range(int((hDomain[-1]-hDomain[0])/step)+1)]
    h = [x for x in d]
    #TODO: Make a graph for progress display.
    def hGet(x):
        return numpy.interp(x,d,h)
    def hSet(x,y):
        h0=hGet(x)
        hp=y-h0
        i=(x-hDomain[0])/step
        #TODO: Adjust slope?
        i0=int(i)
        hp0=hp
        h[i0]+=hp0
        while abs(hp0)>step*threshold and i0>0:
            i0-=1
            hp0*=0.5
            h[i0]+=hp0
        i0=int(i)
        hp0=hp
        if i%1 and i<len(h)-1:
            i0+=1
            h[i0]+=hp0
        while abs(hp0)>step*threshold and i0<len(h)-1:
            i0+=1
            hp0*=0.5
            h[i0]+=hp0
    recursiveAve=step
    #fig = plt.figure()
    #ax = fig.add_subplot(111)
    #ax.plot(d,[function(x) for x in d],'r-')
    #line1,=ax.plot(d,h,'b-')
    #plt.show(block=False)
    i=0
    while recursiveAve>step*threshold:
        x = random.uniform(fDomain[0],fDomain[-1])
        y = function(x)
        y0 = hGet(x)
        if y0>hDomain[1]:
            y0=hDomain[1]
            hSet(x,y0)
        if y0<hDomain[0]:
            y0=hDomain[0]
            hSet(x,y0)
        y1 = hGet(y0)
        yp = y-y1
        y2 = (yp)/2 + y1
        hSet(y0,y2)
        recursiveAve+=abs(yp)
        recursiveAve/=2
        #if not i%1000:
        #    line1.set_ydata(h)
        #    fig.canvas.draw()
        #    plt.show(block=False)
        #    time.sleep(1)
        i+=1
    return hGet

h=halfIteration(lambda x:x**2,(0,0.1,10),(0,100))
