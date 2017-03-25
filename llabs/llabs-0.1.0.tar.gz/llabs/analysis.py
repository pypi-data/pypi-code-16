from .settings import *
from .extras   import *
from .plots    import *
from .utils    import *

def analysis():
    
    os.system('mkdir -p ./plots')
    setup.data = np.loadtxt(sys.argv[1],dtype=str,comments='!',ndmin=2)
    col1,dat1 = setup.data[0,1:], np.array(setup.data[1:,1:],dtype=float).T
    col2,dat2 = setup.data[0,0], np.array(setup.data[1:,0],dtype=str)
    setup.data = dict(zip(col1,dat1))
    setup.data[col2] = dat2
    iremove1  = np.where(setup.data['shift']>setup.limshift)[0]
    iremove2  = np.where(setup.data['SNR']<setup.limsnr)[0]
    iremove   = np.append(iremove1,iremove2)
    for key in setup.data.keys():
        setup.data[key] = np.delete(setup.data[key],iremove,axis=0)
    print '|-',len(setup.data['QSO']),'Lyman limit shifts reported.'
    if '--replot' in sys.argv:
        for i in range(len(setup.data['QSO'])):
            setup.filename   = setup.data['QSO'][i]
            setup.fullpath   = setup.home + setup.filename
            setup.spectrum   = re.split(r'[/.]',setup.fullpath)
            setup.qsoname    = setup.spectrum[-2]
            setup.dvshift    = setup.data['shift'][i]
            setup.zalpha     = (setup.data['zmin'][i]+setup.data['zmax'][i])/2
            setup.z          = setup.data['z'][i]
            setup.N          = setup.data['N'][i]
            setup.b          = setup.data['b'][i]
            setup.npix1a     = setup.data['npix1a'][i]
            setup.npix1b     = setup.data['npix1b'][i]
            setup.npix2a     = setup.data['npix2a'][i]
            setup.npix2b     = setup.data['npix2b'][i]
            setup.walldla    = setup.data['walldla'][i]
            setup.wallobs    = setup.data['wallobs'][i]
            setup.wallobs1   = setup.data['wallobs1'][i]
            setup.dlawidth   = setup.data['DLAwidth'][i]
            if math.isnan(setup.dvshift)==True:
                setup.flag = 'llfound'
                readspec()
                wholespec()
            else:
                setup.flag = 'dlafound'
                readspec()
                plotdla()
        quit()
    if '--reval' in sys.argv:
        setup.update()
    getmetallicity()
    llhist()
    if setup.resolution=='high':
        keyfig()
        statplots()
        metalplots()
        multiplots()
        llregions()
    
def getmetallicity():

    setup.metew,setup.metew_err,setup.metfr,setup.metfr_err = [],[],[],[]
    for i in range(len(setup.data['QSO'])):
        idx = None
        if setup.metals is not None:
            met   = [float(setup.metals[k,1]) for k in range(len(setup.metals))]
            cond1 = setup.metals[:,0]==setup.data['QSO'][i]
            cond2 = abs(setup.data['z'][i]-met)<0.02
            pos   = np.where(np.logical_and(cond1,cond2))[0]
            idx   = idx if len(pos)==0 else pos[0]
        metabs,frac = [],[]
        if idx is None:
            for j in range(len(setup.Metallist)):
                metal = setup.Metallist[j]['Metalline']+'_'+str(setup.Metallist[j]['Metalwave']).split('.')[0]
                metabs.append(setup.data['EW_'+metal][i])
                frac.append(setup.data['FR_'+metal][i])
        else:
            for metal in setup.metals[idx,2].split('-'):
                metabs.append(setup.data['EW_'+metal][i])
                frac.append(setup.data['FR_'+metal][i])
        if len(metabs)==0 or np.std(metabs)==0:
            setup.metew.append(0)
            setup.metew_err.append(1e-32) 
        else:
            setup.metew.append(np.mean(metabs))
            setup.metew_err.append(np.std(metabs))
        if len(frac)==0 or np.std(frac)==0:
            setup.metfr.append(0)
            setup.metfr_err.append(1e-32) 
        else:
            setup.metfr.append(np.mean(frac))
            setup.metfr_err.append(np.std(frac))
    
def llhist():

    def gauss(x, a, b, c):
        return a * np.exp(-(x - b)**2.0 / (2 * c**2))
    print '|- histplot.pdf'
    rc('font', size=12, family='sans-serif')
    rc('axes', labelsize=12, linewidth=0.5)
    rc('legend', fontsize=12, handlelength=10)
    rc('xtick', labelsize=12)
    rc('ytick', labelsize=12)
    rc('lines', lw=0.5, mew=0.2)
    rc('grid', linewidth=1)
    fig = figure(figsize=(7,6))
    plt.subplots_adjust(left=0.1, right=0.95, bottom=0.1, top=0.95, hspace=0.15, wspace=0.2)
    xmin = 0
    xmax = 10000
    ax   = plt.subplot(111,xlim=[xmin,xmax])
    data = setup.data['shift']
    idxs = np.where(np.logical_and(data>xmin,data<xmax))[0]
    data = ax.hist(data[idxs],bins=setup.binning,stacked=True,fill=True,alpha=0.4)
    best = np.where(setup.data['SNR']>10)[0]
    ax.hist(setup.data['shift'][best],bins=setup.binning,stacked=True,fill=True,alpha=0.4,color='red')
    x = np.array([0.5 * (data[1][i] + data[1][i+1]) for i in xrange(len(data[1])-1)])
    y = data[0]
    popt, pcov = curve_fit(gauss,x,y,p0=[20,2000,500])
    x = np.arange(xmin,xmax,0.1)
    y = gauss(x, *popt)
    plot(x, y, lw=3, color="r")
    xlabel('Apparent shift in the Lyman limit break (km/s)')
    ylabel('Frequency')
    os.system('mkdir -p plots/')
    savefig('./plots/histplot.pdf')
    clf()

def statplots():

    def plotting(name,x,y,c,xlab,ylab,xmin,xmax,ymin,ymax,xerr=None,yerr=None):
        '''
        Generic function to do all the plots in the statplots module.
        '''
        def func(x,a,b):
            return a + b*x
        #rc('font', size=12, family='sans-serif')
        #rc('axes', labelsize=12, linewidth=0.5)
        #rc('legend', fontsize=12, handlelength=10)
        #rc('xtick', labelsize=12)
        #rc('ytick', labelsize=12)
        #rc('lines', lw=2, mew=0.2)
        #rc('grid', linewidth=1)
        style = ['o' if 'UVES' in setup.data['QSO'][i] else 's' if 'HIRES' in setup.data['QSO'][i] else 'd' for i in range(len(setup.data['QSO']))]
        label = ['UVES' if 'UVES' in setup.data['QSO'][i] else 'HIRES' if 'HIRES' in setup.data['QSO'][i] else 'SDSS' for i in range(len(setup.data['QSO']))]
        fig = figure(figsize=(7,6))
        plt.subplots_adjust(left=0.1, right=0.87, bottom=0.1, top=0.95, hspace=0, wspace=0)
        ax = subplot(111,xlim=[xmin,xmax],ylim=[ymin,ymax])
        for i in range(len(x)):
            xerr1 = None if xerr==None else xerr[i]
            yerr1 = None if yerr==None else yerr[i]
            scatter(x[i],y[i],marker=style[i],c=c[i],s=120,edgecolors='none',zorder=1,cmap=mpl.cm.rainbow,vmin=min(c),vmax=max(c),alpha=0.7)
            errorbar(x[i],y[i],xerr=xerr1,yerr=yerr1,fmt='o',ms=0,c='0.5',zorder=2)
        xfit = np.arange(0,4000,0.001)
        if yerr==None:
            coeffs,matcov = curve_fit(func,x,y)
            yfit = func(xfit,coeffs[0],coeffs[1])
            print '|  |- Unweighted fit: %.6f +/- %.6f'%(coeffs[1],np.sqrt(matcov[1][1]))
            plot(xfit,yfit,color='black',lw=3,ls='dashed')
        else:
            coeffs,matcov = curve_fit(func,x,y,sigma=yerr)
            yfit = func(xfit,coeffs[0],coeffs[1])
            print '|  |- Weighted fit: %.6f +/- %.6f'%(coeffs[1],np.sqrt(matcov[1][1]))
            plot(xfit,yfit,color='black',lw=3,ls='dashed')
        ylabel(ylab,fontsize=12)
        xlabel(xlab,fontsize=12)
        ax1  = fig.add_axes([0.87,0.1,0.04,0.85])
        cmap = mpl.cm.rainbow
        norm = mpl.colors.Normalize(vmin=min(c),vmax=max(c))
        cb1  = mpl.colorbar.ColorbarBase(ax1,cmap=cmap,norm=norm)
        cb1.set_label('Signal-to-Noise ratio',fontsize=12)
        savefig('./plots/'+name)
        clf()        

    os.system('mkdir -p plots/')
    xmin,xmax = 2,5
    ymin,ymax = 0,3000
    name = 'shift-zabs.pdf'
    xlab = 'Absorption redshift'
    ylab = 'Lyman limit shift (km/s)'
    unit = ''
    print '|-',name
    plotting(name,setup.data['z'],setup.data['shift'],setup.data['SNR'],xlab,ylab,xmin,xmax,ymin,ymax)
    if setup.data['QSO'][0].split('/')[0].lower()!='sdss':
        xmin,xmax = 0,2500
        ymin,ymax = 0,500
        name = 'dlawidth-shift.pdf'
        xlab = 'Lyman limit shift (km/s)'
        ylab = 'DLA velocity dispersion (km/s)'
        print '|-',name
        plotting(name,setup.data['shift'],setup.data['DLAwidth'],setup.data['SNR'],xlab,ylab,xmin,xmax,ymin,ymax)
        xmin,xmax = 0,600
        ymin,ymax = 0,1
        name = 'metew-dlawidth.pdf'
        xlab = 'DLA velocity dispersion (km/s)'
        ylab = r'Average equivalent width ($\mathrm{\AA}$)'
        print '|-',name
        plotting(name,setup.data['DLAwidth'],setup.metew,setup.data['SNR'],xlab,ylab,xmin,xmax,ymin,ymax,yerr=setup.metew_err)
        xmin,xmax = 0,3000
        ymin,ymax = 0,1.1*max(setup.metew)
        name = 'metew-shift.pdf'
        xlab = 'Lyman limit shift (km/s)'
        ylab = 'Average equivalent width ($\mathrm{\AA}$)'
        print '|-',name
        plotting(name,setup.data['shift'],setup.metew,setup.data['SNR'],xlab,ylab,xmin,xmax,ymin,ymax,yerr=setup.metew_err)
        xmin,xmax = 0,600
        ymin,ymax = 0,1
        name = 'metfr-dlawidth.pdf'
        xlab = 'DLA velocity dispersion (km/s)'
        ylab = 'Pixel fraction of metal absorption'
        print '|-',name
        plotting(name,setup.data['DLAwidth'],setup.metfr,setup.data['SNR'],xlab,ylab,xmin,xmax,ymin,ymax,yerr=setup.metfr_err)
        xmin,xmax = 0,3000
        ymin,ymax = 0,1
        name = 'metfr-shift.pdf'
        xlab = 'Lyman limit shift (km/s)'
        ylab = 'Pixel fraction of metal absorption'
        print '|-',name
        plotting(name,setup.data['shift'],setup.metfr,setup.data['SNR'],xlab,ylab,xmin,xmax,ymin,ymax,yerr=setup.metfr_err)
        xmin,xmax = 0,1
        ymin,ymax = 0,1
        name = 'metew-metfr.pdf'
        xlab = 'Pixel fraction of metal absorption'
        ylab = 'Average equivalent width ($\mathrm{\AA}$)'
        print '|-',name
        plotting(name,setup.metfr,setup.metew,setup.data['SNR'],xlab,ylab,xmin,xmax,ymin,ymax)

def metalplots():

    os.system('mkdir -p plots/')
    print '|- metalplots.pdf'
    rc('font', size=12, family='sans-serif')
    rc('axes', labelsize=12, linewidth=0.5)
    rc('legend', fontsize=12, handlelength=10)
    rc('xtick', labelsize=12)
    rc('ytick', labelsize=12)
    rc('lines', lw=0.5, mew=0.2)
    rc('grid', linewidth=1)
    fig = figure(figsize=(12,10))
    plt.subplots_adjust(left=0.05, right=0.87, bottom=0.05, top=0.95, hspace=0, wspace=0)
    for j in range (1,len(setup.Metallist)):
        metal = setup.Metallist[j]['Metalline']+'_'+str(setup.Metallist[j]['Metalwave']).split('.')[0]
        if metal!='ZnII_2062':
            ax = subplot(6,5,j,xlim=[0,1],ylim=[0,setup.limshift])
            for i in range (len(setup.data['QSO'])):
                if setup.metals is not None:
                    met   = [float(setup.metals[k,1]) for k in range(len(setup.metals))]
                    cond1 = setup.metals[:,0]==setup.data['QSO'][i]
                    cond2 = abs(setup.data['z'][i]-met)<0.02
                    pos   = np.where(np.logical_and(cond1,cond2))[0]
                    idx   = None if len(pos)==0 else pos[0]
                if setup.metals is None or (idx is not None and metal in setup.metals[idx,2].split('-')):
                    shift = setup.data['shift'][i]
                    ewmet = setup.data['EW_'+metal][i]
                    color = setup.data['SNR'][i]
                    scatter(ewmet,shift,c=color,s=20,edgecolors='none',zorder=2,cmap=mpl.cm.rainbow,vmin=min(setup.data['SNR']),vmax=max(setup.data['SNR']))
            y_formatter = matplotlib.ticker.ScalarFormatter(useOffset=False)
            ax.yaxis.set_major_formatter(y_formatter)
            plt.xticks(fontsize=8)
            plt.yticks(fontsize=8)
            if j<5*5: plt.setp(ax.get_xticklabels(), visible=False)
            if (j-1)%5!=0: plt.setp(ax.get_yticklabels(), visible=False)
            t1 = ax.text(0.5,0.9*setup.limshift,metal,color='grey',ha='center',fontsize=10)
            t1.set_bbox(dict(color='white', alpha=0.7, edgecolor=None))
    ax   = fig.add_axes([0.9,0.05,0.04,0.9])
    cmap = mpl.cm.rainbow
    norm = mpl.colors.Normalize(vmin=min(setup.data['SNR']),vmax=max(setup.data['SNR']))
    cb1  = mpl.colorbar.ColorbarBase(ax,cmap=cmap,norm=norm)
    cb1.set_label('Estimated SNR')
    savefig('./plots/metalplots.pdf')
    clf()

def multiplots():

    print '|- multiplots.pdf'
    os.system('mkdir -p ./plots')
    rc('font', size=8, family='sans-serif')
    rc('axes', labelsize=8, linewidth=0.5)
    rc('legend', fontsize=8, handlelength=10)
    rc('xtick', labelsize=8)
    rc('ytick', labelsize=8)
    rc('lines', lw=0.5, mew=0.2)
    rc('grid', linewidth=1)
    fig = figure(figsize=(12,10))
    plt.subplots_adjust(left=0.07, right=0.87, bottom=0.1, top=0.95, hspace=0.2, wspace=0.25)
    totavg = []
    for i in range (len(setup.data['QSO'])):
        totavg.append(float(setup.data['SNR'][i]))
    ax = subplot(331)
    for i in range (len(setup.data['QSO'])):
        llshift = float(setup.data['shift'][i])
        coldens = float(setup.data['N'][i])
        scatter(coldens,llshift,c=totavg[i],s=30,edgecolors='none',zorder=0,cmap=mpl.cm.rainbow,vmin=min(totavg),vmax=max(totavg))
    xlabel('HI column density (log)')
    ylabel('Lyman limit shift (km/s)')
    ax = subplot(332)
    x,y,yerr = [],[],[]
    for i in range (len(setup.data['QSO'])):
        EWmet = []
        llshift = float(setup.data['shift'][i])
        for j in range (1,len(setup.Metallist)):
            prev = setup.Metallist[j-1]['Metalline']+'_'+str(setup.Metallist[j-1]['Metalwave']).split('.')[0]
            name = setup.Metallist[j]['Metalline']+'_'+str(setup.Metallist[j]['Metalwave']).split('.')[0]
            cond2 = setup.data['EW_'+name][i] not in ['0.00','1.00']
            cond3 = setup.Metallist[j-1]['Metalline']!=setup.Metallist[j]['Metalline']
            cond4 = setup.Metallist[j-1]['Metalline']==setup.Metallist[j]['Metalline'] and float(setup.data['EW_'+name][i])<float(setup.data['EW_'+prev][i])
            if cond2 and (cond3 or cond4):
                EWmet.append(float(setup.data['EW_'+name][i]))
        if EWmet!=[] and float(setup.data['SNR'][i])>setup.limsnr:
            EWmed = np.mean(EWmet)
            errorbar(EWmed,llshift,xerr=np.std(EWmet),fmt='o',ms=0,c='0.7',zorder=1)
            scatter(EWmed,llshift,c=totavg[i],s=30,edgecolors='none',zorder=2,cmap=mpl.cm.rainbow,vmin=min(totavg),vmax=max(totavg))
            x.append(np.mean(EWmet))
            y.append(llshift)
            yerr.append(np.std(EWmet))
    #fitlinear(x,y,min(x),max(x),min(y),max(y),min(x),max(x),err=yerr)
    xlabel('Average Metal Absorption Equivalent Width')
    ylabel('Lyman limit shift (km/s)')
    ax = subplot(333)
    for i in range (len(setup.data['QSO'])):
        EWmet = []
        coldens = float(setup.data['N'][i])
        for j in range (1,len(setup.Metallist)):
            name = setup.Metallist[j]['Metalline']+'_'+str(setup.Metallist[j]['Metalwave']).split('.')[0]
            if setup.data['EW_'+name][i] not in ['0.00','1.00']:
                EWmet.append(float(setup.data['EW_'+name][i]))
        if EWmet!=[]:
            EWmet = np.mean(EWmet)
            scatter(coldens,EWmet,c=totavg[i],s=30,edgecolors='none',zorder=1,cmap=mpl.cm.rainbow,vmin=min(totavg),vmax=max(totavg))
    xlabel('HI column density (log)')
    ylabel('Average Metal Absorption Equivalent Width')
    ax = subplot(334)
    num_bins = 50
    llshift = []
    for i in range (len(setup.data['QSO'])):
        llshift.append(float(setup.data['shift'][i]))
    n, bins, patches = plt.hist(llshift, num_bins, facecolor='blue', alpha=0.5)
    xlabel('Lyman limit shift (km/s)')
    ax = subplot(335)
    for i in range (len(setup.data['QSO'])):
        llshift = float(setup.data['shift'][i])
        scatter(llshift,totavg[i],c=totavg[i],s=30,edgecolors='none',zorder=1,cmap=mpl.cm.rainbow,vmin=min(totavg),vmax=max(totavg))
    xlabel(r'Lyman limit shift (km/s)')
    ylabel('Estimated SNR')
    #ax = subplot(336)
    #for i in range (len(setup.data['QSO'])):
    #    hilimit = float(setup.data['HI_Limit'][i])
    #    llshift = float(setup.data['shift'][i])
    #    scatter(llshift,hilimit,c=totavg[i],s=30,edgecolors='none',zorder=1,cmap=mpl.cm.rainbow,vmin=min(totavg),vmax=max(totavg))
    #xlabel('Lyman limit shift (km/s)')
    #ylabel('Number of transition available')
    ax = subplot(337)
    for i in range (len(setup.data['QSO'])):
        if setup.data['QSO'][i] in setup.pub[:,0]:
            k = np.where(setup.pub[:,0]==setup.data['QSO'][i])[0][0]
            llshift = float(setup.data['shift'][i])
            errorbar(float(setup.pub[k,1]),llshift,xerr=float(setup.pub[k,2]),fmt='o',ms=0,c='0.5')
            scatter(float(setup.pub[k,1]),llshift,c=totavg[i],s=30,edgecolors='none',zorder=1,cmap=mpl.cm.rainbow,vmin=min(totavg),vmax=max(totavg))
    xlabel('Published D/H values (log)')
    ylabel('Lyman limit shift (km/s)')
    #ax = subplot(338)
    #for i in range (len(setup.data['QSO'])):
    #    scatter(setup.data['Shift_fit'][i],setup.data['Shift_guess'][i],c=totavg[i],s=30,edgecolors='none',zorder=0,cmap=mpl.cm.rainbow,vmin=min(totavg),vmax=max(totavg))
    #xlabel('Lyman limit shift from fit (km/s)')
    #ylabel('Lyman limit shift from first guess (km/s)')
    ax = subplot(339)
    for i in range (len(setup.data['QSO'])):
        EWmet,FRmet = [],[]
        for j in range (1,len(setup.Metallist)):
            name = setup.Metallist[j]['Metalline']+'_'+str(setup.Metallist[j]['Metalwave']).split('.')[0]
            if setup.data['EW_'+name][i] not in ['0.00','1.00']:
                EWmet.append(float(setup.data['EW_'+name][i]))
            if setup.data['FR_'+name][i] not in ['0.00','1.00']:
                FRmet.append(float(setup.data['FR_'+name][i]))
        if EWmet!=[]:
            EWmet = np.mean(EWmet)
            FRmet = np.mean(FRmet)
            scatter(FRmet,EWmet,c=totavg[i],s=30,edgecolors='none',zorder=0,cmap=mpl.cm.rainbow,vmin=min(totavg),vmax=max(totavg))
    xlabel('Metal fraction')
    ylabel('Metal equivalent width')
    ax  = fig.add_axes([0.9,0.1,0.04,0.85])
    cmap = mpl.cm.rainbow
    norm = mpl.colors.Normalize(vmin=min(totavg),vmax=max(totavg))
    cb1  = mpl.colorbar.ColorbarBase(ax,cmap=cmap,norm=norm)
    cb1.set_label('Estimated SNR')
    savefig('./plots/multiplots.pdf')
    clf()

def llregions():
    
    print '|- Create plots of all the Lyman limit regions...'
    os.system('mkdir -p ./plots')
    pdf_pages = PdfPages('./plots/llregions.pdf')
    i=p=0
    while (i<len(setup.data['QSO'])):
        f   = 1
        fig = figure(figsize=(8.27, 11.69))
        axis('off')
        subplots_adjust(left=0.05, right=0.95, bottom=0.06, top=0.96, wspace=0, hspace=0)
        while i<len(setup.data['QSO']) and f<=10:
            p = p + 1
            print '%4.f'%(p)+'/'+str(len(setup.data['QSO'])),':',setup.data['QSO'][i]
            setup.filename   = setup.data['QSO'][i]
            setup.fullpath   = setup.home+setup.filename
            setup.spectrum   = re.split(r'[/.]',setup.fullpath)
            setup.qsoname    = setup.spectrum[-2]
            readspec()
            dv_neg  = -2500
            dv_pos  = 12000
            wastart = float(setup.data['walldla'][i])*(2*setup.c+dv_neg)/(2*setup.c-dv_neg)
            waend   = float(setup.data['walldla'][i])*(2*setup.c+dv_pos)/(2*setup.c-dv_pos)
            istart  = abs(setup.wa - wastart).argmin()
            iend    = abs(setup.wa - waend).argmin()
            ymax    = 1 if istart==iend else sorted(setup.fl[istart:iend])[int(0.99*(iend-istart))]
            wafit   = np.arange(wastart,waend,0.05)
            ax = fig.add_subplot(10,1,f,xlim=[wastart,waend],ylim=[-ymax,ymax])
            ax.xaxis.tick_top()
            ax.xaxis.set_major_locator(NullLocator())
            ax.yaxis.set_major_locator(plt.FixedLocator([0]))
            npix1a = float(setup.data['npix1a'][i])
            npix1b = float(setup.data['npix1b'][i])
            npix2a = float(setup.data['npix2a'][i])
            npix2b = float(setup.data['npix2b'][i])
            ilim = abs(setup.wa-float(setup.data['wallobs1'][i])).argmin()
            ax.axvline(x=setup.data['wallobs1'][i],color='green',lw=2,alpha=0.7)
            ax.axvspan(setup.wa[ilim-npix1b],setup.wa[ilim+npix1a],color='lime',lw=1,alpha=0.2,zorder=1)
            ilim = abs(setup.wa-float(setup.data['wallobs'][i])).argmin()
            ax.axvline(x=setup.data['wallobs'][i],color='blue',lw=2,alpha=0.7)
            ax.axvspan(setup.wa[ilim-npix2b],setup.wa[ilim+npix2a],color='blue',lw=1,alpha=0.2,zorder=1)
            ax.plot(setup.wa[istart:iend],setup.fl[istart:iend],'black',lw=0.2)
            ax.plot(setup.wa[istart:iend],setup.er[istart:iend],'cyan',lw=0.2)
            ax.axhline(y=0,ls='dotted',color='red',lw=0.2)
            ax.axvline(x=float(setup.data['walldla'][i]),color='red',lw=2,alpha=0.5)
            ax.axvline(x=float(setup.data['wallobs'][i]),color='red',lw=2,alpha=0.5)
            t1 = text(float(setup.data['walldla'][i]),0,setup.data['walldla'][i],size=8,rotation=90,color='red',ha='center',va='center')
            t2 = text(float(setup.data['wallobs'][i]),0,setup.data['wallobs'][i],size=8,rotation=90,color='red',ha='center',va='center')
            t3 = text(wastart+0.99*(waend-wastart),-0.50*ymax,setup.data['QSO'][i],size=8,color='blue',ha='right',va='center')
            t4 = text(wastart+0.99*(waend-wastart),-0.75*ymax,'%i km/s'%setup.data['shift'][i],size=6,color='blue',ha='right',va='center')
            for t in [t1,t2,t3,t4]:
                t.set_bbox(dict(color='white', alpha=0.8, edgecolor=None))
            f = f + 1
            i = i + 1
        pdf_pages.savefig(fig)
        close(fig)
    pdf_pages.close()
