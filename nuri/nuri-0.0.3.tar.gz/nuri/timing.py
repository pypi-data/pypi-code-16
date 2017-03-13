from .settings import *
from .extract  import *

def timing():
    
    if '--help' in sys.argv or '-h' in sys.argv:
        
        print ""
        print "-------------------------------------------------------------------------"
        print ""
        print "description:"
        print ""
        print "  In this operation we will do some analysis test."
        print ""
        print "optional arguments:"
        print ""
        print "   --delay         Time delay in hour from UTC and Local times."
        print "   --sample        Specify the data to be field sample, not regular."
        print ""
        print "-------------------------------------------------------------------------"
        print ""
        quit()

    # Get NURI data
    path = '/Volumes/NURI-GNOME/NURIDrive/samples/timing_test/DAQ_NURI/'
    path = '/Users/vincent/ASTRO/data/DAQ_NURI/'
    t1,x1,y1,z1 = magfield('2017-3-1-14-1','2017-3-1-14-2',rep=path)
    t1 = t1 - 8.*3600.
    # Decimate magnetic field data to 990 sample/second
    down_factor = 1
    x1 = signal.decimate(x1,down_factor,zero_phase=True)
    # Extract time every 4 sample
    l = len(t1)/setup.down
    #l = l if l*setup.down==len(t1) else l+1
    t1 = np.array([t1[n*down_factor] for n in range(l)])
    # Get GNOME data
    path = '/Volumes/NURI-GNOME/NURIDrive/samples/timing_test/DAQ_GNOME/'
    path = '/Users/vincent/ASTRO/data/DAQ_GNOME/'
    t2,x2 = gnomedata('Berkeley02','2017-3-1-14-1','2017-3-1-14-2',rep=path)
    # Select start and end time to display
    tstamp1 = (datetime(2017,3,1,22,1,0)-datetime(1970,1,1)).total_seconds()
    tstamp2 = (datetime(2017,3,1,22,1,1)-datetime(1970,1,1)).total_seconds()
    # Create x axis time label
    tbeg = datetime.fromtimestamp(tstamp1).strftime('%Y-%m-%d %H:%M:%S')
    tend = datetime.fromtimestamp(tstamp2).strftime('%Y-%m-%d %H:%M:%S')
    label1 = 'Local time from %s to %s [secs]'%(tbeg,tend)
    # Initialise axis
    fig = figure(figsize=(15,10))
    plt.subplots_adjust(left=0.1,right=0.95,bottom=0.1,top=0.95,hspace=0.05,wspace=0)
    # Plot time series from NURI DAQ
    ax1 = subplot(211)
    ax1.plot(t1-tstamp1,x1)
    ax1.set_ylabel('NURI Magnetic Field [uT]')
    plt.setp(ax1.get_xticklabels(),visible=False)
    # Plot time series from GNOME DAQ
    ax2 = subplot(212,sharex=ax1)
    ax2.plot(t2-tstamp1,x2)
    ax2.set_xlim([0,tstamp2-tstamp1])
    ax2.set_ylabel('GNOME Magnetic Field [uT]')
    ax2.set_xlabel(label1)
    # Save figure
    plt.savefig('timing_test.png')
    
