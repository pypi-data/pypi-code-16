from .settings import *

def extract_coord(filename):
    """
    Extract longitude and latitude from time data binary file
    """
    with open(filename,'rb') as f:
        data = f.read()
    f.close()
    s = len(data)/63
    data = struct.unpack('<'+'qipQddcdcdd'*s,data)
    data = np.reshape(data,(s,11))
    lat  = float(str(float(data[0,5])/100).split('.')[0])
    lat  = lat + (float(data[0,5])-lat*100)/60
    lat  = -lat if data[0,8]=='S' else lat
    lon  = float(str(float(data[0,7])/100).split('.')[0])
    lon  = lon + (float(data[0,7])-lon*100)/60
    lon  = -lon if data[0,6]=='W' else lon
    return lat,lon

def read_time(filename):
    """
    Function to read the binary file of first version
    """
    print filename.split('/')[-1]
    # Read binary file and sore data in array
    with open(filename,'rb') as f:
        data = f.read()
    f.close()
    if 'time_v2' in filename:
        # Define the total number records (63 bytes per record)
        size = len(data)/63
        # Unpack each record as the following succession:
        # int64,int32,byte,int64,double,double,char,double,char,double,double
        data = struct.unpack('<'+'qi?Qddcdcdd'*size,data)
        # Reshape array so that each row corresponds to one record
        data       = np.reshape(data,(size,11))
        date0      = datetime.fromtimestamp(float(data[0,4]))
        datestr    = date0.strftime('%Y/%m/%d')
        t0str      = date0.strftime('%H:%M:%S.%f')
        gps_offset = (datetime(1980,1,6)-datetime(1970,1,1)).total_seconds()
        gps_epoch  = construct_utc_from_metadata(datestr,t0str) + gps_offset
        delay      = round((float(data[0,4])-gps_epoch)/3600.)
        tgps       = []
        # Default timing calculation
        for i in range(len(data)-1):
            for j in range(int(data[i,1])):
                step = (float(data[i+1,4])-float(data[i,4]))/int(data[i,1])
                tgps.append(float(data[i,4]) + j*step - delay*3600.)
        for j in range(int(data[-1,1])):
            tgps.append(float(data[-1,4]) + j*step - delay*3600.)
        # Overwrite timing array if mode 1 selected
        if setup.tmode==1:
            for i in range(len(data)):
                for j in range(int(data[i,1])):
                    tgps.append(float(data[i,4]) + round(j*1./3960.,6) - delay*3600.)
        # Overwrite timing array if mode 2 selected
        if setup.tmode==2:
            num        = int(sum([float(data[i,1]) for i in range(len(data))]))
            start_time = float(data[0,4])-delay*3600.
            end_time   = start_time + num / 3960.
            tgps       = np.linspace(start_time,end_time,num)
    else:
        # Define the total number records (28 bytes per record)
        size = len(data)/28
        # Unpack each record as the following succession: int64,int32,int64,double
        data = struct.unpack('<'+'qiQd'*size,data)
        # Reshape array so that each row corresponds to one record
        data = np.reshape(data,(size,4))
        tgps = []
        utc_offset = (datetime(1970,1,1)-datetime(1,1,1)).total_seconds()
        for i in range(len(data)):
            for j in range(int(data[i,1])):
                t = (int(data[i,2]) & 0x7fffffffffffffff)
                t = t/1e7 - utc_offset + j*1./3960.
                tgps.append(t)
    return np.array(tgps)

def read_axis(filename):
    """
    Function to read the binary file of magnetic field axis
    """
    print filename.split('/')[-1]
    # Read binary file and sore data in array
    with open(filename,'rb') as f:
        data = f.read()
    f.close()
    # Define the total number records (63 bytes per record)
    size = len(data)/8
    # Unpack each record
    data = np.array(struct.unpack('d'*size,data))
    return data

def magfield(start_time,end_time,rep='/Users/vincent/ASTRO/data/NURI/'):
    """
    Glob all files withing user-defined period and extract data.
    
    Parameters
    ----------
    t0 : int
      GPS timestamp of the first required magnetic field data
    t1 : int
      GPS timestamp of the last required magnetic field data
    
    Return
    ------
    ts_data, ts_list : TimeSeries, dictionary, list
      Time series data for selected time period, list of time series
      for each segment
    """
    start,t0,end,t1 = time_edge(start_time,end_time)
    dataset = []
    for date in numpy.arange(start,end,timedelta(hours=1)):
        date = date.astype(datetime)
        path1 = rep+'/'+date.strftime("%Y-%-m-%-d_%-H-xx_time.bin")
        path2 = rep+'/'+date.strftime("%Y-%-m-%-d_%-H-xx_time_v2.bin")
        dataset += glob.glob(path1)
        dataset += glob.glob(path2)
    if setup.sample:
        dataset = glob.glob(rep+"/*time*.bin")
    tdata,xdata,ydata,zdata = [],[],[],[]
    for tfile in sorted(dataset):
        version = 'time_v2' if 'time_v2'in tfile else 'time'
        tdata   = np.hstack((tdata,read_time(tfile)))
        if setup.orientation in [None,'x']:
            xfile = tfile.replace(version,'rawX_uT_3960Hz')
            xdata = np.hstack((xdata,read_axis(xfile))) 
        if setup.orientation in [None,'y']:
            yfile = tfile.replace(version,'rawY_uT_3960Hz')
            ydata = np.hstack((ydata,read_axis(yfile)))
        if setup.orientation in [None,'z']:
            zfile = tfile.replace(version,'rawZ_uT_3960Hz')
            zdata = np.hstack((zdata,read_axis(zfile)))
    idx = np.where(np.logical_and(t0<=tdata,tdata<=t1))[0]
    return np.vstack((tdata[idx],xdata[idx],ydata[idx],zdata[idx])).T

def time_edge(start_time,end_time):
    """
    Calculate timestamp from dates
    """
    dstr    = ['%Y','%m','%d','%H','%M','%S','%f']
    dsplit  = '-'.join(dstr[:start_time.count('-')+1])
    start   = datetime.strptime(start_time,dsplit)
    dsplit  = '-'.join(dstr[:end_time.count('-')+1])
    end     = datetime.strptime(end_time,dsplit)
    t0      = time.mktime(start.timetuple())+start.microsecond/1e6
    t1      = time.mktime(end.timetuple())+end.microsecond/1e6
    return start,t0,end,t1

def gnomedata(station,start_time,end_time,rep='/Users/vincent/ASTRO/data/NURI/'):
    """
    Glob all files withing user-defined period and extract data.

    Parameters
    ----------
    station : str
      Name of the station to be analysed
    t0 : int
      GPS timestamp of the first required magnetic field data
    t1 : int
      GPS timestamp of the last required magnetic field data

    Return
    ------
    ts_data, ts_list, activity : TimeSeries, dictionary, list
      Time series data for selected time period, list of time series
      for each segment, sampling rate of the retrieved data
    """
    setname = "MagneticFields"
    start,t0,end,t1 = time_edge(start_time,end_time)
    dataset = []
    for date in numpy.arange(start,end,timedelta(minutes=1)):
        date = date.astype(datetime)
        fullpath = rep+'/'+station+'_'+date.strftime("%Y%m%d_%H%M*.h5")
        dataset += glob.glob(fullpath)
    if setup.sample:
        dataset = glob.glob(rep+"/*.h5")
    gps_offset = (datetime(1980,1,6)-datetime(1970,1,1)).total_seconds()
    tdata,xdata = [],[]
    for fname in sorted(dataset):
        hfile       = h5py.File(fname, "r")
        dset        = hfile[setname]
        gps_epoch   = construct_utc_from_metadata(dset.attrs["Date"], dset.attrs["t0"])
        sample_rate = dset.attrs["SamplingRate(Hz)"]
        start_time  = gps_epoch	+ gps_offset
        end_time    = start_time + len(dset[:]) / sample_rate
        tarray      = np.linspace(start_time,end_time,len(dset[:]))
        idx         = np.where(np.logical_and(t0<tarray,tarray<t1))[0]
        xdata       = np.hstack((xdata,dset[:][idx]))
        tdata       = np.hstack((tdata,tarray[idx]))
        hfile.close()
    return np.vstack((tdata,xdata)).T

def construct_utc_from_metadata(datestr, t0str):
    """
    Constructing UTC timestamp from metadata

    Parameters
    ----------
    datestr : str
      Date of the extracted data
    t0str : str
      GPS time
    """
    instr = "%d-%d-%02dT" % tuple(map(int, datestr.split('/')))
    instr += t0str
    t = astropy.time.Time(instr, format='isot', scale='utc')
    return t.gps

