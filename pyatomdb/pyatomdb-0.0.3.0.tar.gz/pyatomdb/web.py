import numpy, copy, pickle
import util, atomdb, const, os, atomic, time, spectrum

# get the data!

def get_level_info(lvdat, uplev):
  # Error codes:
  # 1 - level is too low (<0)
  # 2 - level is too high (>N_LEV) but not DR
  
  if uplev < 0:
    return 1
  
  if uplev > len(lvdat):
    return 2
  
  lvdat = {}
  
  lvdat['level']=uplev+1
  lvdat['Electron configuration']=lvdat[uplev]['ELEC_CONFIG']
  lvdat['Energy above ground (eV)']=lvdat[uplev]['ENERGY']
  lvdat['Quantum State']='1s 2p 3s n=test'
  return lvdat


def get_transition_info(uplev, lolev, Z, z1):
  
  # error codes:
  # 1 - no level data for this ion
  # 2 - level is not in this ion
  
  
  # OK: get the data!
  
  lvdat = atomdb.get_data(Z,z1,'LV')
  
  # failure 1:
  if lvdat==False:
    print("No level data for Z,z1 = %i,%i"%(Z,z1))
    return 1
    
  get_level_info(lvdat[1].data, uplev-1)  
