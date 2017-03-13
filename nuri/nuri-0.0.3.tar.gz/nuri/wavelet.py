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
        print "required arguments:"
        print ""
        print "   --start          Starting date to retrieve data from."
        print "   --end            Ending date to retrieve data from."
        print "   --station        Station name"
        print ""
        print "optional arguments:"
        print ""
        print "   --orientation    Orientation to extract if single (all by default)"
        print "   --path           Custom repository where data are stored."
        print "   --sample         Specify the data to be field sample, not regular."
        print "   --unit           Time unit for plot."
        print ""
        print "example:"
        print ""
        print "  nuri wavelet --station station4 --start 2016-03-20 --end 2016-03-21 \ "
        print "               --path /Users/vincent/ASTRO/data/NURI/NURI-station-04/"
        print ""
        print "  nuri wavelet --station byerly --start 2016-11-11 --end 2016-11-12 \ "
        print "               --path /Users/vincent/ASTRO/data/NURI/samples/byerly/"
        print ""
        print "-------------------------------------------------------------------------"
        print ""
        quit()
        
    if setup.station==None or setup.start==None or setup.end==None:
        print '\nERROR: station or start or end dates not specified...\n'
        quit()
    t,x,y,z = magfield(setup.start,setup.end,rep=setup.path)
    # Create x axis time label
    t0 = datetime.fromtimestamp(t[0]).strftime('%Y-%m-%d %H:%M:%S')
    t1 = datetime.fromtimestamp(t[-1]).strftime('%Y-%m-%d %H:%M:%S')
    label1 = 'Local time from %s to %s [%s]'%(t0,t1,setup.unit)
    # Create filename
    t0 = datetime.fromtimestamp(t[0]).strftime('%y%m%d_%H%M%S')
    t1 = datetime.fromtimestamp(t[-1]).strftime('%y%m%d_%H%M%S')
    label2 = '%s-%s-%s.png'%(setup.station,t0,t1)
    # Decimate magnetic field data to 1 sample/second
    rate = [11,10,9,4] if setup.rate==3960. else [setup.rate]
    for i in rate:
        z = signal.decimate(z,i,zero_phase=True)
    # Extract time every 3960 sample
    t = [t[n*3960] for n in range(len(t)/3960+1)]
    # Convert every timing points to scale (hr,min,sec) units
    s = 1. if setup.unit=='secs' else 60. if setup.unit=='mins' else 3600.
    t = [(t[i]-t[0])/s for i in range(len(t))]
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
    ax1.plot(t,abs(z)-np.average(abs(z)),'k')
    ax1.set_ylabel('Magnetic Fields [uT]\n\n')
    # Set up axis range for spectrogram
    twin_ax = ax2.twinx()
    twin_ax.set_yscale('log')
    twin_ax.set_xlim(t[0], t[-1])
    twin_ax.set_ylim(freq[-1], freq[0])
    twin_ax.tick_params(which='both', labelleft=True, left=True, labelright=False)
    # Plot spectrogram
    img = ax2.imshow(np.abs(spec)**2,extent=[t[0],t[-1],freq[-1],freq[0]],
                     aspect='auto',interpolation='nearest',cmap=cm.jet,norm=mpl.colors.LogNorm()) # cm.cubehelix
    ax2.tick_params(which='both', labelleft=False, left=False)
    ax2.set_xlabel(label1)
    ax2.set_ylabel('Frequency [mHz]\n\n')
    fig.colorbar(img, cax=ax3)
    plt.savefig(label2)
    
