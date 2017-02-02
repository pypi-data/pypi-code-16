from .settings import *
from .extract  import *

def wavelet():

    if '--help' in sys.argv or '-h' in sys.argv:

        print ""
        print "-------------------------------------------------------------------------"
        print ""
        print "description:"
        print ""
        print "  This operation will ."
        print ""
        print "optional arguments:"
        print ""
        print "   --sample            Specify the data to be field sample, not regular"
        print "                       data from fixed location of the stations."
        print ""
        print "-------------------------------------------------------------------------"
        print ""
        quit()        

    t,z,name = magfield('2016-11-11','2016-11-12','byerly',
                        rep='/Users/vincent/ASTRO/data/NURI/samples/byerly/')
    #t,z,name = magfield('2016-03-20','2016-03-20-2','station3',
    #                    rep='/Users/vincent/ASTRO/data/NURI/NURI-station-03/')
    t0   = datetime.fromtimestamp(t[0]).strftime('%Y-%m-%d %H:%M:%S')
    for i in [11,10,9,4]:
        z = signal.decimate(z,i,zero_phase=True)
    z = abs(z)-np.average(abs(z))
    #name = 'station03-160320000000-2016032002000'
    # Decimate data and take 
    t = [t[n*3960] for n in range(len(t)/3960+1)]
    t = [(t[i]-t[0])/60. for i in range(len(t))]
    # Do wavelet analysis
    omega0 = 6
    fct    = "morlet"
    scales = mlpy.wavelet.autoscales(N=len(z),dt=1,dj=0.05,wf=fct,p=omega0)
    spec   = mlpy.wavelet.cwt(z,dt=1,scales=scales,wf=fct,p=omega0)
    freq   = (omega0 + np.sqrt(2.0 + omega0 ** 2)) / (4 * np.pi * scales[1:]) * 1000
    idxs   = np.where(np.logical_or(freq<0.1,1000<freq))[0]
    spec   = np.delete(spec,idxs,0)
    freq   = np.delete(freq,idxs,0)
    # Initialise axis
    fig = figure(figsize=(12,8))
    plt.subplots_adjust(left=0.07, right=0.95, bottom=0.1, top=0.95, hspace=0, wspace=0)
    ax1 = fig.add_axes([0.10,0.75,0.70,0.20])
    ax2 = fig.add_axes([0.10,0.10,0.70,0.60], sharex=ax1)
    ax3 = fig.add_axes([0.83,0.10,0.03,0.60])
    # Plot time series
    ax1.plot(t, z, 'k')
    # Set up axis range for spectrogram
    twin_ax = ax2.twinx()
    twin_ax.set_yscale('log')
    twin_ax.set_xlim(t[0], t[-1])
    twin_ax.set_ylim(freq[-1], freq[0])
    twin_ax.tick_params(which='both', labelleft=True, left=True, labelright=False)
    # Plot spectrogram
    img = ax2.imshow(np.abs(spec),extent=[t[0],t[-1],freq[-1],freq[0]],
                     aspect='auto',interpolation='nearest',cmap=cm.jet,norm=mpl.colors.LogNorm())
    ax2.tick_params(which='both', labelleft=False, left=False)
    ax2.set_ylabel('Frequency [mHz]\n\n')
    ax2.set_xlabel('Time from %s [mins]'%t0)
    fig.colorbar(img, cax=ax3)
    plt.savefig(name+'.png')
    
