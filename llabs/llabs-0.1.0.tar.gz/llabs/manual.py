from .settings import *

def manual_scan():

    print '|- Start manual scanning...'
    print '|- Looking for Lyman limit...'
    setup.fig = figure(figsize=(12,8))
    setup.llflag,setup.metlist = 0,''
    subplots_adjust(left=0.05, right=0.95, bottom=0.05, top=0.95, hspace=0, wspace=0.1)
    llsearch()
    setup.fig.canvas.mpl_connect('key_press_event', press)
    show()
    if setup.flag==None:
        print '|  |- No suitable Lyman limit found.'
    if setup.flag=='llfound':
        print '|  |- No suitable DLA candidate found.'                    
    if setup.flag=='dlafound':
        print '|  |- DLA candidate fixed at z=%.5f'%setup.zalpha
        idx,metals = None,np.empty((0,3))
        if os.path.exists('./metals.dat')==True:
            metals = np.loadtxt('metals.dat',dtype=str,ndmin=2)
            for i in range(len(metals)):
                if metals[i,0]==setup.filename and abs(float(metals[i,1])-setup.zalpha)<0.02:
                    idx = i
        metals = np.delete(metals,[idx],0) if idx!=None else metals
        metals = np.vstack((metals,[setup.filename,'%.4f'%setup.zalpha,setup.metlist[:-1]]))
        metals = metals[metals[:,0].argsort()]
        outfile = open('metals.dat','w')
        for i in range(len(metals)):
            outfile.write('{0:<40}{1:<10}{2:<10}\n'.format(metals[i,0],metals[i,1],metals[i,2]))
        outfile.close()


def press(event):

    if event.xdata!=None:
        spidx(event)
        if event.key=='?':
            print '|- Show commands for manual detection:'
            print '|  ? - list of commands'
            print '|  c - confirm the position of Lyman limit'
            print '|  l - select left edge of the fitting region'
            print '|  q - leave the program'
            print '|  r - select right edge of the fitting region'
            print '|  s - select the position of the Lyman limit'
            print '|  t - select metal transition'
            print '|  z - center the subplots to a given absorption redshift'
        if event.key=='c' and setup.zlimit!=None:
            setup.llflag = 1
            setup.flag = 'llfound'
            print '|  |- Lyman Limit confirmed.'
            print '|- Looking for DLA candidate...'
            plottrans()
            setup.fig.canvas.draw()
        if event.key=='l':
            selreg(event,'left')
            plottrans()
            setup.fig.canvas.draw()
        if event.key=='q':
            close()
        if event.key=='r':
            selreg(event,'right')
            plottrans()
            setup.fig.canvas.draw()
        if event.key=='s' and setup.llflag==0:
            selreg(event,'limit')
            setup.fig.canvas.draw()
        if event.key=='t':
            selreg(event,'transition')
            setup.fig.canvas.draw()

def llsearch():

    ax   = subplot(111)
    ax.plot(setup.wa,setup.fl,lw=0.8,alpha=0.8,color='black')
    ax.plot(setup.wa,setup.er,lw=0.8,alpha=0.8,color='cyan')
    ax.set_ylim(0,1)
    setup.ax = ax

def plottrans():

    clf()
    setup.axlist = []
    for idx in range(len(setup.HIlist)):
        wacent  = float(setup.HIlist[idx]['wave'])*(setup.zlimit+1)
        v       = setup.c*((setup.wa-wacent)/wacent)
        istart  = abs(v-(-2000)).argmin()
        iend    = abs(v-(+3000)).argmin()
        ymax    = 1 if istart==iend else sorted(setup.fl[istart:iend])[int(0.95*(iend-istart))]
        ax      = subplot(31,2,1+2*idx) if idx==0 else subplot(31,2,1+2*idx,sharex=ax)
        ax.set_xlim(-5000,0)
        ax.set_ylim(0,ymax)
        ax.yaxis.set_major_locator(NullLocator())
        if idx<len(setup.HIlist)-1:
            ax.xaxis.set_major_locator(MultipleLocator(500))
        else:
            ax.xaxis.set_major_locator(NullLocator())
        ax.plot(v,setup.fl,lw=0.8,alpha=0.8,color='black')
        ax.plot(v,setup.er,lw=0.8,alpha=0.8,color='cyan')
        ax.axvline(x=0,lw=3,color='red')
        ax.axvline(x=setup.dvmin,lw=2,color='green')
        ax.axvline(x=setup.dvmax,lw=2,color='green')
        ax.axvspan(setup.dvmin,setup.dvmax,facecolor='lime',alpha=0.5,ec='none')
        metal = 'HI_'+str(setup.HIlist[idx]['wave']).split('.')[0]
        ylabel(metal,rotation='horizontal',ha='right')
        setup.axlist.append(ax)
    for idx in range(len(setup.Metallist)):
        wacent  = float(setup.Metallist[idx]['Metalwave'])*(setup.zlimit+1)
        v       = setup.c*((setup.wa-wacent)/wacent)
        istart  = abs(v-(-2000)).argmin()
        iend    = abs(v-(+3000)).argmin()
        ymax    = 1 if istart==iend else sorted(setup.fl[istart:iend])[int(0.95*(iend-istart))]
        ax      = subplot(31,2,2+2*idx) if idx==0 else subplot(31,2,2+2*idx,sharex=ax)
        ax.set_xlim(-5000,0)
        ax.set_ylim(0,ymax)
        ax.yaxis.set_major_locator(NullLocator())
        if idx<len(setup.HIlist)-1:
            ax.xaxis.set_major_locator(MultipleLocator(500)) 
        else:
            ax.xaxis.set_major_locator(NullLocator())
        ax.plot(v,setup.fl,lw=0.8,alpha=0.8,color='black')
        ax.plot(v,setup.er,lw=0.8,alpha=0.8,color='cyan')
        ax.axvline(x=0,lw=3,color='red')
        ax.axvline(x=setup.dvmin,lw=2,color='green')
        ax.axvline(x=setup.dvmax,lw=2,color='green')
        ax.axvspan(setup.dvmin,setup.dvmax,facecolor='lime',alpha=0.5,ec='none')
        metal = setup.Metallist[idx]['Metalline']+'_'+str(setup.Metallist[idx]['Metalwave']).split('.')[0]
        ylabel(metal,rotation='horizontal',ha='right')
        setup.axlist.append(ax)
    setup.fig.suptitle(sys.argv[1],fontsize=12)

def selreg(event,action):

    if action=='limit':
        setup.wallobs = event.xdata
        setup.zlimit  = (setup.wallobs/setup.HIlist[-1]['wave'])-1.
        setup.zmin    = setup.zmax = setup.zlimit
        setup.dvmin   = setup.dvmax = 0
        setup.nleftHI = setup.nrightHI = 0
        xmin   = setup.wallobs - 15
        xmax   = setup.wallobs + 15
        istart = abs(setup.wa-xmin).argmin()
        iend   = abs(setup.wa-xmax).argmin()
        ymax   = max(setup.fl[istart:iend])
        ax     = setup.ax
        ax.clear()
        ax.plot(setup.wa,setup.fl,lw=0.8,alpha=0.8,color='black')
        ax.plot(setup.wa,setup.er,lw=0.8,alpha=0.8,color='cyan')
        ax.set_xlim(setup.wallobs-10,setup.wallobs+10)
        ax.set_ylim(-0.1,ymax)
        ax.axvline(x=setup.wallobs,color='red',lw=3)
        print '|  |- Lyman Limit selected at %.2f'%setup.wallobs,'i.e. zll = %.5f'%setup.zlimit
        setup.ax = ax
    if action=='left':
        setup.flag     = 'dlafound'
        setup.dvmin    = event.xdata
        setup.zmin     = setup.zlimit * (2*setup.c+setup.dvmin) / (2*setup.c-setup.dvmin) + 2*setup.dvmin / (2*setup.c-setup.dvmin)
        setup.dlawidth = abs(setup.dvmax - setup.dvmin)
        setup.nleftHI  = setup.axisNr if setup.axisNr<31 else setup.axisNr-31
        setup.lastHI   = max([setup.nleftHI,setup.nrightHI])
        setup.zalpha   = (setup.zmin+setup.zmax)/2
        setup.waalpha  = setup.HIlist[0]['wave']*(setup.zalpha+1)
        setup.walldla  = (setup.zalpha+1.)*setup.HIlist[-1]['wave']
        setup.dvshift  = 2*(setup.wallobs-setup.walldla)/(setup.wallobs+setup.walldla)*setup.c        
        print '|  |- zmin set to %.5f for a DLA redshift of %.5f with dv=%.0fkm/s'%(setup.zmin,setup.zalpha,setup.dlawidth)
    if action=='right':
        setup.flag     = 'dlafound'
        setup.dvmax    = event.xdata
        setup.zmax     = setup.zlimit * (2*setup.c+setup.dvmax) / (2*setup.c-setup.dvmax) + 2*setup.dvmax / (2*setup.c-setup.dvmax)
        setup.dlawidth = setup.dvmax - setup.dvmin
        setup.nrightHI = setup.axisNr if setup.axisNr<31 else setup.axisNr-31
        setup.lastHI   = max([setup.nleftHI,setup.nrightHI])
        setup.zalpha   = (setup.zmin+setup.zmax)/2
        setup.waalpha  = setup.HIlist[0]['wave']*(setup.zalpha+1)
        setup.walldla  = (setup.zalpha+1.)*setup.HIlist[-1]['wave']
        setup.dvshift  = 2*(setup.wallobs-setup.walldla)/(setup.wallobs+setup.walldla)*setup.c
        print '|  |- zmax set to %.5f for a DLA redshift of %.5f with dv=%.0fkm/s'%(setup.zmax,setup.zalpha,setup.dlawidth)
    if action=='transition':
        if setup.axisNr>30:
            ax = setup.axlist[setup.axisNr]
            metal = setup.Metallist[setup.axisNr-31]['Metalline']+'_'+str(setup.Metallist[setup.axisNr-31]['Metalwave']).split('.')[0]
            if metal not in setup.metlist:
                ax.yaxis.label.set_color('magenta')
                setup.metlist += metal+'-'
            else:
                ax.yaxis.label.set_color('black')
                setup.metlist.replace(metal+'-','')
    
def spidx(event):

    i = 0
    setup.axisNr = None
    for axis in setup.fig.axes:
        if axis == event.inaxes:
            setup.axisNr = i
            break
        i += 1
