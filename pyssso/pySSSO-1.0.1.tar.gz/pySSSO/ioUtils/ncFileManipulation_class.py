#!/usr/bin/env python


#-------------
# Load modules
#-------------
from netCDF4 import Dataset
import numpy as np                         # Numpy import
import sys

class ncFileCreate:
   """
     Provides methods to create a netCDF file and
     add variables into it.
   """

   def __init__(self, *args, **kwargs):
      """
        Open a netCDF file.

        Arguments:
           file_name (required)
           Keyword arguments (optional):
           summary = True, if you want a full report of the file contents

         Returns:
            a netcdf dataset instance
      """

      self.file_name = args[0]
      mode   = kwargs.get('mode')
      format = kwargs.get('format')

      if mode:
         if format:
            self.fid = Dataset(self.file_name, mode, format=format)
         else:
            self.fid = Dataset(self.file_name, mode)
      else:
         if format:
            self.fid = Dataset(self.file_name, mode='w', format=format)
         else:
            self.fid = Dataset(self.file_name, mode='w')

      print 'Successfully opened the file: ', self.file_name
      print 'The file format is: ', self.fid.file_format
      print 

      if kwargs.get('summary'):
         self._print_dataset_info()

   #--------------------
   # Add file attributes
   #--------------------
   
   def add_file_attributes(self, **keywords):
       # Add variable attributes 
       for kw in keywords.keys():
           self.fid.setncattr(kw, keywords[kw])
           #if (kw == 'Description'): self.fid.Description = keywords[kw]
           #if (kw == 'Source'):           self.fid.Source = keywords[kw]
           #if (kw == 'Title'):             self.fid.Title = keywords[kw]
           #if (kw == 'History'):         self.fid.History = keywords[kw]
           #if (kw == 'Institution'): self.fid.Institution = keywords[kw]
           #if (kw == 'References'):   self.fid.References = keywords[kw]
           #if (kw == 'Comment'):         self.fid.Comment = keywords[kw]
           #if (kw == 'Conventions'): self.fid.Conventions = keywords[kw]

   #---------------
   # Close the file
   #---------------

   def close_file(self):
       print "Closing the file: ", self.file_name
       self.fid.close()

   #------------------------------------------
   # Function to define Lat/Lon/Lev dimensions
   #------------------------------------------

   def define_dimension(self, dim_name, type, num_points=None, **keywords):
       """
         Performs the following:
           - Define a dimension (lat/lon/lev/time)
           - Create the dimension and 
           - Add dimension attributes.
       
         Required arguments:
            dim_name:   name of the dimension ('lat' for instance)
            type:       type of the dimension ('i4', 'f4', etc.)
            num_points: number of grid points along the dimension
                        Is equal to None if unlimitted die=mension
         Optional arguments (**keywords):
            units    = ...   units of the dimension
            calendar = ...   type of calendar to employ
            ...
       
         Return value:
            ncvar: reference to the dimension in the file.
       """
       # Define the dimension
       var = self.fid.createDimension(dim_name, num_points)
   
       # Create the variable
       ncvar = self.fid.createVariable(dim_name, type, (dim_name,))
   
       # Set variable attributes 
       for kw in keywords.keys():
           ncvar.__setattr__(kw, keywords[kw])

       return ncvar

   #-----------------------------------------------
   # Function to define the time and its attributes
   #-----------------------------------------------
   def define_time(self, time_name,
                   num = None, 
                   units = 'hours since 0001-01-01 00:00:00.0',
                   calendar = 'gregorian'):
       
       """
         Defines the time dimension, creates it and adds attribute.
       
         The arguments are:
            time_name: name of the time dimension
            units:     units of the time dimension
            calendar:  type of calendar to employ
       
         Return value:
            nctime: reference to the time dimension in the file.
       """
       # Define time dimension
       time = self.fid.createDimension(time_name, mode)

       nctime = self.fid.createVariable(time_name,'f8',(time_name,))
       nctime.units = units
       nctime.calendar = calendar
   
       return nctime
   
   #----------------------------------------------
   # Function to add a variable and its attributes
   #----------------------------------------------
   
   def define_var(self, var_name, type, dims = ('lat','lon',),
                  **keywords):
       """
         Performs the following:
           - Create a variable
           - Add variable attributes.
       
         Required arguments:
            var_name:   name of the variable
            type:       type of the variable
            dims:       dimensions of the variable
                        should be with respect to the dimensions
                        previously defined (('lat','lon',))
         Optional arguments (**keywords):
            units         = ... units of the variable
            long_name     = ... long name of the variable 
            missing_value = ... missing value
            ....
       
         Return value:
            ncvar: reference to the dimension in the file.
       """
   
       # Create variable
       ncvar = self.fid.createVariable(var_name, type, dims)
  
       # Add variable attributes 
       # if (kw == 'units') the code will do  ncvar.units = keywords[kw]
       for kw in keywords.keys():
           ncvar.__setattr__(kw, keywords[kw])
   
       return ncvar
   
   #------------------------------------------
   # Function to scale and offset a variable
   #------------------------------------------
   
   def scale_offset_var(self, var_name, scale=1.0, offset=0.0):
       """
           Given:
              - var_name:  an existing variable name
              - scale:     scale
              - offset:    offset
       
           this function will perform the operation:
               var_name = scale*var_name + offset
       """
       # Extract and update the variable
       var1 = self.fid.variables[var_name][:]
       var2 = scale*var1[:] + offset
       var1[:] = var2

   #---------------------------------------------------------------
   # Function to create a new variable by adding existing variables
   #---------------------------------------------------------------
   def create_new_var(self, var_name, *args):
       """
         Creates a new variable in the file.
         The new variable is equal to the sum of existing variables
         which names are passed through *args
       """
       numVars = len(args)
       if (numVars == 0):
          print "Cannot perform the operation in: ", self.file_name
       else:
          var = self.fid.variables[args[0]]
          dims = var.dimensions
          new_var = self.define_var(var_name, var.dtype, var.dimensions)
          for name in var.ncattr(): 
              new_var.__setattr__(name, var.getncattr(name)) 

          new_var = var[:]
          for i in range(1, numVars):
              var = self.fid.variables[args[i]]
              new_var += var[:]

   #------------------------------------------------
   # Function to print a summary of the file content
   #------------------------------------------------
   def dataset_info(self):
        _print_dimensions_info(self)
        _print_dataset_info

   def _print_dataset_info(self):
       print "----------------------------"
       print "Summary of the file content:"
       print "----------------------------"
       print self.fid
       print
       print "   List of variables , dimensions and types:"
       for var in self.fid.variables:
           if (var not in self.fid.dimensions.keys()):
              print "        ", var+":", self.fid.variables[var].dimensions, self.fid.variables[var].dtype
       print
       print "   Global attributes:"
       for name in self.fid.ncattrs():
           print "        ", name, " = ", getattr(self.fid, name)
       print

   #------------------------------------------------
   # Function to print a the dimensions in the file
   #------------------------------------------------
   def _print_dimensions_info(self):
       print "Dimensions in the file: ", self.file_name
       print "_____________________________________"
       print "   Name          Length   isUnlimited"
       print "-------------------------------------"
       for dimname, dimobj in self.fid.dimensions.iteritems():
           print "   %-13s %-8i %-s" %(dimname, len(dimobj), dimobj.isunlimited())
       print



