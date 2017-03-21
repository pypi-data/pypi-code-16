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
        print "required arguments"
        print ""
        print "   --start          Starting date to retrieve data from."
        print "   --end            Ending date to retrieve data from."
        print ""
        print "optional arguments:"
        print ""
        print "   --delay          Time delay in hour from UTC and Local times."
        print "   --sample         Specify the data to be field sample, not regular."
        print "   --rescale        Recalculate time edges for the plot from data"
        print ""
        print "-------------------------------------------------------------------------"
        print ""
        quit()

    # Get start and ending timestamps
    start,tmin,end,tmax = time_edge(setup.start,setup.end)
    # Get NURI data
    path  = '/Users/vincent/ASTRO/data/DAQ_NURI/'
    nuri  = magfield(setup.start,setup.end,rep=path)
    # Get GNOME data
    path  = '/Users/vincent/ASTRO/data/DAQ_GNOME/'
    gnome = gnomedata('Berkeley02',setup.start,setup.end,rep=path)
    # Check cross time
    if setup.rescale:
        tmin = max(nuri[0,0],gnome[0,0])
        tmax = min(nuri[-1,0],gnome[-1,0])
    data1 = []
    flag  = 0
    for i in range(1,len(nuri[:,0])-1):
        if tmin<nuri[i,0] and flag==0 and nuri[i-1,1]<14<=nuri[i,1]:
            data1.append(nuri[i,0])
            flag = 1
        if tmin<nuri[i,0] and flag==1 and nuri[i+1,1]<14<=nuri[i,1]:
            flag = 0
    data2 = []
    for i in range(1,len(gnome)-1):
        if tmin<gnome[i,0] and flag==0 and gnome[i-1,1]<0.9<=gnome[i,1]:
            data2.append(gnome[i,0])
            flag = 1
        if tmin<gnome[i,0] and flag==1 and gnome[i+1,1]<0.9<=gnome[i,1]:
            flag = 0
    data = diff1 = diff2 = np.empty((0,2))
    for i in range(1,min(len(data1),len(data2))):
        diff1 = np.vstack((diff1,[data1[i]-tmin,data1[i]-data1[i-1]]))
        diff2 = np.vstack((diff2,[data2[i]-tmin,data2[i]-data2[i-1]]))
        data  = np.vstack((data,[data1[i]-tmin,data1[i]-data2[i]]))
        print '%.11f | %.11f | %.11f | %.11f'%(data1[i]-tmin,data1[i]-data1[i-1],data2[i]-data2[i-1],data1[i]-data2[i])
    # Create x axis time label
    tbeg = datetime.fromtimestamp(tmin)
    tend = datetime.fromtimestamp(tmax)
    label1 = 'Local time from %s to %s [secs]'%(tbeg.strftime('%Y-%m-%d %H:%M:%S.%f'),tend.strftime('%Y-%m-%d %H:%M:%S.%f'))
    label2 = 'timing_test-%s-%s.png'%(tbeg.strftime('%y%m%d_%H%M%S.%f'),tend.strftime('%y%m%d_%H%M%S.%f'))
    # Initialise axis
    fig = figure(figsize=(15,15))
    plt.subplots_adjust(left=0.08,right=0.95,bottom=0.05,top=0.97,hspace=0.1,wspace=0)
    # Plot time series from NURI DAQ
    ax1 = subplot(511)
    ax1.plot(nuri[:,0]-tmin,nuri[:,1])
    ax1.set_ylabel('NURI Magnetic Field [uT]')
    plt.setp(ax1.get_xticklabels(),visible=False)
    # Plot pulse difference
    ax2 = subplot(512,sharex=ax1)
    ax2.scatter(diff1[:,0],diff1[:,1],lw=0,s=20,c='#4e73ae')
    ax2.set_ylabel('NURI Pulse separation [secs]')
    plt.setp(ax2.get_xticklabels(),visible=False)
    # Plot time series from GNOME DAQ
    ax3 = subplot(513,sharex=ax1)
    ax3.plot(gnome[:,0]-tmin,gnome[:,1])
    ax3.set_ylabel('GNOME Magnetic Field [uT]')
    plt.setp(ax3.get_xticklabels(),visible=False)
    # Plot pulse difference
    ax4 = subplot(514,sharex=ax1)
    ax4.scatter(diff2[:,0],diff2[:,1],lw=0,s=20,c='#4e73ae')
    ax4.set_ylabel('GNOME Pulse separation [secs]')
    plt.setp(ax4.get_xticklabels(),visible=False)
    # Plot pulse delay
    ax5 = subplot(515,sharex=ax1)
    ax5.scatter(data[:,0],data[:,1],lw=0,s=20,c='#4e73ae')
    ax5.set_xlim([0,tmax-tmin])
    ax5.set_ylabel('Pulse delay [secs]')
    ax5.set_xlabel(label1)
    # Save figure
    plt.savefig(label2)
    plt.close()
