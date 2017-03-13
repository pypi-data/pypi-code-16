from .settings import *
from .extract  import *

def transform():
    
    if '--help' in sys.argv or '-h' in sys.argv:
        
        print ""
        print "-------------------------------------------------------------------------"
        print ""
        print "description:"
        print ""
        print "  This operation will plot the Fourier transform of given time series."
        print "  The time series and FFT are shown interactively so the user can select"
        print "  a desired time slot and get the FFT from that region."
        print ""
        print "required arguments:"
        print ""
        print "   --start          Starting date to retrieve data from."
        print "   --end            Ending date to retrieve data from."
        print "   --station        Station name"
        print ""
        print "optional arguments:"
        print ""
        print "   --discard        Discard first selected seconds"
        print "   --fmin           Minimum frequency to display"
        print "   --fmax           Maximum frequency to display"
        print "   --nogps          No GPS provided, create time array using sample rate"
        print "   --orientation    Orientation to extract if single (all by default)"
        print "   --path           Custom repository where data are stored."
        print "   --sample         Specify the data to be field sample, not regular."
        print "   --scale          Rescale y axis"
        print "   --unit           Time unit for plot."
        print ""
        print "example:"
        print ""
        print "  nuri transform --start 2017-03-09-15-58 --end 2017-03-10 \ "
        print "                 --path /Users/vincent/ASTRO/data/others/sample1_background_noise/ \ "
        print "                 --station magnet --sample --unit secs --nogps \ "
        print "                 --discard 1 --fmin 1 --down 12 --seaborn"
        print ""
        print "-------------------------------------------------------------------------"
        print ""
        quit()
        
    if setup.station==None or setup.start==None or setup.end==None:
        print '\nERROR: station or start or end dates not specified...\n'
        quit()
    
    t,x,y,z = magfield(setup.start,setup.end,rep=setup.path)
    # Discard selected data
    t = t[setup.rate*setup.discard:]
    x = x[setup.rate*setup.discard:]
    y = y[setup.rate*setup.discard:]
    z = z[setup.rate*setup.discard:]
    # Create x axis time label
    t0 = datetime.fromtimestamp(t[0]).strftime('%Y-%m-%d %H:%M:%S')
    t1 = datetime.fromtimestamp(t[-1]).strftime('%Y-%m-%d %H:%M:%S')
    label1 = 'Local time from %s to %s [%s]'%(t0,t1,setup.unit)
    # Create filename
    t0 = datetime.fromtimestamp(t[0]).strftime('%y%m%d_%H%M%S')
    t1 = datetime.fromtimestamp(t[-1]).strftime('%y%m%d_%H%M%S')
    label2 = '%s-%s-%s-transform.png'%(setup.station,t0,t1)
    # Decimate magnetic field data to 1 sample/second
    down_factor = [setup.down] if setup.down<13 else \
                  [11,9,4] if setup.down==396 else [11,10,9,4]
    for i in down_factor:
        x = signal.decimate(x,i,zero_phase=True)
        y = signal.decimate(y,i,zero_phase=True)
        z = signal.decimate(z,i,zero_phase=True)
    # Extract time every 3960 sample
    l = len(t)/setup.down
    l = l if l*setup.down==len(t) else l+1
    t = [t[n*setup.down] for n in range(l)]
    if setup.nogps: t = [float(n)*setup.down/setup.rate for n in range(len(x))]
    # Convert every timing points to scale (hr,min,sec) units
    s = 1. if setup.unit=='secs' else 60. if setup.unit=='mins' else 3600.
    t = [(t[i]-t[0])/s for i in range(len(t))]
    # Initialise axis
    fig = figure(figsize=(15,10))
    plt.subplots_adjust(left=0.07,right=0.95,bottom=0.1,top=0.95,hspace=0.2,wspace=0.1)
    # Plot time series
    ax1 = subplot(231)
    ax1.plot(t,x-np.average(x))
    ax1.set_xlim(t[0],t[-1])
    ax1.set_ylabel('Magnetic field [uT]')
    ax1.set_title('X field')
    ax2 = subplot(232,sharex=ax1,sharey=ax1)
    ax2.plot(t,y-np.average(y))
    ax2.set_xlim(t[0],t[-1])
    ax2.set_xlabel(label1)
    ax2.set_title('Y field')
    plt.setp(ax2.get_yticklabels(),visible=False)
    ax3 = subplot(233,sharex=ax1,sharey=ax1)
    ax3.plot(t,z-np.average(z))
    ax3.set_xlim(t[0],t[-1])
    ax3.set_title('Z field')
    plt.setp(ax3.get_yticklabels(),visible=False)
    # Create FFT of data
    N = len(t)
    T = 1.0 / (setup.rate/setup.down)
    f = np.linspace(0.0, 1.0/(2.0*T), N/2)
    i1 = abs(f-setup.fmin).argmin()
    i2 = len(f) if setup.fmax==None else abs(f-setup.fmax).argmin()
    f = f[i1:i2]
    x = 2.0/N * np.abs(fft(x)[:N//2])[i1:i2]
    y = 2.0/N * np.abs(fft(y)[:N//2])[i1:i2]
    z = 2.0/N * np.abs(fft(z)[:N//2])[i1:i2]
    # Plot FFT for x direction
    ax4 = subplot(234)
    ax4.plot(f,x,'k')
    ax4.set_ylabel('|Y(f)|')
    # Plot FFT for y direction
    ax5 = subplot(235,sharex=ax4,sharey=ax4)
    ax5.plot(f,y,'k')
    ax5.set_xlabel('Frequency [Hz]')
    plt.setp(ax5.get_yticklabels(),visible=False)
    # Plot FFT for z direction
    ax6 = subplot(236,sharex=ax4,sharey=ax4)
    ax6.plot(f,z,'k')
    ax6.set_xlim(1,f[-1])
    ax6.set_ylim(0,max(z)/setup.scale)
    plt.setp(ax6.get_yticklabels(),visible=False)
    # Save figure
    plt.savefig(label2)
    plt.close(fig)
