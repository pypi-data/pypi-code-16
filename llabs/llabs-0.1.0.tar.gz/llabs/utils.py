from .settings import *
                
def readspec():
    
    if 'log' not in sys.argv[1]:
        print '|- Loading spectrum...'
    if setup.spectrum[-1]=='fits':
        hdu = fits.open(setup.filename)
        d   = hdu[0].data
        hd  = hdu[0].header
        if setup.resolution=='low':
            hdu0 = hdu[0].header
            hdu1 = hdu[1].header
            setup.wa = np.array(10.**(hdu0['coeff0'] + hdu0['coeff1'] * np.arange(hdu1['naxis2'])))
            setup.co = np.array(hdu[1].data['model'])
            setup.fl = np.array(hdu[1].data['flux'])
            setup.er = np.array([1/np.sqrt(hdu[1].data['ivar'][i]) if hdu[1].data['ivar'][i]!=0 else 10**32 for i in range (len(setup.fl))])
        else:
            setup.wa = 10**(hd['CRVAL1'] + (hd['CRPIX1'] - 1 + np.arange(hd['NAXIS1']))*hd['CDELT1'])
            setup.co = d[3,:]             # continuum estimate
            setup.fl = d[0,:]             # normalised flux
            setup.er = d[1,:]             # the normalised 1 sigma error
        badpixel = np.append(np.where(setup.er>1.e10)[0],np.where(setup.fl==1.)[0])
        setup.wa = np.delete(setup.wa,badpixel,0)
        setup.co = np.delete(setup.co,badpixel,0)
        setup.fl = np.delete(setup.fl,badpixel,0)
        setup.er = np.delete(setup.er,badpixel,0)
        name = setup.filename.split('/')
        setup.qsoname = name[-1].replace('.fits','')
    elif setup.spectrum[-1]=='dat':
        d = np.genfromtxt(setup.filename)
        setup.wa = d[:,0]
        setup.fl = d[:,1]             # normalised flux
        setup.er = d[:,2]             # the normalised 1 sigma error
        if np.average(setup.er) == 0:
            setup.er.fill(.01)
        badpixel = np.append( (np.where(abs(setup.er) < 1e-10)[0]) , (np.where(abs(setup.er) > 1e+10)[0]))
        setup.wa = np.delete(setup.wa,badpixel,0)
        setup.fl = np.delete(setup.fl,badpixel,0)
        setup.er = np.delete(setup.er,badpixel,0)
        name = setup.filename.split('/')
        setup.qsoname = name[-1].replace('.dat','')
    else:
        '''
        Read simulated ASCII spectrum from qsosim9. Only the second spectrum is read.
        There's no noise in the spectra so it's randomly generated
        specfile:   filename
        '''
        d = np.genfromtxt(setup.filename)
        setup.wa = d[:,0]
        setup.co = np.ndarray((len(setup.wa),))
        setup.co.fill(1)              # continuum estimate
        setup.fl = d[:,1]             # normalised flux
        setup.er = d[:,2]             # the normalised 1 sigma error
        badpixel = np.append( (np.where(abs(setup.er) < 1e-10)[0]) , (np.where(abs(setup.er) > 1e+10)[0]))
        setup.wa = np.delete(setup.wa,badpixel,0)
        setup.co = np.delete(setup.co,badpixel,0)
        setup.fl = np.delete(setup.fl,badpixel,0)
        setup.er = np.delete(setup.er,badpixel,0)
        name = setup.filename.split('/')
        setup.qsoname = name[-1].replace('.dat','')

def update():

    if '--reval' in sys.argv and '--manual' in sys.argv:
        for i in range(len(setup.data2)):
            setup.flag       = 'dlafound'
            setup.filename   = str(setup.data2['QSO'][i])
            setup.N          = float(setup.data2['N'][i])
            setup.b          = float(setup.data2['b'][i])
            setup.zalpha     = float(setup.data2['z'][i])
            setup.dlawidth   = float(setup.data2['DLAwidth'][i])
            setup.dvshift    = float(setup.data2['shift'][i])
            setup.walldla    = float(setup.data2['walldla'][i])
            setup.waalpha    = (setup.zalpha+1) * setup.HIlist[0]['wave']
            setup.wallobs    = setup.walldla * (2*setup.c + setup.dvshift) / (2*setup.c - setup.dvshift)
            setup.wmin       = setup.waalpha * (2*setup.c - setup.dlawidth) / (2*setup.c + setup.dlawidth)
            setup.wmax       = setup.waalpha * (2*setup.c + setup.dlawidth) / (2*setup.c - setup.dlawidth)
            setup.zmin       = setup.wmin / setup.HIlist[0]['wave'] - 1
            setup.zmax       = setup.wmax / setup.HIlist[0]['wave'] - 1
            setup.filename   = setup.home + setup.filename
            setup.readfits(setup.filename) if setup.filename.split('.')[-1]=='fits' else setup.readascii(setup.filename)
            setup.metal_equiwidth()
            setup.metal_fraction()
            setup.snrestimator()
            results = []
            results.append(setup.filename)
            results.append('%.2f'%setup.walldla)
            results.append('%.2f'%setup.wallobs)
            results.append('%.2f'%setup.dvshift)
            results.append('%.4f'%setup.zmin)
            results.append('%.4f'%setup.zmax)
            results.append('%.2f'%setup.dlawidth)
            results.append('%.4f'%setup.zalpha)
            results.append('%.2f'%setup.N)
            results.append('%.2f'%setup.b)
            results.append('%.2f'%setup.avgsnr)
            for j in range (len(setup.equiwidth)):
                results.append('%.2f'%setup.equiwidth[j])
                results.append('%.2f'%setup.fraction[j])
            data = np.array([results]) if i==0 else np.vstack((data,results))
    else:
        condition = (setup.flag=='dlafound') or (setup.flag=='llfound' and '--nodla' in sys.argv)
        if condition==True:
            results = []
            results.append(setup.filename)
            results.append('%.2f'%setup.walldla)
            results.append('%i'%setup.npix1a)
            results.append('%i'%setup.npix1b)
            results.append('%.2f'%setup.wallobs1)
            results.append('%i'%setup.npix2a)
            results.append('%i'%setup.npix2b)
            results.append('%.2f'%setup.wallobs)
            results.append('%.2f'%setup.dvshift)
            results.append('%.4f'%setup.zmin)
            results.append('%.4f'%setup.zmax)
            results.append('%.2f'%setup.dlawidth)
            results.append('%.4f'%setup.zalpha)
            results.append('%.2f'%setup.N)
            results.append('%.2f'%setup.b)
            results.append('%.2f'%setup.avgsnr)
            for i in range (len(setup.equiwidth)):
                results.append('%.2f'%setup.equiwidth[i])
                results.append('%.2f'%setup.fraction[i])
        if os.path.exists('infile.log')==True:
            data = np.loadtxt('infile.log',dtype='string',comments='!',ndmin=2)
            data = np.delete(data,0,0)
            if setup.filename in data[:,0]:
                idx = np.where(data[:,0]==setup.filename)[0][0]
                if condition==True:
                    data[idx] = results
                else:
                    data = np.delete(data,[idx],0)
            elif condition==True:
                data = np.vstack((data,results))
            data = data[data[:,0].argsort()]
        elif condition==True:
            data = np.array([results])
        else:
            data = []
    if len(data)>0:
        metcol = '{0:>15}'.format('SNR')
        for i in range (len(setup.Metallist)):
            name = setup.Metallist[i]['Metalline']+'_'+str(setup.Metallist[i]['Metalwave']).split('.')[0]
            metcol = metcol+'{0:>15}'.format('EW_'+name)
            metcol = metcol+'{0:>15}'.format('FR_'+name)
        logfile = open('infile.log','w')
        logfile.write('{0:<35}'.format('QSO'))
        logfile.write('{0:>15}'.format('walldla'))
        logfile.write('{0:>8}'.format('npix1a'))
        logfile.write('{0:>8}'.format('npix1b'))
        logfile.write('{0:>15}'.format('wallobs1'))
        logfile.write('{0:>8}'.format('npix2a'))
        logfile.write('{0:>8}'.format('npix2b'))
        logfile.write('{0:>15}'.format('wallobs'))
        logfile.write('{0:>12}'.format('shift'))
        logfile.write('{0:>10}'.format('zmin'))
        logfile.write('{0:>10}'.format('zmax'))
        logfile.write('{0:>10}'.format('DLAwidth'))
        logfile.write('{0:>10}'.format('z'))
        logfile.write('{0:>10}'.format('N'))
        logfile.write('{0:>10}'.format('b'))
        logfile.write(metcol)
        logfile.write('\n')
        for i in range (len(data)):
            if data[i,1]!='-':
                logfile.write('{0:<35}'.format(data[i,0]))
                logfile.write('{0:>15}'.format(data[i,1]))
                logfile.write( '{0:>8}'.format(data[i,2]))
                logfile.write( '{0:>8}'.format(data[i,3]))
                logfile.write('{0:>15}'.format(data[i,4]))
                logfile.write( '{0:>8}'.format(data[i,5]))
                logfile.write( '{0:>8}'.format(data[i,6]))
                logfile.write('{0:>15}'.format(data[i,7]))
                logfile.write('{0:>12}'.format(data[i,8]))
                logfile.write('{0:>10}'.format(data[i,9]))
                logfile.write('{0:>10}'.format(data[i,10]))
                logfile.write('{0:>10}'.format(data[i,11]))
                logfile.write('{0:>10}'.format(data[i,12]))
                logfile.write('{0:>10}'.format(data[i,13]))
                logfile.write('{0:>10}'.format(data[i,14]))
                for j in range(15,len(data[i])):
                    logfile.write('{0:>15}'.format(data[i,j]))
                logfile.write('\n')
        logfile.close()
    elif os.path.exists('./infile.log')==True:
        os.system('rm ./infile.log')

def equiwidth():
    '''
    Determine the absorption equivalent width around metal lines within the DLA velocity dispersion.
    '''
    setup.equiwidth = []
    for trans in setup.Metallist:
        if setup.flag=='dlafound':
            wamin  = trans['Metalwave']*(setup.zmin+1)
            wamax  = trans['Metalwave']*(setup.zmax+1)
            imin   = abs(setup.wa-wamin).argmin()
            imax   = abs(setup.wa-wamax).argmin()
            if imin >= imax:
                (setup.equiwidth).append(0)
            else:
                ymax   = sorted(setup.fl[imin:imax])[int(0.99*(imax-imin))]
                metabs = 0
                for i in range(imin,imax-1):
                    flux   = 0 if setup.fl[i]<=0 else 1 if setup.fl[i]>=ymax else setup.fl[i]/ymax
                    metabs += (1-flux)*(setup.wa[i+1]-setup.wa[i])/(setup.zalpha+1)
                (setup.equiwidth).append(metabs)
        else:
            (setup.equiwidth).append(float('nan'))
            
def fraction():
    '''
    Determine the fraction of pixels with absorption around metal lines
    CHECK OUT THE DEFINITION OF DELTAV in http://arxiv.org/pdf/astro-ph/0606185v1.pdf,better described
    here http://arxiv.org/pdf/1303.7239v3.pdf. Not sure it's possible to use here, since they visually
    inspect to require the lines aren't saturated...
    '''
    setup.fraction = []
    for trans in setup.Metallist:
        if setup.flag=='dlafound':
            wamin  = trans['Metalwave']*(setup.zmin+1)
            wamax  = trans['Metalwave']*(setup.zmax+1)
            imin    = abs(setup.wa-wamin).argmin()
            imax    = abs(setup.wa-wamax).argmin()
            index   = np.where(setup.fl[imin:imax] < 1. - setup.stdev*setup.er[imin:imax])
            metfrac = float(len(index[0]))/float(imax-imin) if imin<imax else 0
            (setup.fraction).append(metfrac)
        else:
            (setup.fraction).append(float('nan'))

def snrestimator():

    if setup.flag in ['llfound','dlafound']:
        wmin = setup.walldla if setup.flag=='dlafound' else setup.wallobs
        wmax = setup.waalpha if setup.flag=='dlafound' else setup.wallobs+1000
        snr  = []
        ibeg = abs(setup.wa - wmin).argmin()
        iend = abs(setup.wa - wmax).argmin() 
        for j in range(ibeg,iend):
            if np.isnan(setup.fl[j])==np.isnan(setup.er[j])==False:
                snr.append(setup.fl[j]/setup.er[j])
        setup.avgsnr = np.average(snr)
