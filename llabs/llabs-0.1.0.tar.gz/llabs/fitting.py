from .settings import *

def maskdef():

    setup.ileftmasklow  = abs(setup.wa - setup.HIlist[setup.nleftHI]['wave']*(setup.zmin+1)).argmin()
    setup.ileftmaskhigh = abs(setup.wa - setup.HIlist[setup.nleftHI]['wave']*(setup.zalpha+1)).argmin()
    for i in range(setup.ileftmaskhigh,setup.irange,-1):
        if np.average(setup.fl[i-setup.irange:i+setup.irange]/setup.er[i-setup.irange:i+setup.irange]) > setup.stdev:
            setup.ileftmasklow = i-int(setup.maskwidth*(setup.ileftmaskhigh-setup.ileftmasklow))
            break
                                                                                                                  
    setup.irightmasklow  = abs(setup.wa - setup.HIlist[setup.nrightHI]['wave']*(setup.zalpha+1)).argmin()               
    setup.irightmaskhigh = abs(setup.wa - setup.HIlist[setup.nrightHI]['wave']*(setup.zmax+1)).argmin()
    for i in range(setup.irightmasklow,len(setup.wa),1):
        if np.average(setup.fl[i-setup.irange:i+setup.irange]/setup.er[i-setup.irange:i+setup.irange]) > setup.stdev:
            setup.irightmaskhigh = i+int(setup.maskwidth*(setup.irightmaskhigh-setup.irightmasklow))
            break

#===============================================================

def fitHI():
    
    '''
    Using lmfit to fit a one component model to the absorber
    '''
    
    transmin = 0 #lowest transition to be fitted, alpha=0
    transmax = 30 # highest transition to be fitted, max 31

    voigtparams = Parameters()
    voigtparams.add('z', value=setup.zalpha, min=0.9*setup.zalpha, max=1.1*setup.zalpha,vary=True)
    voigtparams.add('N', value=setup.N, min=0,max=30,vary=False)
    voigtparams.add('b', value=setup.b,min=1.,max=200,vary=True)
    voigtparams.add('transmin',value=transmin,min=0,max=31,vary=False)
    voigtparams.add('transmax',value=transmax,min=0,max=30,vary=False)

    setup.guessparams = voigtparams
    
    setup.fitmask = np.ndarray((len(setup.wa),),dtype=bool)
    setup.fitmask.fill(0)
    setup.fitmask[setup.ileftmasklow:setup.ileftmaskhigh] = 1
    setup.fitmask[setup.irightmasklow:setup.irightmaskhigh] = 1

    out = minimize(residual, voigtparams, args=(setup.wa[setup.fitmask],setup.fl[setup.fitmask],setup.er[setup.fitmask]))
    report_fit(voigtparams)
    setup.fitchi2 = out.redchi
    setup.fitparams = voigtparams

    setup.zalpha  = setup.fitparams['z'].value
    setup.N       = setup.fitparams['N'].value
    setup.b       = setup.fitparams['b'].value
    setup.waalpha = (1.+setup.zalpha)*setup.HIlist[0]['wave']
    setup.walldla = (setup.zalpha+1.)*setup.HIlist[-1]['wave']
    setup.dvshift = 2*(setup.wallobs-setup.walldla)/(setup.wallobs+setup.walldla)*setup.c

#===============================================================

def _read_atom_dat():
    
    """
    Reads atom.dat file from VPfit into numpy array of strings.
    """
    
    atomdat  = sp.array([])

    restwl = []
    transs = []
    gammas = []
    resstr = []

    for line in open(setup.datapath+'atom.dat'):
        if line.startswith('!'):
            continue
        tmp = line.split()
        if len(tmp[0]) == 1:
            tmp[0] += ' ' + tmp[1]
            tmp.pop(1)
        transs.append(tmp[0])
        restwl.append(tmp[1])
        resstr.append(tmp[2])
        gammas.append(tmp[3])

    atomdat = sp.vstack(
        [sp.asarray(transs),
         sp.asarray(restwl),
         sp.asarray(resstr),
         sp.asarray(gammas)]).T

    return atomdat

#===============================================================

def _get_transition_info(transition='Halpha'):
    
    """
    Collects info on the transition. At later stage may read info from
    VPfit atom.dat and/or my own version of the galaxy lines thingie.
    NB: if the atom.dat file doesn't exist, will fall back on Halpha...
    """

    resstrengths={'Halpha': 0.695800, 'Hbeta': 0.121800, 'Hgamma': 0.044370}
    gammas = {'Halpha': 6.465e7, 'Hbeta': 2.062e7, 'Hgamma': 9.425e6}

    if os.path.exists(setup.datapath+'atom.dat'):
        atomdat = _read_atom_dat()
        tmp = transition.split()
        if len(tmp) == 3:
            tmp[0] += ' ' + tmp[1]
            tmp.pop(1)
        name = tmp[0]
        restwl = tmp[1]
        row = sp.where((atomdat[:, 0] == name) & (atomdat[:, 1] == restwl))
        #f = float(atomdat[row, 2])
        #g = float(atomdat[row, 3])
        f = atomdat[row, 2][0][0]
        g = atomdat[row, 3][0][0]
    else:
        f = resstrengths[transition]
        g = gammas[transition]

    return f, g

#===============================================================

def residual(voigtparams, wavelengths, flux=None, error=None):
    
    """
    Function to use with lmfit. Calculates the weighted residuals of flux-voigtprofile/error.
    voigtparams:   A parameter class defining the variables
    wavelengths:   An array of wavelengths to fit over
    flux:          Corresponding flux values. If absent, the model (and not the residuals) is returned. Useful for plotting.
    error:         Corresponding error values. If absent, the residuals are unweighted
    """

    wall = 911.753463416  #theoretical calculation (http://physics.nist.gov/PhysRefData/HDEL/data.html
    aLL = 6.30e-18 #ask Vincent if there is a newer value
    
    # Look at derivatives, stepsizes etc.
    
    z = voigtparams['z'].value                  #redshift
    N = voigtparams['N'].value                  #log(N), column density
    b = voigtparams['b'].value                  #b parameter in km/s
    transmin = voigtparams['transmin'].value    #Lowest transition in transitionnames to fit
    transmax = voigtparams['transmax'].value    #Highest transition in transitionnames to fit
     
    absmodel = np.ndarray((len(wavelengths),),dtype=float)
    absmodel.fill(1.)

    restwave = wavelengths/(1+z)
    
    for trans in setup.transitionnames[transmin:transmax]:
        f, gamma = _get_transition_info(trans)
        f, gamma = float(f), float(gamma)
        lambdao = float(trans.split()[-1])

        absmodel = absmodel*setup.p_voigt(N,b,restwave,lambdao,gamma,f)

        #interpolating between the Lyman Limit and the last line in the Lyman series

    if (transmax == len(setup.transitionnames)) and (restwave[0] <= wall):
        walast = float(setup.transitionnames[-1].split()[-1])
        ilast = abs(restwave-walast).argmin()
        ill = abs(restwave-wall).argmin()

        nsubbins = 1000
        subwav = np.linspace(wall,walast,nsubbins) #generating a wavelength array of nsubbins bins between wall and walast
        submodel = np.ndarray((nsubbins,),dtype=float)

        for i in range(0,nsubbins):
            submodel[i] = np.exp(-10**N*aLL*(subwav[i]/wall)**3)
            
            #rebin to match original wavelengths
        funct = sp.interpolate.splrep(subwav,submodel,s=0)
        interpolated = sp.interpolate.splev(restwave[ill:ilast],funct,der=0)

        absmodel[ill:ilast] = interpolated
        absmodel[0:ill] = interpolated[0] #setting the model to zero below the lyman limit

        #convolution with Gaussian to account for instrumental resolution (vsig = 2pix ~ 5km/sec)
        absmodel = sp.ndimage.filters.gaussian_filter1d(absmodel,1.5)

        #The output depends on wether flux or errors are given (if not given, the output can be used for plotting)
    if flux is None:
        return absmodel
    elif error is None:
        return flux-absmodel
    else:
        return (flux-absmodel)/error

#===============================================================

def fitlinear(x,y,xmin,xmax,ymin,ymax,xmin_fit,xmax_fit,err=None):

    xfit = np.arange(xmin,xmax,0.001)
    if err==None:
        a,b = polyfit(x,y,1)
    else:
        def func(func,a,b):
            return a + b*x
        pars,cov = curve_fit(func,x,y)
        yfit = pars[0] + pars[1]*xfit
        plot(xfit,yfit,color='blue',ls='dashed',lw=1)
        pars,cov = curve_fit(func,x,y,sigma=err)
        yfit = pars[0] + pars[1]*xfit
        plot(xfit,yfit,color='red',lw=1)
    print 'slope +/- error: %.4f +/- %.4f'%(pars[1],np.sqrt(cov[1][1]))

#==================================================================================================================
