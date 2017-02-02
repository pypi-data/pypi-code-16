import os
import copy
import contextlib
import shutil
import tempfile
import subprocess
import numpy as np
from ase.io import write
from .wave import Wave, Potential
from .read import binread

max_retries=100

def bool2str(x):
    if x: return 'yes'
    else: return 'no'
    
class Multislice:
    
    default_parameters={
        'mode' : 'TEM',
        # model
        'adjust_cell': True,
        'ncell' : (1,1,1),
        'crystal_tilt' : (0,0,0),
        'offset' : (0,0,0),
        'tds' : False,
        'num_tds_runs' : 30,
        'temperature' : 300,
        # image array
        'sampling' : 0.1,
        'size' : None,
        # slicing
        'slice_thickness' : 0.2,
        'slices' : None,
        'center_slices' : False,
        'periodic_xy' : True,
        'periodic_z' : False,
        # microscope
        'energy' : 300,
        'beam_tilt' : (0,0),
        'tilt_back' : False,
        # stem probe
        'defocus' : 0.,
        'Cs' : 0,
        'C5' : 0,
        'astigmatism' : 0,
        'astigmatism_angle' : 0,
        'Cc' : 0,
        'energy_spread' : 0,
        'illumination_angle' : 0,
        'source_size' : 0,
        'beam_current' : 1,
        'dwell_time' : 1,
        'smooth_edge' : True,
        # stem scan window
        'scan_window' : [(0,10,10),(0,10,10)],
        # stem detector
        'detectors' : {'detector1': (70, 200, 0, 0), 'detector2': (0, 40, 0, 0)},
        # output
        'folder' : None,
        'cfg_file' : 'qstem_tmp.cfg',
        'qsc_file' : 'qstem_tmp.qsc',
        'save_every' : False,
        'save_potential' : False,
        'save_projected_potential' : False,
        # other
        'cleanup' : True,
        'potential_3d' : True,
        'propagation_progress_interval' : 10,
        'potential_progress_interval' : 1000,
        'one_time_integration' : True,
        'atom_radius' : 5.0,
        'structure_factors' : 'WK',
        }

    def __init__(self,atoms,**kwargs):
        
        self.parameters=copy.deepcopy(self.default_parameters)
        
        self.parameters.update(**kwargs)
        self.atoms=self.prepare_atoms(atoms)
        self.cell = atoms.get_cell()
        
        if self.parameters['size'] is None:
            if not isinstance(self.parameters['sampling'], (list, tuple)):
                self.parameters['sampling'] = (self.parameters['sampling'],)*2
            
            self.parameters['size'] = (np.round(self.cell[0,0]/self.parameters['sampling'][0]).astype(int),
                                        np.round(self.cell[1,1]/self.parameters['sampling'][1]).astype(int))

        if self.parameters['slices'] is None:
            self.parameters['slices'] = np.round(self.cell[2,2]/self.parameters['slice_thickness']).astype(int)
    
    def run(self):
        self.create_folder()
        
        ret=()
        try:
            self.write_cfg()
            self.write_qsc()
            
            subprocess.call(['stem3', self.parameters['folder']+'\\'+self.parameters['qsc_file']])
            
            if self.parameters['mode'] == 'TEM':
                ret += (self.read_wave(),)
            elif self.parameters['mode'] == 'STEM':
                img_dict={}
                for key in self.parameters['detectors'].keys():
                    array,dx,dy=binread(self.parameters['folder']+'\\'+key+'.img')
                    img_dict[key]=array
                
                ret+=(img_dict,)
            
            if self.parameters['save_potential']:
                ret+=(self.read_potential(),)
            
            if self.parameters['save_projected_potential']:
                ret+=(self.read_projected_potential(),)
            
        finally:
            if self.parameters['cleanup']:
                shutil.rmtree(self.parameters['folder'])
        
        if len(ret)==1:
            return ret[0]
        else:
            return ret
        
    def prepare_atoms(self,atoms_old):
        atoms=atoms_old.copy()
        numbers=atoms.arrays['numbers']
        positions=atoms.arrays['positions']
        atoms.arrays.clear()
        atoms.arrays['numbers']=numbers
        atoms.arrays['positions']=positions
        return atoms
    
    def read_wave(self):
        
        if self.parameters['save_every']:
            num_saved = self.parameters['slices']//self.parameters['save_every']
            array = np.zeros(self.parameters['size']+(num_saved,),dtype=complex)
            for i in range(num_saved):
                array[:,:,i],dx,dy=binread('{0}\wave_{1}.img'.format(self.parameters['folder'],i))
            
            wave = Wave(array,self.parameters['energy'],(dx,dy,self.cell[2,2]/num_saved))
        else:
            array,dx,dy=binread(self.parameters['folder']+'\\'+'wave.img')
            wave = Wave(array,self.parameters['energy'],(dx,dy))
        
        return wave
    
    def read_potential(self):        
        array = np.zeros(self.parameters['size']+(self.parameters['slices'],),dtype=complex)
        for i in range(self.parameters['slices']):
            array[:,:,i],dx,dy=binread('{0}/{1}_{2}.img'.format(self.parameters['folder'],''.join(self.parameters['qsc_file'].split('.')[:1]),i))
        
        return Potential(array,(dx,dy,self.cell[2,2]/self.parameters['slices']))
    
    def read_projected_potential(self):
        array,dx,dy=binread('{0}/{1}_Proj.img'.format(self.parameters['folder'],''.join(self.parameters['qsc_file'].split('.')[:1])))
        
        return Potential(array,(dx,dy,))
    
    def create_folder(self):
        if self.parameters['folder'] is None:
            self.parameters['folder'] = tempfile.mkdtemp()
        elif not os.path.exists(self.parameters['folder']):
            os.makedirs(self.parameters['folder'])
        
        self.parameters['folder'] = os.path.abspath(self.parameters['folder'])
    
    def write_cfg(self):
        write(self.parameters['folder']+'\\'+self.parameters['cfg_file'],self.atoms)
    
    def write_qsc(self,prec=6):
        
        t = 'mode: {0}\n'.format(self.parameters['mode'])
        # model
        t += 'NCELLX: {0}\n'.format(self.parameters['ncell'][0])
        t += 'NCELLY: {0}\n'.format(self.parameters['ncell'][1])
        t += 'NCELLZ: {0}\n'.format(self.parameters['ncell'][2])
        t += 'Crystal tilt X: {0:.6f}\n'.format(self.parameters['crystal_tilt'][0],prec=prec)
        t += 'Crystal tilt Y: {0:.6f}\n'.format(self.parameters['crystal_tilt'][1],prec=prec)
        t += 'Crystal tilt Z: {0:.6f}\n'.format(self.parameters['crystal_tilt'][2],prec=prec)
        t += 'xOffset: {0:.{prec}f}\n'.format(self.parameters['offset'][0],prec=prec)
        t += 'yOffset: {0:.{prec}f}\n'.format(self.parameters['offset'][1],prec=prec)
        t += 'zOffset: {0:.{prec}f}\n'.format(self.parameters['offset'][2],prec=prec)
        t += 'tds: {0}\n'.format(bool2str(self.parameters['tds']))
        t += 'Runs for averaging: {0}\n'.format(self.parameters['num_tds_runs'])
        t += 'temperature: {0:.{prec}f}\n'.format(self.parameters['temperature'],prec=prec)
        # image array
        t += 'resolutionX: {0:.{prec}f}\n'.format(self.cell[0,0]/self.parameters['size'][0],prec=prec)
        t += 'resolutionY: {0:.{prec}f}\n'.format(self.cell[1,1]/self.parameters['size'][1],prec=prec)
        t += 'nx: {0}\n'.format(self.parameters['size'][0])
        t += 'ny: {0}\n'.format(self.parameters['size'][1])
        # slicing
        t += 'slice-thickness: {0:.{prec}f}\n'.format(self.cell[2,2]/self.parameters['slices'],prec=prec)
        t += 'slices: {0}\n'.format(self.parameters['slices'])
        #t += 'slice-thickness: {0}\n'.format(self.cell[2,2]/self.parameters['slices'])
        t += 'center slices: {0}\n'.format(bool2str(self.parameters['center_slices']))
        t += 'periodicXY: {0}\n'.format(bool2str(self.parameters['periodic_xy']))
        t += 'periodicZ: {0}\n'.format(bool2str(self.parameters['periodic_z']))
        # microscope
        t += 'v0: {0:.{prec}f}\n'.format(self.parameters['energy'],prec=prec)
        t += 'Beam tilt X: {0:.{prec}f} deg\n'.format(self.parameters['beam_tilt'][0],prec=prec)
        t += 'Beam tilt Y: {0:.{prec}f} deg\n'.format(self.parameters['beam_tilt'][1],prec=prec)
        t += 'Tilt back: {0}\n'.format(bool2str(self.parameters['tilt_back']))
        # stem probe
        t += 'defocus: {0:.{prec}f}\n'.format(self.parameters['defocus'],prec=prec)
        t += 'Cs: {0:.{prec}f}\n'.format(self.parameters['Cs'],prec=prec)
        t += 'C5: {0:.{prec}f}\n'.format(self.parameters['C5'],prec=prec)
        t += 'astigmatism: {0:.{prec}f}\n'.format(self.parameters['astigmatism'],prec=prec)
        t += 'astigmatism angle: {0:.{prec}f}\n'.format(self.parameters['astigmatism_angle'],prec=prec)
        t += 'Cc: {0:.{prec}f}\n'.format(self.parameters['Cc'],prec=prec)
        t += 'dV/V: {0:.{prec}f}\n'.format(self.parameters['energy_spread'],prec=prec)
        t += 'alpha: {0:.{prec}f}\n'.format(self.parameters['illumination_angle'],prec=prec)
        t += 'source size: {0:.{prec}f}\n'.format(self.parameters['source_size'],prec=prec)
        t += 'beam current: {0:.{prec}f}\n'.format(self.parameters['beam_current'],prec=prec)
        t += 'dwell time: {0:.{prec}f}\n'.format(self.parameters['dwell_time'],prec=prec)
        t += 'smooth: {0}\n'.format(bool2str(self.parameters['smooth_edge']))
        if self.parameters['mode'] == 'STEM':
            # stem scan window
            t += 'scan_x_start: {0:.{prec}f}\n'.format(self.parameters['scan_window'][0][0],prec=prec)
            t += 'scan_x_stop: {0:.{prec}f}\n'.format(self.parameters['scan_window'][0][1],prec=prec)
            t += 'scan_x_pixels: {0}\n'.format(self.parameters['scan_window'][0][2])
            t += 'scan_y_start: {0:.{prec}f}\n'.format(self.parameters['scan_window'][1][0],prec=prec)
            t += 'scan_y_stop: {0:.{prec}f}\n'.format(self.parameters['scan_window'][1][1],prec=prec)
            t += 'scan_y_pixels: {0}\n'.format(self.parameters['scan_window'][1][2])
            # stem detector
            for key, value in self.parameters['detectors'].items():
                t += 'detector: {0:.{prec}f} {1:.{prec}f} {2} {3:.{prec}f} {4:.{prec}f}\n'.format(
                        value[0],value[1],key,value[2],value[3],prec=prec)
        # output
        t += 'Folder: {0}\n'.format(self.parameters['folder'])
        t += 'filename: "{0}"\n'.format(self.parameters['folder']+'\\'+self.parameters['cfg_file'])
        t += 'slices between outputs: {0}\n'.format(self.parameters['save_every'])
        t += 'save potential: {0}\n'.format(bool2str(self.parameters['save_potential']))
        t += 'save projected potential: {0}\n'.format(bool2str(self.parameters['save_projected_potential']))
        # other
        t += 'potential3D: {0}\n'.format(bool2str(self.parameters['potential_3d']))
        t += 'propagation progress interval: {0}\n'.format(self.parameters['propagation_progress_interval'])
        t += 'potential progress interval: {0}\n'.format(self.parameters['potential_progress_interval'])
        t += 'one time integration: {0}\n'.format(bool2str(self.parameters['one_time_integration']))
        t += 'atom radius: {0:.{prec}f}\n'.format(self.parameters['atom_radius'],prec=6)
        t += 'Structure Factors: {0}\n'.format(self.parameters['structure_factors'])
        t += 'bandlimit f_trans: no\n'
        t += 'sequence: 1 1\n'
        
        with open(self.parameters['folder']+'\\'+self.parameters['qsc_file'],'w') as f:
            f.write(t)
