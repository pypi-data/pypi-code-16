from .settings import *
from .voigt    import *

def plotdla():
    '''
    Main plotting routine to plot DLA systems
    '''
    fig = figure(figsize=(8.27,11.69))
    axis('off'),xticks(()),yticks(())
    subplots_adjust(left=0.05, right=0.95, bottom=0.01, top=0.93, hspace=0, wspace=0.05)
    llplot(fig,vmin=-5000,vmax=5000)
    specplot(fig)
    print '|- Plotting Lyman series...',
    start_time = time.time()
    vmin,vmax  = -2000,3000
    for Ntrans in range(0,31,1):
        Nplot=(2*Ntrans-1)+10
        Hplot(fig,Ntrans,Nplot=Nplot,vmin=vmin,vmax=vmax)
        if Ntrans == 30:
            xticks((np.arange(vmin,vmax,400)))
    print round(float(time.time()-start_time),3),'seconds'
    print '|- Plotting metal transitions...',
    start_time = time.time()
    vmin,vmax  = -500,500
    for Ntrans in range(0,31,1):
        Nplot=(2*Ntrans-1)+11
        metalplot(fig,Ntrans,Nplot=Nplot,vmin=vmin,vmax=vmax)
        if Ntrans == 30:
            xticks((np.arange(vmin,vmax,100)))
    print round(float(time.time()-start_time),3),'seconds.'
    os.system('mkdir -p ./candidates/dla/')
    savefig('./candidates/dla/'+setup.qsoname+'.pdf')
    clf()

def llplot(fig,vmin=-10000.,vmax=10000.,Ncol=1,Nplot=1):    
    '''
    Plot the spectrum region where the Lyman-limit is detected

    Parameters
    ----------
    fig   : Figure to be plotted on
    vmin  : Minimum velocity on plot in km/s
    vmax  : Maximum velocity on plot in km/s
    Ncol  : Number of columns to plot over
    Nplot : Plot number
    '''
    llinfo  = '$\lambda_\mathrm{LL,obs}$ = %.2f $\AA$  |  $\mathrm{dv}_\mathrm{LL,shift}$ = %.0f km/s'%(setup.wallobs,setup.dvshift)
    dlainfo = '$z_\mathrm{abs}$ = %.5f  |  $\mathrm{dv}_\mathrm{DLA}$ = %.0f km/s'%(setup.zalpha,setup.dlawidth)
    plt.title(setup.filename+'\n'+llinfo+'\n'+dlainfo+'\n',fontsize=7)
    Nrows   = 23
    dv_neg  = -2500
    dv_pos  = 12000
    wastart = setup.walldla*(2*setup.c+dv_neg)/(2*setup.c-dv_neg)
    waend   = setup.walldla*(2*setup.c+dv_pos)/(2*setup.c-dv_pos)
    istart  = abs(setup.wa - wastart).argmin()
    iend    = abs(setup.wa - waend).argmin()
    ymax    = 1 if istart==iend else sorted(setup.fl[istart:iend])[int(0.99*(iend-istart))]
    wafit   = np.arange(wastart,waend,0.05)
    ax = fig.add_subplot(Nrows,Ncol,Nplot,xlim=[wastart,waend],ylim=[-ymax,ymax])
    ax.xaxis.tick_top()
    ax.xaxis.set_major_locator(plt.FixedLocator([setup.walldla,setup.wallobs]))
    ax.yaxis.set_major_locator(plt.FixedLocator([0]))
    npix1a = setup.npix1a
    npix1b = setup.npix1b
    npix2a = setup.npix2a
    npix2b = setup.npix2b
    ilim = abs(setup.wa-setup.wallobs1).argmin()
    ax.axvline(x=setup.wallobs1,color='green',lw=2,alpha=0.7)
    ax.axvspan(setup.wa[ilim-npix1b],setup.wa[ilim+npix1a],color='lime',lw=1,alpha=0.2,zorder=1)
    ilim = abs(setup.wa-float(setup.wallobs)).argmin()
    ax.axvline(x=setup.wallobs,color='blue',lw=2,alpha=0.7)
    ax.axvspan(setup.wa[ilim-npix2b],setup.wa[ilim+npix2a],color='blue',lw=1,alpha=0.2,zorder=1)
    ax.plot(setup.wa[istart:iend],setup.fl[istart:iend],'black',lw=0.2)
    ax.plot(setup.wa[istart:iend],setup.er[istart:iend],'cyan',lw=0.2)
    ax.axhline(y=0,ls='dotted',color='red',lw=0.2)
    ax.axvline(x=float(setup.walldla),color='red',lw=2,alpha=0.5)
    ax.axvline(x=float(setup.wallobs),color='red',lw=2,alpha=0.5)
    #if '--dlafit' in sys.argv:
    #    fit = residual(setup.fitparams,wafit)
    #    ax.plot(wafit,fit,'red',lw=0.7)
    #elif '--sdss' not in sys.argv:
    #    flux = 1.
    #    for Ntrans in range (len(setup.HIlist)):
    #        flux = flux*setup.p_voigt(setup.N,\
    #                                 setup.b,\
    #                                 wafit/(setup.zalpha+1),\
    #                                 setup.HIlist[Ntrans]['wave'],\
    #                                 setup.HIlist[Ntrans]['gamma'],\
    #                                 setup.HIlist[Ntrans]['strength'])
    #        flux  = gaussian_filter1d(flux,1.5)
    #    ax.plot(wafit,flux,'red',lw=0.7)

def specplot(fig,Ncol=1,Nplot=2):
    '''
    Plot the spectrum region from the detected Lyman-limit to the detected Lyman-alpha

    Parameters
    ----------
    fig   : Figure to be plotted on
    Ncol  : Number of columns to plot over
    Nplot : Plot number
    '''
    Nrows  = 23
    ymin   = 0
    istart = abs(setup.wa - ((setup.zalpha+1)*setup.HIlist[-1]['wave']-20)).argmin()
    iend   = abs(setup.wa - ((setup.zalpha+1)*setup.HIlist[0]['wave']+20)).argmin()
    ymax   = 1 if istart==iend else sorted(setup.fl[istart:iend])[int(0.9*(iend-istart))]
    x = setup.wa[istart:iend]
    y = setup.fl[istart:iend]        
    ax = fig.add_subplot(Nrows,Ncol,Nplot,xlim=[setup.wa[istart],setup.wa[iend]],ylim=[ymin,ymax])
    ax.yaxis.set_major_locator(NullLocator())
    ax.xaxis.set_major_locator(NullLocator())
    ax.plot(x,y,'black',lw=0.2)
    ax.plot(x,setup.er[istart:iend],'cyan',lw=0.2)
    for trans in setup.HIlist:
        ax.axvline(x=(setup.zalpha+1)*trans['wave'], color='red', lw=0.5)
    ax.axvline(x=setup.wallobs, color='lime', lw=1)
    xmin = 10*round(min(x)/10)
    xmax = 10*round(max(x)/10)
    if 10*round((xmax-xmin)/100)>0:
        ax.xaxis.set_major_locator(plt.FixedLocator(np.arange(xmin,xmax,10*round((xmax-xmin)/100))))
    else:
        ax.xaxis.set_major_locator(plt.FixedLocator([xmin,xmax]))            

def Hplot(fig,Ntrans,vmin=-1200.,vmax=3000.,Ncol=2,Nplot=10):    
    '''
    Plot the HI lines

    Parameters
    ----------
    fig    : Figure to be plotted on
    Ntrans : Transition number
    vmin   : Minimum velocity on plot in km/s
    vmax   : Maximum velocity on plot in km/s
    Ncol   : Number of columns to plot over
    Nplot  : Plot number
    '''
    Nrows   = 36
    ymin    = 0
    watrans = setup.HIlist[Ntrans]['wave']*(setup.zalpha+1) #observed wavelength of transition
    wabeg   = watrans*(1+vmin/setup.c)
    waend   = watrans*(1+vmax/setup.c)
    istart  = abs(setup.wa-wabeg).argmin()
    iend    = abs(setup.wa-waend).argmin()
    ymax    = 1 if istart==iend else sorted(setup.fl[istart:iend])[int(0.99*(iend-istart))]
    istart  = istart-1 if istart!=0 else istart
    iend    = iend+1
    v       = setup.c*((setup.wa-watrans)/watrans)
    vllobs  = setup.c*((setup.wallobs-watrans)/watrans)
    ax = fig.add_subplot(Nrows,Ncol,Nplot,xlim=[vmin,vmax],ylim=[ymin,ymax])
    ax.xaxis.set_major_locator(NullLocator())
    ax.yaxis.set_major_locator(NullLocator())
    ax.plot(v[istart:iend],setup.fl[istart:iend],'black',lw=0.2)
    ax.plot(v[istart:iend],setup.er[istart:iend],'cyan',lw=0.2)
    ax.axvline(x=0,ls='dashed',color='blue',lw=0.5,alpha=0.7)
    ax.axvline(x=setup.wallobs,color='red',lw=2,alpha=0.5)
    if setup.zmin!=setup.zmax:
        wamin = setup.HIlist[Ntrans]['wave']*(setup.zmin+1)
        wamax = setup.HIlist[Ntrans]['wave']*(setup.zmax+1)
        vmin2 = setup.c*(2*(wamin-watrans)/(wamin+watrans))
        vmax2 = setup.c*(2*(wamax-watrans)/(wamin+watrans))
        ax.axvline(x=vmin2,color='blue',lw=1,alpha=0.7)
        ax.axvline(x=vmax2,color='blue',lw=1,alpha=0.7)
    if '--dlasearch' in sys.argv and setup.zmin!=setup.zmax:
        '''Plotting the edges found of the system...'''
        ax.axvline(x=v[setup.point],color='orange',lw=1,alpha=0.7)
        if Ntrans==setup.nleftHI:
            ax.axvspan(vmin2,0,color='lime',lw=1)
        if Ntrans==setup.nrightHI:
            ax.axvspan(0,vmax2,color='lime',lw=1)
    if '--manual' not in sys.argv:
        '''Plotting first guesses'''
        wafit = np.arange(wabeg,waend,0.05)
        v     = setup.c*((wafit-watrans)/watrans)
        flux  = p_voigt(setup.N,setup.b,wafit/(setup.zalpha+1),setup.HIlist[Ntrans]['wave'],setup.HIlist[Ntrans]['gamma'],setup.HIlist[Ntrans]['strength'])
        ax.plot(v,flux,'red',lw=0.7,alpha=0.7)
    if '--dlafit' in sys.argv:
        '''Plotting mask'''
        y = np.ma.array(setup.fl,mask=1-setup.fitmask)
        ax.plot(v,y,'magenta',lw=1,alpha=0.7)
        '''Plotting fit'''
        wafit = np.arange(wabeg,waend,0.1)
        v     = setup.c*((wafit-watrans)/watrans)
        fit   = residual(setup.fitparams,wafit)
        ax.plot(v,fit,'magenta',lw=0.7,alpha=0.7)

def metalplot(fig,Ntrans,vmin=-500.,vmax=500.,Ncol=2,Nplot=11):
    '''
    Plot the HI lines

    Parameters
    ----------
    fig    : Figure to be plotted on
    Ntrans : Transition number
    vmin   : Minimum velocity on plot in km/s
    vmax   : Maximum velocity on plot in km/s
    Ncol   : Number of columns to plot over
    Nplot  : Plot number
    '''
    Nrows   = 36
    ymin    = 0
    watrans = (setup.zalpha+1.)*setup.Metallist[Ntrans]['Metalwave']
    v       = (setup.c*((setup.wa-watrans)/setup.wa))
    istart  = abs(v-vmin).argmin()
    iend    = abs(v-vmax).argmin()
    ymax    = 1 if istart==iend else sorted(setup.fl[istart:iend])[int(0.99*(iend-istart))]
    istart  = istart-1 if istart!=0 else istart
    iend    = iend+1
    y       = setup.fl[istart:iend]
    ax      = fig.add_subplot(Nrows,Ncol,Nplot,xlim=[vmin,vmax],ylim=[ymin,ymax])
    ax.yaxis.set_major_locator(NullLocator())
    ax.xaxis.set_major_locator(NullLocator())
    ax.plot(v[istart:iend],y,'black',lw=0.2)
    ax.text(0.9*vmin,0.2*ymax,setup.Metallist[Ntrans]['Metalline']+'_'+str(int(setup.Metallist[Ntrans]['Metalwave'])),color='blue',fontsize=7)
    ax.axvline(x=0, ls='dotted', color='blue', lw=0.2)
    if setup.zmin!=setup.zmax:
        '''Plotting the found edges of the system...'''
        wamin = setup.Metallist[Ntrans]['Metalwave']*(setup.zmin+1)
        wamax = setup.Metallist[Ntrans]['Metalwave']*(setup.zmax+1)
        vmin2 = setup.c*((wamin-watrans)/watrans)
        vmax2 = setup.c*((wamax-watrans)/watrans)
        ax.axvline(x=vmin2,color='blue',lw=0.2)
        ax.axvline(x=vmax2,color='blue',lw=0.2)

def wholespec():
    '''
    Plot the spectrum region from the detected Lyman-limit to the detected Lyman-alpha

    Parameters
    ----------
    fig   : Figure to be plotted on
    Ncol  : Number of columns to plot over
    Nplot : Plot number
    '''
    print '|- Plotting whole spectrum...',
    start_time = time.time()
    fig = figure(figsize=(8.27,11.69))
    axis('off'),xticks(()),yticks(())
    subplots_adjust(left=0.05, right=0.95, bottom=0.05, top=0.95, hspace=0.2, wspace=0.05)
    if setup.flag==None:
        plt.title(setup.qsoname+'   -   No suitable DLAs found in this spectrum!',fontsize=7)
    elif setup.flag=='dlafound':
        plt.title(setup.qsoname+'   |   Lyman-limit shift of %i km/s'%setup.dvshift,fontsize=7)
    else:
        plt.title(setup.qsoname+'   |   Lyman-limit found at %.2f'%setup.wallobs,fontsize=7)
    #colcode = []
    #for k in range(0,len(setup.zll)):
    #    r = lambda: randint(0,255)
    #    colcode.append('#%02X%02X%02X' % (r(),r(),r()))
    Ncol    = 1
    Nrows   = 8
    ymin    = 0
    ymax    = 1.2
    waveint = (setup.wa[-1]-setup.wa[0])/Nrows
    wmin    = setup.wa[0]
    wmax    = setup.wa[0] + waveint
    istart  = 0
    iend    = abs(setup.wa - wmax).argmin()
    for i in range(1,Nrows+1):
        x    = setup.wa[istart:iend]
        y    = setup.fl[istart:iend]
        ymax = 1 if iend==istart else sorted(y)[int(0.95*(iend-istart))]
        ax   = fig.add_subplot(Nrows,Ncol,i,xlim=[wmin,wmax],ylim=[-ymax,ymax])
        ax.plot(x,setup.er[istart:iend],'cyan',lw=0.2)
        ax.axhline(y=0,color='orange',lw=1,ls='dashed')
        if setup.flag=='dlafound':
            for trans in setup.HIlist:
                ax.axvline(x=(setup.zalpha+1)*trans['wave'], color='red', lw=1,alpha=0.4,zorder=2)
        if setup.flag!=None:
            ilim = abs(setup.wa-setup.wallobs1).argmin()
            ax.axvline(x=setup.wallobs1,color='green',lw=2,alpha=0.7)
            ax.axvspan(setup.wa[ilim-setup.npix1b],setup.wa[ilim+setup.npix1a],color='lime',lw=1,alpha=0.2,zorder=1)
            ilim = abs(setup.wa-setup.wallobs).argmin()
            ax.axvline(x=setup.wallobs,color='blue',lw=2,alpha=0.7)
            ax.axvspan(setup.wa[ilim-setup.npix2b],setup.wa[ilim+setup.npix2a],color='blue',lw=1,alpha=0.2,zorder=1)
        ax.plot(x,y,'black',lw=0.1,alpha=0.6,zorder=3)
        wmin   = wmax
        wmax   = wmin+waveint
        istart = iend
        iend   = abs(setup.wa - wmax).argmin()
    path = 'limit' if setup.flag=='llfound' else 'spec'
    os.system('mkdir -p ./candidates/'+path)
    savefig('./candidates/'+path+'/'+setup.qsoname+'.pdf')
    print round(float(time.time()-start_time),3),'seconds.'
    close(fig)
