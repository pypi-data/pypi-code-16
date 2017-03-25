""" Set global variables """

import sys,os

def showhelp():
    """
    Display help menu
    """
    print ""
    print "--------------------------------------------------------------------------------------"
    print "  Damped Lyman-Alpha systems finder"
    print "--------------------------------------------------------------------------------------"
    print ""
    print "usage: LLabs <input> [--args]"
    print ""
    print "acceptable inputs:"
    print ""
    print "   <filelist>      List of quasar spectra to be scanned for suitable DLA systems"
    print "   <logfile>       Output from LLabs to generate statiscal plots"
    print "   <spectrum>      Run LLabs on one single quasar spectrum"
    print ""
    print "required parameters:"
    print ""
    print "   --resolution    Spectrograph used [ low | high ]"
    print ""
    print "default parameters:"
    print "" 
    print "   --dvlyamax      Maximum velocity dispersion for Lyman alpha line [",setup.dvlyamax,"]"
    print "   --dvtrans       Velocity dispersion of higher Lyman transitions [",setup.dvtrans,"]"
    print "   --irange        Pixel interval over which fluctuations are evaluated [",setup.irange,"]"
    print "   --limshift      Shift upper limit for unphysically large shifts [",setup.limshift,"]"
    print "   --limsnr        SNR lower limit to discard noisy candidates [",setup.limsnr,"]"
    print "   --maskwidth     Additional fraction of the saturated region [",setup.maskwidth,"]"
    print "   --stdev         Standard deviation threshold for significant SNR [",setup.stdev,"]"
    print ""
    print "optional arguments:"
    print ""
    print "   --bin           Change binning for histogram"
    print "   --dlafit        Fit the DLA candidate"
    print "   --dlasearch     Search for DLA candidate"
    print "   --reval         Re-evaluate SNR and metal absorption for each system"
    print "   --help, -h      Display help message"
    print "   --manual        Manually select the edges and the limit Lyman"
    print "   --metals        Provide list of metal transitions for statistical plots"
    print "   --nodla         Do not look for Damped Lyman system"
    print "   --noplot        Don't plot the figures"
    print "   --replot        Plot the figures based on the log file results"
    print "   --reset         Uncomment infile.dat content and re-scan the spectra"
    print "   --verbose, -v   Do verbose"
    print "   --zabs          Specify DLA absorption redshift"
    print ""
    print "Notes: In order to stop scanning the spectra from the infile.dat, you can type"
    print "       'touch stop' in the terminal in the running directory, the loop will stop"
    print "       after completion of the currently processed spectrum."
    print ""
    print "--------------------------------------------------------------------------------------"
    print ""
    quit()

def variables():

    # Setup figure information
    rc('font', size=2)
    rc('axes', labelsize=8, linewidth=0.2)
    rc('legend', fontsize=2, handlelength=10)
    rc('xtick', labelsize=6)
    rc('ytick', labelsize=6)
    rc('lines', lw=0.2, mew=0.2)
    rc('grid', linewidth=1)
    # Empty keymap for interactive tool
    keyMaps = [key for key in rcParams.keys() if 'keymap.' in key]
    for keyMap in keyMaps:
        rcParams[keyMap] = ''
    # Prepare setup array
    sys.stderr.write('Prepare setup object...')
    v        = type('v', (), {})()
    v.HIlist = [{'wave':1215.6701,'strength':0.416400,'gamma':6.265E8},
                {'wave':1025.7223,'strength':0.079120,'gamma':1.897E8},
                {'wave':972.53680,'strength':0.029000,'gamma':8.127E7},
                {'wave':949.74310,'strength':0.013940,'gamma':4.204E7},
                {'wave':937.80350,'strength':0.007799,'gamma':2.450E7},
                {'wave':930.74830,'strength':0.004814,'gamma':1.236E7},
                {'wave':926.22570,'strength':0.003183,'gamma':8.255E6},
                {'wave':923.15040,'strength':0.002216,'gamma':5.785E6},
                {'wave':920.96310,'strength':0.001605,'gamma':4.210E6},
                {'wave':919.35140,'strength':0.001200,'gamma':3.160E6},
                {'wave':918.12940,'strength':0.000921,'gamma':2.432E6},
                {'wave':917.18060,'strength':7.226e-4,'gamma':1.911E6},
                {'wave':916.42900,'strength':0.000577,'gamma':1.529E6},
                {'wave':915.82400,'strength':0.000469,'gamma':1.243E6},
                {'wave':915.32900,'strength':0.000386,'gamma':1.024E6},
                {'wave':914.91900,'strength':0.000321,'gamma':8.533E5},
                {'wave':914.57600,'strength':0.000270,'gamma':7.186E5},
                {'wave':914.28600,'strength':0.000230,'gamma':6.109E5},
                {'wave':914.03900,'strength':0.000197,'gamma':5.237E5},
                {'wave':913.82600,'strength':0.000170,'gamma':4.523E5},
                {'wave':913.64100,'strength':0.000148,'gamma':3.933E5},
                {'wave':913.48000,'strength':0.000129,'gamma':3.443E5},
                {'wave':913.33900,'strength':0.000114,'gamma':3.030E5},
                {'wave':913.21500,'strength':0.000101,'gamma':2.679E5},
                {'wave':913.10400,'strength':0.000089,'gamma':2.382E5},
                {'wave':913.00600,'strength':0.000080,'gamma':2.127E5},
                {'wave':912.91800,'strength':0.000071,'gamma':1.907E5},
                {'wave':912.83900,'strength':0.000064,'gamma':1.716E5},
                {'wave':912.76800,'strength':0.000058,'gamma':1.550E5},
                {'wave':912.70300,'strength':0.000053,'gamma':1.405E5},
                {'wave':912.64500,'strength':0.000048,'gamma':1.277E5}]
    
    v.Hindex = [0,5,10,15,20,25,
                1,6,11,16,21,26,
                2,7,12,17,22,27,
                3,8,13,18,23,28,
                4,9,14,19,24,29]
    
    v.Metallist = [{'Metalline':'MgII', 'Metalwave':2796.35},
                   {'Metalline':'MgII', 'Metalwave':2803.53},
                   {'Metalline':'SiII', 'Metalwave':1260.42},
                   {'Metalline':'SiII', 'Metalwave':1526.71},
                   {'Metalline':'SiII', 'Metalwave':1304.37},
                   {'Metalline':'SiII', 'Metalwave':1808.01},
                   {'Metalline':'SiIV', 'Metalwave':1393.76},
                   {'Metalline':'SiIV', 'Metalwave':1402.77},
                   {'Metalline':'CI',   'Metalwave':945.188},
                   {'Metalline':'CII',  'Metalwave':1334.53},
                   {'Metalline':'CII',  'Metalwave':1036.34},
                   {'Metalline':'CIV',  'Metalwave':1548.20},
                   {'Metalline':'CIV',  'Metalwave':1550.78},
                   {'Metalline':'OI',   'Metalwave':1302.17},
                   {'Metalline':'OI',   'Metalwave':988.77},
                   {'Metalline':'OI',   'Metalwave':1039.23},
                   {'Metalline':'FeII', 'Metalwave':2382.76},
                   {'Metalline':'FeII', 'Metalwave':2600.17},
                   {'Metalline':'FeII', 'Metalwave':2344.21},
                   {'Metalline':'FeII', 'Metalwave':1144.94},
                   {'Metalline':'FeII', 'Metalwave':2586.65},
                   {'Metalline':'FeII', 'Metalwave':1608.45},
                   {'Metalline':'FeII', 'Metalwave':2374.46},
                   {'Metalline':'FeII', 'Metalwave':1081.87},
                   {'Metalline':'FeII', 'Metalwave':1112.05},
                   {'Metalline':'FeII', 'Metalwave':2260.78},
                   {'Metalline':'FeII', 'Metalwave':1611.20},
                   {'Metalline':'AlIII','Metalwave':1854.72},
                   {'Metalline':'AlIII','Metalwave':1862.79},
                   {'Metalline':'ZnII', 'Metalwave':2026.13709},
                   {'Metalline':'ZnII', 'Metalwave':2062.66045}]

    v.knownd2h = [{'name':'J000344-232354','zabs':2.18700},
                  {'name':'J001708+813508','zabs':2.79796},
                  {'name':'J001708+813508','zabs':3.32110},
                  {'name':'J010806+163550','zabs':2.53600},
                  {'name':'J013301-400628','zabs':2.80000},
                  {'name':'J034943-381031','zabs':3.02500},
                  {'name':'J040718-441013','zabs':2.62100},
                  {'name':'J042214-384452','zabs':3.08600},
                  {'name':'J083141+524517','zabs':3.37800},
                  {'name':'J083141+524517','zabs':3.51400},
                  {'name':'J091613+070224','zabs':2.61843},
                  {'name':'J095852+120245','zabs':3.09622},
                  {'name':'J101155+294141','zabs':2.50400},
                  {'name':'J113418+574204','zabs':3.41088},
                  {'name':'J120523-074232','zabs':4.67200},
                  {'name':'J124610+303117','zabs':2.52566},
                  {'name':'J133724+315254','zabs':3.17447},
                  {'name':'J135842+652236','zabs':3.06726},
                  {'name':'J141950+082948','zabs':3.04984},
                  {'name':'J155810-003120','zabs':2.70262},
                  {'name':'J171938+480412','zabs':0.70100},
                  {'name':'J193957-100241','zabs':3.25590},
                  {'name':'J193957-100241','zabs':3.57200},
                  {'name':'J220852-194400','zabs':2.07620}]
    
    v.home            = os.getenv('HOME')
    v.home            = v.home+'/Volumes/ASTRO_HOME/ASTRO/data/' if '--server' in sys.argv else v.home+'/ASTRO/data/' 
    v.c               = 299792.458
    v.datapath        = os.path.abspath(__file__).rsplit('/', 1)[0] + '/data/'
    v.sdsspath        = v.home+'SDSS/DR10/'
    v.atomlist        = numpy.loadtxt(v.datapath+'atom.dat',dtype='str',delimiter='\n')
    v.transitionnames = [v.atomlist[i][0:18] for i in range (len(v.HIlist))]
    v.pub             = numpy.loadtxt(v.datapath+'published.dat',dtype='str')
    v.sdssdla         = numpy.genfromtxt(v.datapath+'SDSS_DLA_DR10.dat',names=True,dtype=object,skip_header=1)
    v.d               = {}
    v.zmin,v.zmax     = float('nan'),float('nan')
    v.verbose         = '--verbose' in sys.argv or '-v' in sys.argv
    for i in range (len(v.HIlist)):
        v.d['HI{0}'.format(i)] = numpy.loadtxt(v.datapath+'HI'+str(i)+'.dat',comments='!')
    args         = numpy.array(sys.argv, dtype='str')
    v.resolution = None   if '--resolution' not in sys.argv else           str(args[numpy.where(args=='--resolution')[0][0]+1])
    v.irange     = 10     if '--irange'     not in sys.argv else           int(args[numpy.where(args=='--irange'    )[0][0]+1])
    v.binning    = 47     if '--bin'        not in sys.argv else           int(args[numpy.where(args=='--bin'       )[0][0]+1])
    v.limsnr     = 0.     if '--limsnr'     not in sys.argv else         float(args[numpy.where(args=='--limsnr'    )[0][0]+1])
    v.dvlyamax   = 20000. if '--dvlyamax'   not in sys.argv else         float(args[numpy.where(args=='--dvlyamax'  )[0][0]+1])
    v.dvtrans    = 50.    if '--dvtrans'    not in sys.argv else         float(args[numpy.where(args=='--dvtrans'   )[0][0]+1])
    v.limshift   = 10000. if '--limshift'   not in sys.argv else         float(args[numpy.where(args=='--limshift'  )[0][0]+1])
    v.maskwidth  = 0.5    if '--maskwidth'  not in sys.argv else         float(args[numpy.where(args=='--maskwidth' )[0][0]+1])
    v.stdev      = 2.5    if '--stdev'      not in sys.argv else         float(args[numpy.where(args=='--stdev'     )[0][0]+1])
    v.zabs       = None   if '--zabs'       not in sys.argv else         float(args[numpy.where(args=='--zabs'      )[0][0]+1])
    v.dvalpha    = None   if '--dvalpha'    not in sys.argv else         float(args[numpy.where(args=='--dvalpha'   )[0][0]+1])
    v.metals     = None   if '--metals'     not in sys.argv else numpy.loadtxt(args[numpy.where(args=='--metals'    )[0][0]+1],dtype=str)
    print >>sys.stderr,' done!'
    if len(sys.argv)>1 and '--help' not in sys.argv and '-h' not in sys.argv and v.resolution==None:
        print '\nERROR: --resolution not found...\n'
        quit()        
    return v

if sys.argv[0].split('/')[-1]!='llabs':
    pass
else:
    sys.stderr.write('Import all relevant packages...')
    import math,os,sys,re,time,random,numpy
    import numpy                           as np
    import scipy                           as sp
    import matplotlib.pyplot               as plt
    import matplotlib                      as mpl
    from matplotlib.ticker                 import MultipleLocator, FormatStrFormatter
    from matplotlib                        import rc
    from matplotlib.pyplot                 import *
    from scipy.ndimage                     import gaussian_filter1d
    from matplotlib.backends.backend_pdf   import PdfPages
    from math                              import sqrt, pi
    from scipy                             import stats
    from scipy.optimize                    import curve_fit
    if 'z3399255' not in os.getenv('HOME'):
        import seaborn
        from astropy.io import fits
    else:
        import pyfits as fits
    print >>sys.stderr,' done!'
    setup = variables()
    if len(sys.argv)==1 or '--help' in sys.argv or '-h' in sys.argv:
        showhelp()
