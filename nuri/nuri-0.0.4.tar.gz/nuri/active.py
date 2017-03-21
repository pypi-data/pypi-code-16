from .settings import *
from .extract  import *

def active():

    if '--help' in sys.argv or '-h' in sys.argv:

        print ""
        print "-------------------------------------------------------------------------"
        print ""
        print "description:"
        print ""
        print "  This operation will display the active periods for which data are"
        print "  available from every sensors."
        print ""
        print "required argument:"
        print ""
        print "   --date            Year and month to display activity from."
        print "                       The format shoud be YYYY-MM."
        print ""
        print "-------------------------------------------------------------------------"
        print ""
        quit()

    elif setup.date==None:
        print 'ERROR: --date argument is missing...'
        quit()
    os.chdir(setup.home+'/analysis/nuri/activetime/')
    sys.stderr.write('Retrieve information from Google Drive...')
    os.system('skicka ls -r /MagneticFieldData/ > data')
    data = np.loadtxt('data',dtype=str,delimiter='\n')
    print >>sys.stderr,' done!'
        
    sys.stderr.write('Select active hours for each station...')
    dates = np.empty((0,5))
    st1,st2,st3,st4 = [],[],[],[]
    y0    = int(setup.date.split('-')[0])
    m0    = int(setup.date.split('-')[1])
    d0    = datetime(y0,m0,1)
    y1    = y0   if m0<12 else y0+1
    m1    = m0+1 if m0<12 else 1
    d1    = datetime(y1,m1,1)
    dt    = timedelta(hours=1)
    dates = np.arange(d0,d1,dt)
    dstr  = np.array([[int(str(d).split('T')[0].split('-')[0]),
                       int(str(d).split('T')[0].split('-')[1]),
                       int(str(d).split('T')[0].split('-')[2]),
                       int(str(d).split('T')[1].split(':')[0])] for d in dates])
    station1 = np.array([['MagneticFieldData/%i/%i/%i/%i/NURI-station-01/%i-%i-%i_%i-xx.zip'%(d[0],d[1],d[2],d[3],d[0],d[1],d[2],d[3])] for d in dstr])
    station2 = np.array([['MagneticFieldData/%i/%i/%i/%i/NURI-station-02/%i-%i-%i_%i-xx.zip'%(d[0],d[1],d[2],d[3],d[0],d[1],d[2],d[3])] for d in dstr])
    station3 = np.array([['MagneticFieldData/%i/%i/%i/%i/NURI-station-03/%i-%i-%i_%i-xx.zip'%(d[0],d[1],d[2],d[3],d[0],d[1],d[2],d[3])] for d in dstr])
    station4 = np.array([['MagneticFieldData/%i/%i/%i/%i/NURI-station-04/%i-%i-%i_%i-xx.zip'%(d[0],d[1],d[2],d[3],d[0],d[1],d[2],d[3])] for d in dstr])
    st1 = np.array([[1 if filepath in data else 0] for filepath in station1])
    st2 = np.array([[1 if filepath in data else 0] for filepath in station2])
    st3 = np.array([[1 if filepath in data else 0] for filepath in station3])
    st4 = np.array([[1 if filepath in data else 0] for filepath in station4])
    print >>sys.stderr,' done!'
    print 'Save information in ASCII file...'
    beg = d0.strftime("%Y-%m-%d-%H")
    end = d1.strftime("%Y-%m-%d-%H")
    o = open('text/%i-%02i.dat'%(y0,m0),'w')
    for i in range(len(dstr)):
        yr,mt,dy,hr = dstr[i]
        datestring = '%i-%02i-%02i_%02i'%(yr,mt,dy,hr)
        o.write(datestring)
        o.write('  NURI-station-01') if 'MagneticFieldData/%i/%i/%i/%i/NURI-station-01/%i-%i-%i_%i-xx.zip'%(yr,mt,dy,hr,yr,mt,dy,hr) in data else o.write('  -              ')
        o.write('  NURI-station-02') if 'MagneticFieldData/%i/%i/%i/%i/NURI-station-02/%i-%i-%i_%i-xx.zip'%(yr,mt,dy,hr,yr,mt,dy,hr) in data else o.write('  -              ')
        o.write('  NURI-station-03') if 'MagneticFieldData/%i/%i/%i/%i/NURI-station-03/%i-%i-%i_%i-xx.zip'%(yr,mt,dy,hr,yr,mt,dy,hr) in data else o.write('  -              ')
        o.write('  NURI-station-04') if 'MagneticFieldData/%i/%i/%i/%i/NURI-station-04/%i-%i-%i_%i-xx.zip'%(yr,mt,dy,hr,yr,mt,dy,hr) in data else o.write('  -              ')
        o.write('\n')
    o.close()

    dates = [datetime(d[0],d[1],d[2],d[3]) for d in dstr]
    rc('font', size=2, family='serif')
    rc('axes', labelsize=10, linewidth=0.2)
    rc('legend', fontsize=2, handlelength=10)
    rc('xtick', labelsize=7)
    rc('ytick', labelsize=7)
    rc('lines', lw=0.2, mew=0.2)
    rc('grid', linewidth=0.2)
    fig = figure(figsize=(10,6))
    subplots_adjust(left=0.07, right=0.95, bottom=0.1, top=0.96, hspace=0.2, wspace=0)
    print 'Plot active time for station 1...'
    ax1 = fig.add_subplot(411,xlim=[d0,d1],ylim=[0,1])
    ax1.bar(dates,st1,width=0.01,edgecolor='none',color='green')
    ax1.set_ylabel('Station 1')
    ax1.xaxis.set_major_formatter(md.DateFormatter('%d'))
    ax1.xaxis.set_major_locator(md.DayLocator())
    ax1.xaxis_date()
    plt.yticks([])
    ax1.grid()
    print 'Plot active time for station 2...'
    ax = fig.add_subplot(412,sharex=ax1,sharey=ax1)
    ax.bar(dates,st2,width=0.01,edgecolor='none',color='green')
    ax.set_ylabel('Station 2')
    ax.xaxis_date()
    plt.yticks([])
    ax.grid()
    print 'Plot active time for station 3...'
    ax = fig.add_subplot(413,sharex=ax1,sharey=ax1)
    ax.bar(dates,st3,width=0.01,edgecolor='none',color='green')
    ax.set_ylabel('Station 3')
    ax.xaxis_date()
    plt.yticks([])
    ax.grid()
    print 'Plot active time for station 4...'
    ax = fig.add_subplot(414,sharex=ax1,sharey=ax1)
    ax.bar(dates,st4,width=0.01,edgecolor='none',color='green')
    ax.set_ylabel('Station 4')
    ax.xaxis_date()
    plt.yticks([])
    ax.grid()
    xlabel('\nHourly activity in %s %i (UTC)'%(d0.strftime("%B"),y0))
    plt.savefig('plot/%i-%02i.pdf'%(y0,m0),dpi=80)
