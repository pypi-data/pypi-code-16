import sys

def showhelp():

    print ""
    print "--------------------------------------------------------------------------------------------"
    print "   Analysis of Magnetic Field Data from NURI Project"
    print "--------------------------------------------------------------------------------------------"
    print ""
    print "usage: nuri <operation> [--args]"
    print ""
    print "possible operations:"
    print ""
    print "    active           Plot active periods"
    print "    download         Download data from selective dates"
    print "    mapping          Identify location of the stations on Berkeley of map"
    print "    notify           Check list of files on server and notify station if missing data"
    print "    wavelet          Wavelet analysis"
    print ""
    print "--------------------------------------------------------------------------------------------"
    print ""
    quit()

def variables():

    v             = type('v', (), {})()
    v.home        = os.getenv('HOME')+'/ASTRO/'
    v.pathdata    = os.path.abspath(__file__).rsplit('/',1)[0] + '/data/'
    v.infile      = None
    v.filt        = None
    v.rate        = 3960.
    v.binning     = 0.5
    v.imin,v.imax = 0,-1
    v.tmin,v.tmax = None,None
    v.reset       = '--reset' in sys.argv
    v.notify      = '--notify' in sys.argv
    args          = numpy.array(sys.argv, dtype='str')
    start         = (datetime.now()+timedelta(days=-1)).strftime("%Y-%m-%d-%H")
    end           = (datetime.now()+timedelta(hours=7)).strftime("%Y-%m-%d-%H")
    v.imin        = 0     if '--imin'    not in sys.argv else   int(args[np.where(args=='--imin'   )[0][0]+1])
    v.imax        = -1    if '--imax'    not in sys.argv else   int(args[np.where(args=='--imax'   )[0][0]+1])
    v.station     = None  if '--station' not in sys.argv else   int(args[np.where(args=='--station')[0][0]+1])
    v.rate        = 3960. if '--rate'    not in sys.argv else float(args[np.where(args=='--rate'   )[0][0]+1])
    v.binning     = 0.5   if '--bin'     not in sys.argv else float(args[np.where(args=='--bin'    )[0][0]+1])
    v.tmin        = None  if '--tmin'    not in sys.argv else float(args[np.where(args=='--tmin'   )[0][0]+1])
    v.tmax        = None  if '--tmax'    not in sys.argv else float(args[np.where(args=='--tmax'   )[0][0]+1])
    v.tdata       = None  if '--tdata'   not in sys.argv else   str(args[np.where(args=='--tdata'  )[0][0]+1])
    v.date        = None  if '--date'    not in sys.argv else   str(args[np.where(args=='--date'   )[0][0]+1])
    v.path        = None  if '--path'    not in sys.argv else   str(args[np.where(args=='--path'   )[0][0]+1])
    v.start       = start if '--start'   not in sys.argv else   str(args[np.where(args=='--start'  )[0][0]+1])
    v.end         = end   if '--end'     not in sys.argv else   str(args[np.where(args=='--end'    )[0][0]+1])
    if v.infile!=None and os.path.exists(v.infile)==False:
        print 'The path of the input file is incorrect...'
        quit()
    return v

if sys.argv[0].split('/')[-1]!='nuri':
    pass
elif len(sys.argv)==1 or sys.argv[1] in ['--help','-h']:
    showhelp()     
elif len(sys.argv)>1 and '--help' not in sys.argv and '-h' not in sys.argv:
    sys.stderr.write('Import all relevant packages...')
    import struct,sys,os,matplotlib,time,pylab,glob
    import scipy,numpy,mlpy,obspy,operator,math,smtplib
    import numpy                  as np
    import matplotlib.pylab       as plt
    import matplotlib.dates       as md
    import matplotlib             as mpl
    from email.mime.text          import MIMEText
    from pylab                    import *
    from matplotlib               import pyplot as plt
    from matplotlib               import rc,animation
    from matplotlib.pyplot        import *
    from scipy                    import signal
    from scipy.optimize           import curve_fit,fminbound
    from datetime                 import datetime,timedelta,date
    print >>sys.stderr,' done!'
    setup = variables()
