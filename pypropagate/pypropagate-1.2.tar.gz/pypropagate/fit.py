


def fit_gaussians(array,N,periodic = False,plot = False):
    import numpy as np
    from scipy.optimize import curve_fit
    import expresso.pycas as pc
    dx = array._dbounds[0]
    xvalues = np.linspace(float(array.bounds[0][0]/dx),float(array.bounds[0][1]/dx),array.shape[0])
    yvalues = array.data.copy()
    gaussian = lambda x,a,x0,s: a*np.exp(-(x-x0)**2/(2*s**2))
    parameters = []
    sigmas = []
    shifts = 0
    for i in range(N):
        ymax = yvalues.max()
        center_idx = np.where(yvalues == ymax)[0][0]
        if periodic:
            yvalues = np.roll(yvalues,len(yvalues)/2 - center_idx)
            center_x = xvalues[len(yvalues)/2]
            shifts += len(yvalues)/2 - center_idx
        else:
            center_x = xvalues[center_idx]
        p0 = [ymax,center_x,(xvalues[-1] - xvalues[0])/100]
        popt,pcov = curve_fit(gaussian,xvalues,yvalues,p0 = p0)
        if plot:
	    import matplotlib.pyplot as plt
            plt.figure()
            plt.plot(xvalues,yvalues,label='data')
            plt.plot(xvalues,gaussian(xvalues,*p0),'--',label='initial')
            plt.plot(xvalues,gaussian(xvalues,*popt),'--',label='fit')
            plt.legend()
            plt.show()
        yvalues -= gaussian(xvalues,*popt)
        parameters.append((popt[0],(popt[1] - shifts)*dx,popt[2]*dx))
        sigmas.append((pcov[0][0],pc.sqrt(pcov[1][1])*dx,pc.sqrt(pcov[2][2])*dx))
    return parameters,sigmas

