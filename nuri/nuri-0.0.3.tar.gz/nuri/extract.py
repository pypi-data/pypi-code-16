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
        data = struct.unpack('<'+'qipQddcdcdd'*size,data)
        # Reshape array so that each row corresponds to one record
        data = np.reshape(data,(size,11))
        tgps = []
        for i in range(len(data)):
            for j in range(int(data[i,1])):
                tgps.append(float(data[i,4]) + j*1./3960.)
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
    return np.array(tgps)+setup.delay*3600.

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
    dstr    = ['%Y','%m','%d','%H','%M','%S']
    dsplit  = '-'.join(dstr[:start_time.count('-')+1])
    start   = datetime.strptime(start_time,dsplit)
    dsplit  = '-'.join(dstr[:end_time.count('-')+1])
    end     = datetime.strptime(end_time,dsplit)
    dataset = []
    for date in numpy.arange(start,end,timedelta(hours=1)):
        date = date.astype(datetime)
        path1 = rep+'/'+date.strftime("%Y-%-m-%-d_%-H-xx_time.bin")
        path2 = rep+'/'+date.strftime("%Y-%-m-%-d_%-H-xx_time_v2.bin")
        dataset += glob.glob(path1)
        dataset += glob.glob(path2)
    if sample:
        dataset = glob.glob(rep+"/*time*.bin")
    tdata,xdata,ydata,zdata = [],[],[],[]
    for tfile in dataset:
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
    t0  = time.mktime(start.timetuple())
    t1  = time.mktime(end.timetuple())
    idx = np.where(np.logical_and(t0<tdata,tdata<t1))[0]
    return tdata[idx],xdata[idx],ydata[idx],zdata[idx]

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
    dstr    = ['%Y','%m','%d','%H','%M']
    dsplit  = '-'.join(dstr[:start_time.count('-')+1])
    start   = datetime.strptime(start_time,dsplit)
    dsplit  = '-'.join(dstr[:end_time.count('-')+1])
    end     = datetime.strptime(end_time,dsplit)
    dataset = []
    for date in numpy.arange(start,end,timedelta(minutes=1)):
        date = date.astype(datetime)
        fullpath = rep+'/'+station+'_'+date.strftime("%Y%m%d_%H%M*.h5")
        dataset += glob.glob(fullpath)
    if sample:
        dataset = glob.glob(rep+"/*.h5")
    file_order,data_order = {},{}
    for fname in dataset:
        hfile = h5py.File(fname, "r")
        segfile = file_to_segment(hfile,setname)
        file_order[segfile] = fname
        data_order[segfile] = hfile
    # Extract sample rate from metadata of last read data file
    sample_rate = hfile[setname].attrs["SamplingRate(Hz)"]
    # Generate an ASCII representation of the GPS timestamped segments of time covered by the input data
    seglist = segmentlist(data_order.keys())
    # Sort the segment list
    seglist.sort()
    # Retrieve channel data for all the segments
    xdata = numpy.hstack([data_order[seg][setname][:] for seg in seglist])
    # Time array
    gps_offset = (datetime(1980,1,6)-datetime(1970,1,1)).total_seconds()
    tdata = np.array([seglist[0][0]+gps_offset+j*1/sample_rate for j in range(len(xdata))])
    return tdata,xdata

def file_to_segment(hfile,segname):
    """
    Define length of data segment

    Parameters
    ----------
    hfile : HDF5 file object
      HDF5 data file preloaded with the h5py package
    segname : str
      Attribute name of the metadata to extract.
    """
    attrs = hfile[segname].attrs
    dstr, t0, t1 = attrs["Date"], attrs["t0"], attrs["t1"]
    start_utc = construct_utc_from_metadata(dstr, t0)
    end_utc = construct_utc_from_metadata(dstr, t1)
    return segment(start_utc,end_utc)

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
