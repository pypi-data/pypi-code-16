from .settings import *
from .utils    import *

def keyfig():
    
    # Setup figure information
    rc('font', size=2)
    rc('axes', labelsize=8, linewidth=0.2)
    rc('legend', fontsize=2, handlelength=10)
    rc('xtick', labelsize=12)
    rc('ytick', labelsize=12)
    rc('lines', lw=0.2, mew=0.2)
    rc('grid', linewidth=1)
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
            
    xlab      = 'Lyman limit shift (km/s)'
    ylab      = 'Average equivalent width ($\mathrm{\AA}$)'
    x         = setup.data['shift']
    y,yerr    = setup.metew,setup.metew_err

    def func(x,a,b):
        return a + b*x
    
    style = ['o' if 'UVES' in setup.data['QSO'][i] else 's' if 'HIRES' in setup.data['QSO'][i] else 'd' for i in range(len(setup.data['QSO']))]
    label = ['UVES' if 'UVES' in setup.data['QSO'][i] else 'HIRES' if 'HIRES' in setup.data['QSO'][i] else 'SDSS' for i in range(len(setup.data['QSO']))]
    color = []
    for i in range(len(setup.data['QSO'])):
        color.append('black')
        for j in range(len(setup.knownd2h)):
            cond1 = re.split('[/ .]',setup.data['QSO'][i])[-2]==setup.knownd2h[j]['name']
            cond2 = abs(float(setup.data['z'][i])-setup.knownd2h[j]['zabs'])<0.01
            if cond1 and cond2:
                color[-1]='red'
                print setup.data['z'][i]
                break
    fig = figure(figsize=(12,5))
    plt.subplots_adjust(left=0.1, right=0.95, bottom=0.1, top=0.95, hspace=0, wspace=0)
    ax = subplot(111,ylim=[0,1],xlim=[0,4000])
    for i in range(len(x)):
        order = 1 if color[i]=='black' else 2
        scatter(x[i],y[i],marker=style[i],c=color[i],s=150,edgecolors='none',zorder=order,alpha=0.6)
        errorbar(x[i],y[i],yerr=yerr[i],fmt='o',ms=0,c=color[i],zorder=order)
    xfit = np.arange(0,4000,0.001)
    coeffs,matcov = curve_fit(func,x,y,sigma=yerr)
    yfit = func(xfit,coeffs[0],coeffs[1])
    print '|  |- Weighted fit: %.6f +/- %.6f'%(coeffs[1],np.sqrt(matcov[1][1]))
    plot(xfit,yfit,color='black',lw=3,ls='dashed')
    ylabel(ylab,fontsize=12)
    xlabel(xlab,fontsize=12)
    savefig('./plots/keyfig.pdf')
    clf()
    
    xlab = 'Lyman limit shift (km/s)'
    ylab = 'DLA velocity dispersion (km/s)'
    x    = setup.data['shift']
    y    = setup.data['DLAwidth']

    fig = figure(figsize=(7,6))
    plt.subplots_adjust(left=0.1, right=0.87, bottom=0.1, top=0.95, hspace=0, wspace=0)
    plt.subplots_adjust(left=0.1, right=0.95, bottom=0.1, top=0.95, hspace=0, wspace=0)
    ax = subplot(111,ylim=[0,500],xlim=[0,2500])
    for i in range(len(x)):
        order = 1 if color[i]=='black' else 2
        scatter(x[i],y[i],marker=style[i],c=color[i],s=150,edgecolors='none',zorder=order,alpha=0.6)
    xfit = np.arange(0,4000,0.001)
    coeffs,matcov = curve_fit(func,x,y,sigma=yerr)
    yfit = func(xfit,coeffs[0],coeffs[1])
    print '|  |- Weighted fit: %.6f +/- %.6f'%(coeffs[1],np.sqrt(matcov[1][1]))
    plot(xfit,yfit,color='black',lw=3,ls='dashed')
    ylabel(ylab,fontsize=12)
    xlabel(xlab,fontsize=12)
    savefig('./plots/keyfig2.pdf')
    clf()
