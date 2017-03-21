from .settings import *
from .extract  import *

def download():

    """
    This routine will download the NURI data present in Google Drive.
    """
    
    if '--help' in sys.argv or '-h' in sys.argv:

        print "" 
        print "-------------------------------------------------------------------------"
        print ""
        print "description:"
        print ""
        print "  This operation downloads the data for specific period. The default"
        print "  period downloaded will be the last 24 hours."
        print ""
        print "required arguments:"
        print ""
        print "   --start        Starting date of the data to be retrieved [last 24hrs]"
        print "                    The format is YYYY-MM-DD[-hh]"
        print "   --end          Ending date of the data to be retrieved [current time]"
        print "                    The format is YYYY-MM-DD[-hh]"
        print ""
        print "optional arguments:"
        print ""
        print "   --path         Path where the data are stored [current repository]"
        print "   --station      Station(s) to retrieve data from [all the stations]"
        print ""
        print "example:"
        print ""
        print "   nuri download --start 2016-07-12 --end 2016-07-12-2 --station 1 \ "
        print "                 --path /Users/vincent/ASTRO/data/NURI"
        print ""
        print "-------------------------------------------------------------------------"
        print ""
        quit()
        
    if setup.path!=None:
        os.chdir(setup.path)
    os.system('skicka ls -r /MagneticFieldData/ > data')
    data = np.loadtxt('data',dtype=str,delimiter='\n')
    d0 = datetime(*np.array(setup.start.split('-'),dtype=int))
    d1 = datetime(*np.array(setup.end.split('-'),dtype=int))
    dt = timedelta(hours=1)
    dates = np.arange(d0,d1,dt)
    for d in dates:
        year  = d.astype(object).year
        month = d.astype(object).month
        day   = d.astype(object).day
        hour  = d.astype(object).hour
        path  = 'MagneticFieldData/%i/%i/%i/%i/'%(year,month,day,hour)
        fzip  = '%i-%i-%i_%i-xx.zip'%(year,month,day,hour)
        for station in range(4):
            if (int(setup.station) in [None,station+1]) and  path+'NURI-station-%02i/'%(station+1)+fzip in data:
                os.system('mkdir -p ./NURI-station-%02i/'%(station+1))
                os.system('skicka download /'+path+'NURI-station-%02i/'%(station+1)+fzip+' ./')
                os.system('unzip '+fzip)
                os.system('mv %i-%i-%i_%i-xx_* NURI-station-%02i'%(year,month,day,hour,station+1))
                os.system('rm '+fzip)
    os.system('rm data')
