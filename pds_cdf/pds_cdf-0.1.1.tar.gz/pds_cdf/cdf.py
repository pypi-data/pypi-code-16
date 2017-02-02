"""
pds_cdf.py

    This is a python script to read PDS4 compliant CDF files
without needing to install the CDF NASA library.  

    Creates a CDF file variable, and then access the variable with 
the commands:

Attribute Inquiry:  attinq( attribute_name )
                    Returns a python dictionary of attribute information
                   
Get Attribute:      attget( attribute_name, entry_number )
                    Returns the value of the attribute at the entry number provided
                   
Variable Inquiry:   varinq( variable_name )
                    Returns a python dictionary of variable information 
                   
Get Variable:       varget( variable_name )
                    Returns a numpy array of all of the variable records


Sample use - 

    import pds_cdf
    swea_cdf_file = pds_cdf.CDFFile('/path/to/swea_file.cdf')
    x = swea_cdf_file.varget("NameOfVariable")

@author: Bryan Harter
"""


import numpy as np

class CDF(object):
    def __init__(self, path):
        
        #READ FIRST INTERNAL RECORDS       
        f = open(path, 'rb')
        self.file = f
        magic_number = f.read(4).hex()
        if magic_number != 'cdf30001':
            print('Not a valid CDF file!')
            return
        compressed_bool = f.read(4).hex()
        self._compressed = not (compressed_bool == '0000ffff')
        if self._compressed:
            print("This procedure does not work on compressed CDF files")
            print("PDS4 requires that the files be uncompressed.")
            return None
        
        cdr_info = self._read_cdr(self.file.tell())
        gdr_info = self._read_gdr(self.file.tell())
        
        #SET GLOBAL VARIABLES
        self._path = path
        self._encoding = cdr_info['encoding']
        self._copyright = cdr_info['copyright']
        self._first_zvariable = gdr_info['first_zvariable']
        self._first_adr = gdr_info['first_adr']
        self._num_zvariable = gdr_info['num_variables']
        self._num_att = gdr_info['num_attributes']

    def _read_cdr(self, byte_loc):
        f = self.file
        f.seek(byte_loc, 0)
        block_size = int.from_bytes(f.read(8),'big')
        section_type = int.from_bytes(f.read(4),'big')
        gdr_loc=int.from_bytes(f.read(8),'big')
        version=int.from_bytes(f.read(4),'big')
        release=int.from_bytes(f.read(4),'big')
        encoding = int.from_bytes(f.read(4),'big')
        
        #FLAG
        #
        #0 The majority of variable values within a variable record. Variable records are described in Chapter 4. Set indicates row-majority. Clear indicates columnmajority.
        #1 The file format of the CDF. Set indicates single-file. Clear indicates multifile.
        #2 The checksum of the CDF. Set indicates a checksum method is used.
        #3 The MD5 checksum method indicator. Set indicates MD5 method is used for the checksum. Bit 2 must be set.
        #4 Reserved for another checksum method. Bit 2 must be set and bit 3 must be clear .\
        
        flag = int.from_bytes(f.read(4),'big')
        nothing1 = int.from_bytes(f.read(4),'big')
        nothing2 = int.from_bytes(f.read(4),'big')
        increment = int.from_bytes(f.read(4),'big')
        nothing3=int.from_bytes(f.read(4),'big')
        nothing4=int.from_bytes(f.read(4),'big')
        
        #Copyright, we will always be here at byte 64.  We know the length of the CDR from the GDR offset,
        #so the length to read is 320-64, or 256
        length_of_copyright = byte_loc+(block_size-64)
        copyright = f.read(length_of_copyright).decode("utf-8")
        
        cdr_info={}
        cdr_info['encoding'] = encoding
        cdr_info['copyright'] = copyright
        
        return cdr_info
    
    def _read_gdr(self, byte_loc):
        f = self.file
        f.seek(byte_loc, 0)
        block_size = int.from_bytes(f.read(8),'big')
        section_type = int.from_bytes(f.read(4),'big')
        first_rvariable = int.from_bytes(f.read(8),'big', signed=True)
        first_zvariable = int.from_bytes(f.read(8),'big', signed=True)
        first_adr = int.from_bytes(f.read(8),'big', signed=True)
        eof = int.from_bytes(f.read(8),'big', signed=True)
        num_rvariable = int.from_bytes(f.read(4),'big', signed=True)
        num_att = int.from_bytes(f.read(4),'big', signed=True)
        rMaxRec = int.from_bytes(f.read(4),'big', signed=True)
        num_rdim = int.from_bytes(f.read(4),'big', signed=True)
        num_zvariable = int.from_bytes(f.read(4),'big', signed=True)
        first_unused = int.from_bytes(f.read(8),'big', signed=True)
        nothing1 = int.from_bytes(f.read(4),'big', signed=True)
        #YYYMMDD form
        leapsecondlastupdate = int.from_bytes(f.read(4),'big', signed=True)
        nothing2 = int.from_bytes(f.read(4),'big', signed=True)
        
        #rDimSizes, depends on Number of dimensions for r variables
        #A bunch of 4 byte integers in a row.  Length is (size of GDR) - 84
        #In this case. there is nothing
        rdim_sizes=[]
        for _ in range(0, num_rdim):
            rdim_sizes.append(int.from_bytes(f.read(4),'big', signed=True))
        
        gdr_info = {}
        gdr_info['first_zvariable'] = first_zvariable
        gdr_info['first_adr'] = first_adr
        gdr_info['num_variables'] = num_zvariable
        gdr_info['num_attributes'] = num_att 
        
        return gdr_info
    
    def _read_adr(self, byte_loc):
        f = self.file
        f.seek(byte_loc, 0)
        block_size = int.from_bytes(f.read(8),'big')
        #Type of internal record
        section_type = int.from_bytes(f.read(4),'big')
        
        #Position of next ADR
        next_adr_loc = int.from_bytes(f.read(8),'big', signed=True)
        
        #Position of next agrADR
        position_next_gr_entry = int.from_bytes(f.read(8),'big', signed=True)
        
        #Scope, 1 is global 2 is variable
        scope = int.from_bytes(f.read(4),'big', signed=True)
        
        #This attributes number
        num = int.from_bytes(f.read(4),'big', signed=True)
        
        #Number of grEntries
        num_gr_entry=int.from_bytes(f.read(4),'big', signed=True)
        
        #Maximum number of grEntries
        MaxEntry=int.from_bytes(f.read(4),'big', signed=True)
        
        #Literally nothing
        empty1 = int.from_bytes(f.read(4),'big', signed=True)
        
        #File offset to first Attribute zEntry Descriptor Record
        position_next_z_entry =int.from_bytes(f.read(8),'big', signed=True)
        #Number of z entries
        num_z_entry=int.from_bytes(f.read(4),'big', signed=True)
        
        #Maximum number of z entries
        MaxZEntry= int.from_bytes(f.read(4),'big', signed=True)
        
        #Literally nothing
        empty2 = int.from_bytes(f.read(4),'big', signed=True)
        
        #Name
        name = str(f.read(256).decode("utf-8"))
        name = name.replace('\x00', '')
        
        #Build the return dictionary
        return_dict = {}
        #return_dict['section_type'] = section_type
        return_dict['scope'] = scope
        return_dict['next_adr_location'] = next_adr_loc
        return_dict['attribute_number'] = num
        return_dict['num_gr_entry'] = num_gr_entry 
        return_dict['max_gr_entry'] = MaxEntry
        return_dict['num_z_entry'] = num_z_entry 
        return_dict['max_z_entry'] = MaxZEntry
        return_dict['first_z_entry'] = position_next_z_entry
        return_dict['first_gr_entry'] = position_next_gr_entry 
        return_dict['name'] = name
        
        return return_dict

    def _read_aedr(self, byte_loc):
        f = self.file
        f.seek(byte_loc, 0)
        block_size = int.from_bytes(f.read(8),'big')
        section_type = int.from_bytes(f.read(4),'big')     
        next_aedr = int.from_bytes(f.read(8),'big', signed=True)
        
        #Attribute number, should be zero for first one
        att_num = int.from_bytes(f.read(4),'big', signed=True)
        
        #Data type of this attribute
        data_type = int.from_bytes(f.read(4),'big', signed=True)
        
        #Variable number
        entry_num = int.from_bytes(f.read(4),'big', signed=True)
        
        #Number of elements
        #Length of string if string, otherwise its the number of numbers
        num_elements = int.from_bytes(f.read(4),'big', signed=True)

        #Literally nothing
        nothing1 = int.from_bytes(f.read(4),'big', signed=True)
        nothing2 = int.from_bytes(f.read(4),'big', signed=True)
        nothing3 = int.from_bytes(f.read(4),'big', signed=True)
        nothing4 = int.from_bytes(f.read(4),'big', signed=True)
        nothing5 = int.from_bytes(f.read(4),'big', signed=True)
        
        #Always will have 56 bytes before the data
        byte_stream = f.read(block_size - 56)
        entry = self._read_data(byte_stream, data_type, num_elements)
        
        return next_aedr, entry 
             
    def _read_vdr(self, byte_loc):
        f = self.file
        f.seek(byte_loc, 0)
        block_size = int.from_bytes(f.read(8),'big')
        
        #Type of internal record
        section_type = int.from_bytes(f.read(4),'big')
        next_vdr = int.from_bytes(f.read(8),'big', signed=True)
    
        data_type = int.from_bytes(f.read(4),'big', signed=True)
        
        max_rec = int.from_bytes(f.read(4),'big', signed=True)
        
        next_vxr = int.from_bytes(f.read(8),'big', signed=True)
        last_vxr = int.from_bytes(f.read(8),'big', signed=True)
        
        flags = int.from_bytes(f.read(4),'big', signed=True)
        
        flag_bits = '{0:032b}'.format(flags)
        
        record_varaince_bool = (flag_bits[31]=='1') 
        pad_bool = (flag_bits[30]=='1')
        compression_bool = (flag_bits[29]=='1') 
        
        
        sparse = int.from_bytes(f.read(4),'big', signed=True)
        nothing1 = int.from_bytes(f.read(4),'big', signed=True)
        nothing2 = int.from_bytes(f.read(4),'big', signed=True)
        nothing3 = int.from_bytes(f.read(4),'big', signed=True)
    
        num_elements = int.from_bytes(f.read(4),'big', signed=True)
        
        var_num = int.from_bytes(f.read(4),'big', signed=True)
        
        CPRorSPRoffset = int.from_bytes(f.read(8),'big', signed=True)
        
        blocking_factor = int.from_bytes(f.read(4),'big', signed=True)
        
        name = str(f.read(256).decode("utf-8"))
        name = name.replace('\x00', '')
        
        #Will not be present if an "r" variable
        num_dims = int.from_bytes(f.read(4),'big', signed=True)
        
        zdim_sizes = []
        for _ in range(0, num_dims):
            zdim_sizes.append(int.from_bytes(f.read(4),'big', signed=True))
        zdim_varys = []
        for _ in range(0, num_dims):
            zdim_varys.append(int.from_bytes(f.read(4),'big', signed=True))
        
        #Only set if pad value is in the flags
        if pad_bool:
            byte_stream = f.read((block_size - (f.tell() - byte_loc)))
            pad_data = self._read_data(byte_stream, data_type, num_elements)
        
        
        return_dict = {}
        return_dict['data_type'] = data_type
        #return_dict['section_type'] = section_type
        return_dict['next_vdr_location'] = next_vdr
        return_dict['variable_number'] = var_num
        return_dict['next_vxr'] = next_vxr
        return_dict['last_vxr'] = last_vxr
        return_dict['max_records'] = max_rec
        #return_dict['blocking_factor'] = blocking_factor
        return_dict['name'] = name
        return_dict['num_dims'] = num_dims
        return_dict['dim_sizes'] = zdim_sizes
        #return_dict['dim_varys'] = zdim_varys
        return_dict['pad'] = pad_data
        
        return return_dict
            
    def _read_vxr(self, byte_loc):
        f = self.file
        f.seek(byte_loc, 0)
        block_size = int.from_bytes(f.read(8),'big')
        
        #Type of internal record
        section_type = int.from_bytes(f.read(4),'big')
        next_vxr_pos = int.from_bytes(f.read(8),'big', signed=True)
    
        num_ent = int.from_bytes(f.read(4),'big', signed=True)
        num_ent_used = int.from_bytes(f.read(4),'big', signed=True)
    
        rec_num_start = []
        rec_num_end = []
        rec_offset = []
        
        for _ in range(0, num_ent):
            rec_num_start.append(int.from_bytes(f.read(4),'big', signed=True))
        for _ in range(0, num_ent):
            rec_num_end.append(int.from_bytes(f.read(4),'big', signed=True))
        for _ in range(0, num_ent):
            rec_offset.append(int.from_bytes(f.read(8),'big', signed=True))
        
        #Build the return dictionary
        return_dict = {}
        return_dict['next_vxr'] = next_vxr_pos
        return_dict['num_entries_used'] = num_ent_used
        return_dict['rec_num_start'] = rec_num_start
        return_dict['rec_num_end'] = rec_num_end 
        return_dict['rec_offset'] = rec_offset
            
        return return_dict
         
    def _read_vvr(self, vdr_dict, vxr_dict):
        
        #THIS IS CURRENTLY WRITTEN TO ASSUME THE CDF FILE IS PDS4 COMPLIANT
        f = self.file
        f.seek(vxr_dict['rec_offset'][0], 0)
        block_size = int.from_bytes(f.read(8),'big')
        section_type = int.from_bytes(f.read(4),'big')
        bytes = f.read(block_size-12)
        
        
        
        x = self._read_data(bytes, vdr_dict['data_type'], vdr_dict['max_records']+1, dimensions=vdr_dict['dim_sizes'])
        
        return x

    def _read_data(self, bytes, data_type, num_elements, dimensions=None):
        ##DATA TYPES
        #
        #1 - 1 byte signed int
        #2 - 2 byte signed int
        #4 - 4 byte signed int
        #8 - 8 byte signed int
        #11 - 1 byte unsigned int
        #12 - 2 byte unsigned int
        #14 - 4 byte unsigned int
        #41 - same as 1
        #21 - 4 byte float
        #22 - 8 byte float (double)
        #44 - same as 21
        #45 - same as 22
        #31 - double representing milliseconds
        #32 - 2 doubles representing milliseconds
        #33 - 8 byte signed integer representing nanoseconds from J2000
        #51 - signed character
        #52 - unsigned character
        
        
        #NEED TO CONSTRUCT DATA TYPES FOR ARRAYS
        #
        #SOMETHING LIKE:
        #
        #  dt = np.dtype('>(48,4,16)f4')
        
        #TODO:
        #Do += for all data_types
        
        squeeze_needed = False
        dt_string = '>'
        if dimensions!=None:
            if (len(dimensions) == 1):
                dimensions.append(1)
                squeeze_needed = True
            dt_string += "(" 
            count = 0
            for dim in dimensions:
                count += 1
                dt_string += str(dim)
                if count < len(dimensions):
                    dt_string += ','
            dt_string += ")"
        
        if (data_type == 1) or (data_type == 41):
            dt_string += 'i1'
            dt = np.dtype(dt_string)
            ret = np.frombuffer(bytes, dtype=dt, count=num_elements)
            ret.setflags("WRITEABLE")
        elif data_type == 2:
            dt_string += 'i2'
            dt = np.dtype(dt_string)
            ret = np.frombuffer(bytes, dtype=dt, count=num_elements)
            ret.setflags("WRITEABLE")
        elif data_type == 4:
            dt_string += 'i4'
            dt = np.dtype(dt_string)
            ret = np.frombuffer(bytes, dtype=dt, count=num_elements)
            ret.setflags("WRITEABLE")
        elif (data_type == 8) or (data_type == 33):
            dt_string += 'i8'
            dt = np.dtype(dt_string)
            ret = np.frombuffer(bytes, dtype=dt, count=num_elements)
            ret.setflags("WRITEABLE")
        elif data_type == 11:
            dt_string += 'u1'
            dt = np.dtype(dt_string)
            ret = np.frombuffer(bytes, dtype=dt, count=num_elements)
            ret.setflags("WRITEABLE")
        elif data_type == 12:
            dt_string += 'u2'
            dt = np.dtype(dt_string)
            ret = np.frombuffer(bytes, dtype=dt, count=num_elements)
            ret.setflags("WRITEABLE")
        elif data_type == 14:
            dt_string += 'u4'
            dt = np.dtype(dt_string)
            ret = np.frombuffer(bytes, dtype=dt, count=num_elements)
            ret.setflags("WRITEABLE")
        elif (data_type == 21) or (data_type == 44):
            dt_string += 'f'
            dt = np.dtype(dt_string)
            ret = np.frombuffer(bytes, dtype=dt, count=num_elements)
            ret.setflags("WRITEABLE")
        elif (data_type == 22) or (data_type == 45) or (data_type == 31):
            dt_string += 'd'
            dt = np.dtype(dt_string)
            ret = np.frombuffer(bytes, dtype=dt, count=num_elements)
            ret.setflags("WRITEABLE")
        elif data_type ==52 or data_type == 51:
            ret = str(bytes[0:num_elements])
        else:
            print("NOT IMPLEMENTED!!!")
        
        if squeeze_needed:
            ret = np.squeeze(ret)
        
        return ret
   

    def attinq(self, attribute = None):
        position = self._first_adr
        if isinstance(attribute, str):
            for _ in range(0, self._num_att):
                adr_info = self._read_adr(position)
                if adr_info['name'] == attribute:
                    return adr_info
                position = adr_info['next_adr_location']
            print("No attribute by that name")
            return
        elif isinstance(attribute, int):
            for _ in range(0, attribute):
                adr_info = self._read_adr(position)
                position = adr_info['next_adr_location']
            return adr_info
        else:
            print("Please set attribute keyword equal to the name or number of an attribute")
            for _ in range(0, self._num_att):
                adr_info = self._read_adr(position)
                print("NAME: " + adr_info['name'])
                position=adr_info['next_adr_location']
                
    def attget(self, attribute = None, entry_num = None):
        
        #Starting position
        position = self._first_adr
        
        #Check if an attribute string was given
        if isinstance(attribute, str):
            for _ in range(0, self._num_att):
                adr_info = self._read_adr(position)
                if adr_info['name'] == attribute:
                    #Check if valid entry number was given
                    if adr_info['scope'] == 1:
                        num_entry = 'num_gr_entry'
                        first_entry = 'first_gr_entry'
                    else:
                        num_entry = 'num_z_entry'
                        first_entry = 'first_z_entry'
                    if entry_num >= adr_info[num_entry]:
                        print('There are not this many entries for this attribute')
                        return
                    position = adr_info[first_entry]
                    for _ in range(0, entry_num+1):
                        pos, entry = self._read_aedr(position)
                        position = pos 
                    return entry   
                position = adr_info['next_adr_location']
            print("No attribute by that name")
            return
        
        #Check if an attribute number was given
        elif isinstance(attribute, int):
            for _ in range(0, attribute):
                adr_info = self._read_adr(position)
                position = adr_info['next_adr_location']
            if adr_info['scope'] == 1:
                num_entry = 'num_gr_entry'
                first_entry = 'first_gr_entry'
            else:
                num_entry = 'num_z_entry'
                first_entry = 'first_z_entry'
            #Check if valid entry was given
            if entry >= adr_info[num_entry]:
                print('There are not this many entries for this attribute')
                return
            position = adr_info[first_entry]
            for _ in range(0, entry+1):
                pos, entry = self._read_aedr(position)
                position = pos 
            return entry
        else:
            print("Please set attribute keyword equal to the name or number of an attribute")
            for _ in range(0, self._num_att):
                adr_info = self._read_adr(position)
                print(adr_info['name'])
                position=adr_info['next_adr_location']
    
    def varinq(self, variable = None):
        position = self._first_zvariable
        if isinstance(variable, str):
            for _ in range(0, self._num_zvariable):
                vdr_info = self._read_vdr(position)
                if vdr_info['name'] == variable:
                    return vdr_info
                position = vdr_info['next_vdr_location']
            print("No attribute by that name")
            return
        elif isinstance(variable, int):
            for _ in range(0, variable):
                vdr_info = self._read_vdr(position)
                position = vdr_info['next_vdr_location']
            return vdr_info
        else:
            print("Please set variable keyword equal to the name or number of an variable")
            for _ in range(0, self._num_zvariable):
                vdr_info = self._read_vdr(position)
                print("NAME: " + vdr_info['name'])
                position=vdr_info['next_vdr_location']
                
    def varget(self, variable = None):
        position = self._first_zvariable
        if isinstance(variable, str):
            for _ in range(0, self._num_zvariable):
                vdr_info = self._read_vdr(position)
                if vdr_info['name'] == variable:
                    vxr_info = self._read_vxr(vdr_info['next_vxr'])
                    data = self._read_vvr(vdr_info, vxr_info)
                    #Change the data to little endian before returning 
                    if (data.dtype.byteorder == '>'):
                        data = data.byteswap().newbyteorder()
                    return data
                position = vdr_info['next_vdr_location']
            print("No attribute by that name")
            return
        elif isinstance(variable, int):
            for _ in range(0, variable):
                vdr_info = self._read_vdr(position)
                position = vdr_info['next_vdr_location']
            x = self._read_vxr(vdr_info['next_vxr'])
            y = self._read_vvr(x['rec_offset'][0])
            #Change the data to little endian before returning 
            if (y.dtype.byteorder == '>'):
                    y = y.byteswap().newbyteorder()
            return y
        else:
            print("Please set variable keyword equal to the name or number of an variable")
            for _ in range(0, self._num_zvariable):
                vdr_info = self._read_vdr(position)
                print("NAME: " + vdr_info['name'])
                position=vdr_info['next_vdr_location']