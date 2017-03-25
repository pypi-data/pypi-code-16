from .settings import *
from .manual   import *
from .plots    import *
from .utils    import *

def scanning():
    # Create qsolist based on whether the input argument is a list or path to single spectrum
    if 'infile' in sys.argv[1]:
        if 'z3399255' not in os.getenv('PWD') and '--reset' in sys.argv:
            os.system("sed -i '' 's,!,,' "+sys.argv[1])
        qsolist = np.loadtxt(sys.argv[1],dtype=object,comments='!',ndmin=2)
        qsolist = dict(zip(qsolist[0], qsolist[1:].T))
    else:
        qsolist = {}
        qsolist['path'] = [sys.argv[1]]
    n = 1
    for i in range(len(qsolist['path'])):
        proceed         = False
        setup.wa,setup.fl = [],[]
        setup.filename   = qsolist['path'][i]
        setup.spectrum   = re.split(r'[/.]',setup.filename)
        setup.qsoname    = setup.spectrum[-2]
        setup.zalpha     = float(qsolist['zabs'][i]) if ('zabs' in qsolist and qsolist['zabs'][i]!='-') else setup.zabs if setup.zabs!=None else float('nan')
        setup.dvshift    = float('nan')
        setup.dlawidth   = float('nan')
        setup.waalpha    = float('nan')
        setup.walldla    = float('nan')
        setup.N          = float('nan')
        setup.b          = float('nan')
        setup.flag       = None
        if os.path.exists('./candidates/dla/'+setup.qsoname+'.pdf'):
            os.system('rm ./candidates/dla/'+setup.qsoname+'.pdf')
        if os.path.exists('./candidates/limit/'+setup.qsoname+'.pdf'):
            os.system('rm ./candidates/limit/'+setup.qsoname+'.pdf')
        if os.path.exists('./candidates/spec/'+setup.qsoname+'.pdf'):
            os.system('rm ./candidates/spec/'+setup.qsoname+'.pdf')
        if os.path.exists(setup.filename)==True:
            proceed = True
            print '\n',n,' ======================================',setup.qsoname,'\n'
            readspec()
            if len(setup.wa)==0:
                print '|  |- Zero flux everywhere, spectrum not usable.'
                proceed = False
                n += 1
        if proceed==True:
            if '--manual' in sys.argv:
                manual_scan()
            else:
                print '|- Start automatic scanning...'
                loopfind()
            if '--dlafit' in sys.argv:
                maskdef()
                fitHI()
            equiwidth()
            fraction()
            snrestimator()
            update()
            if '--noplot' not in sys.argv:
                if setup.flag=='dlafound':
                    plotdla()
                else:
                    wholespec()
            print '|- End of scanning.'                    
            n += 1
        if 'z3399255' not in os.getenv('PWD') and sys.argv[1]=='infile.dat':
            os.system("sed -i '' 's,"+setup.filename+",!"+setup.filename.replace('!','')+",' "+sys.argv[1])
        if os.path.exists('./stop')==True:
            os.system('rm stop')
            break    

def loopfind():
    '''
    Looping over spectrum to find lyman limit (llfind) and corresponding Lyman-alpha (findsatreg)
    '''
    # Check if DLA search is activated or not
    if '--dlasearch' in sys.argv or math.isnan(setup.zalpha)==True:
        dv       = 2000
        wastart  = setup.wa[0] * (2*setup.c+dv) / (2*setup.c-dv)
        istart   = 0 if setup.resolution=='low' else abs(setup.wa-wastart).argmin()
        iend     = len(setup.wa)
    elif math.isnan(setup.zalpha)==False:
        wstart   = setup.HIlist[-1]['wave']*(setup.zalpha+1.)-100
        istart   = abs(setup.wa-wstart).argmin()
        wend     = setup.HIlist[0]['wave']*(setup.zalpha+1.)
        iend     = abs(setup.wa-wend).argmin()
    else:
        print '|- DLA redshift not provided...'
    # Looping over spectrum to find lyman limit
    llfind(istart,iend)
    if '--dlasearch' in sys.argv or math.isnan(setup.zalpha)==True:
        # If LL found
        if setup.flag=='llfound':
            findsatreg()
        # If DLA type system found
        if setup.flag=='dlafound':
            getbestz()
        # If DLA type system confirmed, find best column density and Doppler parameter estimatse
        if setup.flag=='dlafound':
            getparam()
    if setup.flag==None:
        print '|- No observable Lyman limit found...'

def llfind(istart,iend):

    ill          = None
    threshold1   = 7   if setup.resolution=='low' else 10
    threshold2   = 5   if setup.resolution=='low' else 5
    setup.npix1a = 50  if setup.resolution=='low' else 250
    setup.npix1b = 100 if setup.resolution=='low' else 500
    for i in range(istart+setup.npix1b,iend):
        fl1,er1 = setup.fl[i:i+setup.npix1a],abs(setup.er[i:i+setup.npix1a])
        badpix  = np.where(er1>10000)[0]
        fl1,er1 = np.delete(fl1,badpix,0),np.delete(er1,badpix,0)
        fl2,er2 = setup.fl[i-setup.npix1b:i],abs(setup.er[i-setup.npix1b:i])
        badpix  = np.where(er2>10000)[0]
        fl2,er2 = np.delete(fl2,badpix,0),np.delete(er2,badpix,0)
        avgfl1  = np.median(fl1)
        avgfl2  = np.median(fl2)
        avger1  = sum(er1**2)/setup.npix1a**2
        avger2  = sum(er2**2)/setup.npix1b**2
        cond1   = (avgfl1-avgfl2)/np.sqrt(avger1+avger2) > threshold1
        cond2   = avgfl1/np.median(er1) > threshold2*avgfl2/np.median(er2)
        if cond1==cond2==True:
            ill = i
            setup.wallobs1 = setup.wa[ill]
            break
    if ill!=None:
        threshold1   = 7  if setup.resolution=='low' else 10
        threshold2   = 5  if setup.resolution=='low' else 5
        setup.npix2a = 20 if setup.resolution=='low' else 100
        setup.npix2b = 40 if setup.resolution=='low' else 200
        for i in range(ill,ill+setup.npix1a):
            fl1,er1 = setup.fl[i:i+setup.npix2a],abs(setup.er[i:i+setup.npix2a])
            badpix  = np.where(er1>10000)[0]
            fl1,er1 = np.delete(fl1,badpix,0),np.delete(er1,badpix,0)
            fl2,er2 = setup.fl[i-setup.npix2b:i],abs(setup.er[i-setup.npix2b:i])
            badpix  = np.where(er2>10000)[0]
            fl2,er2 = np.delete(fl2,badpix,0),np.delete(er2,badpix,0)
            avgfl1  = np.median(fl1)
            avgfl2  = np.median(fl2)
            avger1  = sum(er1**2)/setup.npix2a**2
            avger2  = sum(er2**2)/setup.npix2b**2
            cond1   = (avgfl1-avgfl2)/np.sqrt(avger1+avger2) > threshold1
            cond2   = avgfl1/np.median(er1) > threshold2*avgfl2/np.median(er2)
            if cond1==cond2==True:
                setup.wallobs = setup.wa[i]
                terminate(i)
                break

def terminate(i):
    '''
    Define function for when scanning is terminated
    '''
    setup.flag    = 'llfound'
    setup.wallobs = setup.wa[i]                        
    setup.zlimit  = (setup.wallobs/setup.HIlist[-1]['wave'])-1.
    print '|- Lyman Limit found at %.2f'%setup.wallobs,'i.e. zll = %.5f'%setup.zlimit
    if '--dlasearch' not in sys.argv and math.isnan(setup.zalpha)==False:
        setup.flag = 'dlafound'    
        print '|  |- DLA already pre-detected at z=%.5f'%setup.zalpha
        setup.walldla = setup.HIlist[-1]['wave']*(setup.zalpha+1)
        setup.dvshift = 2*(setup.wallobs-setup.walldla)/(setup.wallobs+setup.walldla)*setup.c
        print '|  |- LL shift estimated to',int(setup.dvshift),'km/s'
        
def findsatreg():
    '''
    Look for Lyman alpha signature of DLA type systems by looking for wide velocity absorption.
    '''
    print '|- Looking for DLA Ly-alpha line...'
    flag    = 0
    dlalist = []
    # Wavelength of the associated Lyman-alpha
    waalpha = setup.HIlist[0]['wave']*(setup.zlimit+1.)+50
    # Pixel position of the associated Lyman-alpha
    istart  = abs(setup.wa - waalpha).argmin()
    # Define minimum redshift to scan the spectrum for Lyman-alpha
    dv      = -setup.limshift
    zll     = setup.zlimit * (2*setup.c+dv) / (2*setup.c-dv) + 2*dv / (2*setup.c-dv)
    # Wavelength of the associated Lyman-limit
    walimit = setup.HIlist[0]['wave']*(zll+1.)
    # Pixel position of the associated Lyman limt
    iend    = abs(setup.wa - walimit).argmin()
    # Initialise array to record all likely candidates
    likely  = np.empty((0,4))
    # Scan spectrum blueward and look for DLA type Lyman alpha absorption
    for i in range(istart-setup.irange,iend,-1):
        # Median value over irange below current position
        medianleft  = sorted(setup.fl[i-setup.irange:i])[int(setup.irange/2)]
        # Median value over irange above current position
        medianright = sorted(setup.fl[i:i+setup.irange])[int(setup.irange/2)]
        avgrange    = np.average(setup.fl[i-setup.irange:i+setup.irange]/setup.er[i-setup.irange:i+setup.irange])
        # If right wing found
        if (flag==0) and (avgrange < setup.stdev) and (medianleft < setup.fl[i] < medianright):
            # Set the new right edge pixel position
            iright = i
            # Flag position
            flag = 1
        # If left wing found
        if (flag==1) and (avgrange > setup.stdev) and (medianleft > setup.fl[i] > medianright):
            # Set the new left edge pixel position
            ileft = i
            # Flag position
            flag = 2
            # Calculate system redshift
            setup.zalpha = ((setup.wa[ileft]+setup.wa[iright])/2)/setup.HIlist[0]['wave']-1
            # Velocity interval
            velint = setup.c*(2*(setup.wa[iright]-setup.wa[ileft])/(setup.wa[iright]+setup.wa[ileft]))
            # Condition 1 for Lyalpha detection: decently large velocity dispersion
            cond1  = setup.dvtrans < velint < setup.dvlyamax
            # Condition 2 for Lyalpha detection: average flux/error less than setup.stdev
            cond2  = np.average(setup.fl[ileft:iright]/setup.er[ileft:iright]) < setup.stdev
            cond3  = setup.zalpha not in dlalist
        # If DLA type Lyman alpha found
        if (flag==2) and cond1==True and cond2==True and cond3==True:
            print '|  |- DLA Ly-a found at','%.5f'%setup.zalpha,'with dv =',int(velint),'km/s'
            # Add system to list of possible candidates
            likely = np.vstack([likely,[setup.zalpha,velint,ileft,iright]])
            # DLA redshift recorded for future loop
            (dlalist).append(setup.zalpha)
            # Discard the system and stop looking for the left edge
            setup.flag = 'dlafound'
            flag = 0
        elif flag==2:
            # If velocity width smaller than minimum DLA type width (i.e. N=19.5, b=10),
            # discard the system and stop looking for the left edge
            flag = 0
    # If no suitable system found
    if len(likely)==0:
        print '|  |- No suitable DLA Ly-a found...'
    else:
        print '|- Looking for saturated system among each DLA candidate...'
        # Initialise array to record all system candidates
        setup.allsys = np.empty((0,4),dtype=object)
        for idx in range(len(likely)):
            zalpha = likely[idx,0]
            ileft  = int(likely[idx,2])
            iright = int(likely[idx,3])
            '''
            Once Lyman alpha found, look within its redshift range for a saturated system over setup.nHI HI transitions.
            Check, in that order, if the transition is:
            1) outside the spectral range (flag=1) > system recorded based on previous transitions found
            2) noisy (flag=2) > system recorded based on previous transitions found
            3) not saturated (flag=-1) > system discarded
            '''
            print '|  |- Exploring region around DLA candidate at z=%.5f'%zalpha
            # Initialise array to record all system candidates
            system = np.empty((0,4),dtype=object)
            # End of the scan (left part of the detected Lyman alpha transition)
            imin   = ileft
            # Start of the scan (right part of the detected Lyman alpha transition)
            # The starting pixel is located setup.dvtrans km/s leftward the detected
            # Lya right edge.
            imax   = abs(setup.wa-setup.wa[iright]*(1-setup.dvtrans/setup.c)).argmin()
            # Initialise Lya left edge as upper limit for future right edges
            iprev  = iright+2
            # Scan spectrum blueward and look for DLA type Lyman alpha absorption
            for i in range(imax,imin,-1):
                # Initialise flag for detected absorption systems
                flag     = 0
                Lya_zmid = setup.wa[i]/setup.HIlist[0]['wave']-1
                Lya_wmin = setup.wa[i]*(1-setup.dvtrans/setup.c)
                Lya_wmax = setup.wa[i]*(1+setup.dvtrans/setup.c)
                Lya_zmin = Lya_wmin/setup.HIlist[0]['wave']-1
                Lya_zmax = Lya_wmax/setup.HIlist[0]['wave']-1
                # Pixel of the new left edge, setup.dvtrans blueward the new Lya pixel position
                Lya_imin = abs(setup.wa-Lya_wmin).argmin()
                # Pixel of the new right edge, setup.dvtrans redward the new Lya pixel position
                Lya_imax = abs(setup.wa-Lya_wmax).argmin()
                if setup.verbose: print '|  |  |- Looking at %.5f-%.5f redshift region around pixel %.0f'%(Lya_zmin,Lya_zmax,i)
                # Loop over HI transitions
                for j in range (len(setup.HIlist)):
                    HI_wmid = setup.wa[i]/setup.HIlist[0]['wave']*setup.HIlist[j]['wave']
                    HI_wmin = HI_wmid*(1-setup.dvtrans/setup.c)
                    HI_wmax = HI_wmid*(1+setup.dvtrans/setup.c)
                    # Pixel index on the blue edge
                    HI_imin = abs(setup.wa-HI_wmin).argmin()
                    # Pixel index on the red edge
                    HI_imax = abs(setup.wa-HI_wmax).argmin()
                    npixsat = len(np.where(np.array(setup.fl[HI_imin:HI_imax]/setup.er[HI_imin:HI_imax])<setup.stdev)[0])
                    if setup.verbose: print '|  |  |  |- Exploring HI%02i region:'%j
                    if  HI_imax-HI_imin<10:
                        #print 'Not enough pixels to evaluate the saturation.'
                        break
                    elif setup.wa[HI_imin]>HI_wmax or setup.wa[HI_imax]<HI_wmin:
                        #print 'Region not available in spectrum.'
                        pass
                    elif setup.wa[HI_imin]<setup.wallobs or HI_imin==0:
                        # If transition blueward the observable Lyman limit
                        if setup.verbose: print 'End of spectrum reached.'
                        # Discard the HI transition from analysis
                        break
                    elif npixsat<0.4*(HI_imax-HI_imin):
                        # If more than 20% of the pixels have average flux/error larger than setup.stdev
                        if setup.verbose: print '%.0f percent saturation.'%(100*npixsat/(HI_imax-HI_imin))
                        # Flag system as not saturated
                        flag = 1
                        # Stop the loop and go to next pixel
                        break
                    else:
                        if setup.verbose: print '%.0f percent saturation.'%(100*npixsat/(HI_imax-HI_imin))
                        pass
                if setup.verbose: print '|  |  |  |- Final flag:',flag
                # If saturated system found
                if flag==0:
                    # If new system found (current right edge below previous left edge)
                    if Lya_imax < iprev:
                        if setup.verbose: print '|  |  |  |- New system found!'
                        # Record left edge redshift
                        zmin     = setup.wa[Lya_imin]/setup.HIlist[0]['wave']-1
                        # Record right edge redshift
                        zmax     = setup.wa[Lya_imax]/setup.HIlist[0]['wave']-1
                        # Left edge wavelength of the candidate system
                        wamin    = setup.HIlist[0]['wave']*(zmin+1)
                        # Right edge wavelength of the candidate system
                        wamax    = setup.HIlist[0]['wave']*(zmax+1)
                        # Calculate velocity dispersion
                        dlawidth = 2*(wamax-wamin)/(wamax+wamin)*setup.c
                        # Add system to list of possible candidates
                        system   = np.vstack([system,[j,zmin,zmax,dlawidth]])
                    # If region connected to previous absorption candidate
                    if Lya_imax >= iprev:
                        if setup.verbose: print '|  |  |  |- System extended.'
                        # Re-estimate redshift of the left edge
                        zmin  = setup.wa[Lya_imin]/setup.HIlist[0]['wave']-1
                        # Re-estimate wavelength of the left edge
                        wamin = setup.HIlist[0]['wave']*(zmin+1)
                        # Re-estimate velocity dispersion
                        dlawidth = 2*(wamax-wamin)/(wamax+wamin)*setup.c
                        # Update system information in list
                        system[-1,:] = [j,zmin,zmax,dlawidth]
                    # Define pixel of current Lya left edge as upper limit for future right edge
                    iprev = Lya_imin
                else:
                    if setup.verbose: print '|  |  |  |- No saturated region found.'
                    pass
            for i in range(len(system)):
                if (zmin+zmax)/2<setup.zlimit:
                    setup.allsys = np.vstack((setup.allsys,system[i]))
        if len(setup.allsys)==0 or len(np.where(setup.allsys[:,3]>100)[0])==0:
            setup.flag = 'llfound'
            print '|  |- No suitable saturated Lyman series found...'
        else:
            setup.flag = 'dlafound'
            print '|- List of found saturated region(s):'
            for i in np.where(setup.allsys[:,3]>100)[0]:
                # Midpoint redshift of the DLA-type system found
                zalpha = (float(setup.allsys[i,1])+float(setup.allsys[i,2]))/2
                print '|  |- System found at','%.5f'%zalpha,'with dv =',int(float(setup.allsys[i,3])),'km/s'

def getbestz():
    '''
    For all HI transitions available in the spectrum, measure the
    velocity dispersion, and re-estimate the redshift in the closest
    redshift range available.
    '''
    for best in np.where(setup.allsys[:,3]>100)[0]:
        setup.nHI     = int(setup.allsys[best,0])
        setup.zmin    = float(setup.allsys[best,1])
        setup.zmax    = float(setup.allsys[best,2])
        # Midpoint redshift of the DLA-type system found
        setup.zalpha  = (setup.zmin+setup.zmax)/2
        # Midpoint wavelength of the DLA-type system found
        setup.waalpha = setup.HIlist[0]['wave']*(setup.zalpha+1)
        setup.nleftHI = setup.nrightHI = setup.nHI if setup.nHI == 0 else setup.nHI-1
        # Loop over all HI transitions down to Lyman order limit
        for j in range(setup.nHI):
            # Re-defining pixel position based on previous value
            imin = abs(setup.wa - setup.HIlist[j]['wave']*(setup.zmin+1)).argmin()
            # Re-defining pixel position based on previous value
            iref = abs(setup.wa - setup.HIlist[j]['wave']*(setup.zalpha+1)).argmin()
            # Re-defining pixel position based on previous value
            imax = abs(setup.wa - setup.HIlist[j]['wave']*(setup.zmax+1)).argmin()
            npix = len(np.where(np.array(setup.fl[imin:imax]/setup.er[imin:imax])<setup.stdev)[0])
            if npix<0.4*(imax-imin):
                setup.flag = 'llfound'
                break
            for i in range(iref,imin,-1):
                med = np.median(setup.fl[i-setup.irange:i+setup.irange]/setup.er[i-setup.irange:i+setup.irange])
                if (med > setup.stdev):
                    setup.zmin = setup.wa[i]/setup.HIlist[j]['wave']-1
                    setup.nleftHI = j
                    break
                elif setup.wa[i] < setup.wallobs:
                    break
            for i in range(iref,imax):
                med = np.median(setup.fl[i-setup.irange:i+setup.irange]/setup.er[i-setup.irange:i+setup.irange])
                if (med > setup.stdev):
                    setup.zmax = setup.wa[i]/setup.HIlist[j]['wave']-1
                    setup.nrightHI = j
                    break
                elif setup.wa[i] < setup.wallobs:
                    break
            # Re-defining center redshift
            setup.zalpha = (setup.zmin+setup.zmax)/2
        if setup.flag=='dlafound':
            print '|- Best region found at %.5f'%setup.zalpha
            setup.lastHI   = max([setup.nleftHI,setup.nrightHI])
            # Left edge wavelength of the candidate system
            wamin         = setup.HIlist[setup.lastHI]['wave']*(setup.zmin+1)
            # Right edge wavelength of the candidate system
            wamax         = setup.HIlist[setup.lastHI]['wave']*(setup.zmax+1)
            # Re-estimate velocity dispersion
            setup.dlawidth = 2*(wamax-wamin)/(wamax+wamin)*setup.c
            # Midpoint redshift of the DLA-type system found
            setup.zalpha   = (setup.zmin+setup.zmax)/2
            # Midpoint wavelength of the DLA-type system found
            setup.waalpha  = (setup.zalpha+1.)*setup.HIlist[0]['wave']
            setup.walldla  = (setup.zalpha+1.)*setup.HIlist[-1]['wave']
            # LL shift between observed LL (setup.wallobs) and associated LL of the detected DLA
            setup.dvshift  = 2*(setup.wallobs-setup.walldla)/(setup.wallobs+setup.walldla)*setup.c
            # Central pixel position of the Lyman alpha absorption
            illdla  = abs(setup.wa - setup.walldla).argmin()
            dvlldla = 2*abs(setup.wa[illdla]-setup.walldla)/(setup.wa[illdla]+setup.walldla)*setup.c
            print '|  |- Left wing found at Ly',setup.nleftHI,'and right wing at Ly',setup.nrightHI
            print '|  |- z estimated to','%.5f'%setup.zalpha,'with DLA velocity width of',int(setup.dlawidth),'km/s'
            break
            
def getparam():
    '''
    Determine the column density and Doppler parameter of the DLA by locate precisely the wings of the Lyman alpha.
    '''
    # Wavelength of the associated Lyman alpha
    waalpha   = setup.HIlist[0]['wave']*(setup.zalpha+1)
    # Central pixel position of the Lyman alpha absorption
    imidalpha = abs(setup.wa - waalpha).argmin()
    # Initialisation for Lyman alpha wing detection from center
    i,flag    = 0,0
    # Starting from the center, search for one of the 2 wings
    while flag==0:
        ileft    = imidalpha-i
        avgrange = np.average(setup.fl[ileft-setup.irange:ileft+setup.irange]/setup.er[ileft-setup.irange:ileft+setup.irange])
        if (avgrange > setup.stdev):
            # Calculate width of Lyman alpha
            widthfirstHI = 2*(setup.wa[imidalpha+i]-setup.wa[imidalpha-i])/(setup.wa[imidalpha+i]+setup.wa[imidalpha-i])*setup.c
            # Pixel position of detected wing (orange line in plot)
            setup.point = ileft
            # Stop loop
            flag = 1
        iright   = imidalpha+i
        avgrange = np.average(setup.fl[iright-setup.irange:iright+setup.irange]/setup.er[iright-setup.irange:iright+setup.irange])
        if (avgrange > setup.stdev):
            # Calculate width of Lyman alpha
            widthfirstHI = 2*(setup.wa[imidalpha+i]-setup.wa[imidalpha-i])/(setup.wa[imidalpha+i]+setup.wa[imidalpha-i])*setup.c
            # Pixel position of detected wing (orange line in plot)
            setup.point = iright
            flag = 1
        i = i + 1
    col = np.arange(19.5,23,0.01)
    Ndx = abs(setup.d['HI0'][:,0] - widthfirstHI).argmin()
    setup.N = float(col[Ndx])
    print '|  |- N estimated to','%.2f'%setup.N,'using',int(widthfirstHI),'km/s wide HI 1215'
    dop = np.arange(10,50,1)
    bdx = abs(setup.d['HI'+str(setup.lastHI)][Ndx,:] - setup.dlawidth).argmin()
    setup.b = float(dop[bdx])
    print '|  |- b estimated to','%.2f'%setup.b,'using',int(setup.dlawidth),'km/s wide Lyman',setup.lastHI
    print '|  |- LL shift estimated to',int(setup.dvshift),'km/s'
