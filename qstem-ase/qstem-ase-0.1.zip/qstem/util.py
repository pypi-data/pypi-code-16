import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import warnings
from ase.data.colors import cpk_colors
from scipy.cluster.hierarchy import linkage,fcluster
from ase import Atoms

def energy2wavelength(v0):
    m0=0.5109989461*10**3 # keV / c**2
    h=4.135667662*10**(-15)*10**(-3) # eV * s
    c=2.99792458*10**8 # m / s
    return h*c/np.sqrt(v0*(2*m0+v0))*10**10
    #return 0.38783/np.sqrt(v0+9.78476*10**(-4)*v0**2)

def focal_spread(Cc,energy,energy_spread,current_stability):
    return Cc*np.sqrt((dv0/v0)**2+2*current_stability**2)

def scherzer(v0,Cs):
    assert Cs > 0.
    return -1.2*np.sqrt(wavelength(v0)*Cs)

def scherzer_point_resolution(v0,Cs):
    assert Cs > 0.
    return 0.6*wavelength(v0)**(3/4.)*Cs**(1/4.)

def spatial_frequencies(shape,sampling,return_polar=False,return_nyquist=False,wavelength=None):
    
    if not isinstance(shape, (list, tuple)):
        shape = (shape,)*2

    if not isinstance(sampling, (list, tuple)):
        sampling = (sampling,)*2
    
    dkx=1/(shape[0]*sampling[0])
    dky=1/(shape[1]*sampling[1])
    
    if shape[0]%2==0:
        kx = np.fft.fftshift(dkx*np.arange(-shape[0]/2,shape[0]/2,1))
    else:
        kx = np.fft.fftshift(dkx*np.arange(-shape[0]/2-.5,shape[0]/2-.5,1))
    
    if shape[1]%2==0:
        ky = np.fft.fftshift(dky*np.arange(-shape[1]/2,shape[1]/2,1))
    else:
        ky = np.fft.fftshift(dky*np.arange(-shape[1]/2-.5,shape[1]/2-.5,1))
    
    ky,kx = np.meshgrid(ky,kx)
    
    k2 = kx**2+ky**2
    
    ret = (kx,ky,k2)
    if return_nyquist:
        knx = 1/(2*sampling[0])
        kny = 1/(2*sampling[1])
        Kx=kx/knx
        Ky=ky/knx
        K2 = Kx**2+Ky**2
        ret += (Kx,Ky,K2)
    if return_polar:
        theta = np.sqrt(k2*wavelength**2)
        phi = np.arctan2(ky,kx)
        ret += (theta,phi)
    
    return ret
    
def atoms_plot(atoms,direction=2,ax=None,scan_window=None,s=40,boundary=1,cluster_dist=None):
 
    if not np.allclose(atoms.get_cell(), np.diag(np.diag(atoms.get_cell()))):
        warnings.warn("Ignoring non-diagonal components of unit cell")
    
    axes=np.delete([0,1,2],direction)
    labels=np.delete(['x','y','z'],direction)
    
    pos=atoms.get_positions()[:,axes]
    direction_sort=np.argsort(-atoms.get_positions()[:,direction])
    pos=pos[direction_sort]
    cell=atoms.get_cell()[axes,axes]
    
    if cluster_dist is not None:
        pos=project_positions(atoms,cluster_dist=cluster_dist)
    
    if ax is None:
        fig, ax = plt.subplots()
    
    if scan_window is not None:
        ax.add_patch(patches.Rectangle((scan_window[0][0],scan_window[1][0]),
                scan_window[0][1]-scan_window[0][0],scan_window[1][1]-scan_window[1][0],
                alpha=0.1,linewidth=None))
        ax.add_patch(patches.Rectangle((scan_window[0][0],scan_window[1][0]),
                scan_window[0][1]-scan_window[0][0],scan_window[1][1]-scan_window[1][0],
                linestyle='dashed',linewidth=1,fill=False))
        dx=(scan_window[0][1]-scan_window[0][0])/scan_window[0][2]
        dy=(scan_window[1][1]-scan_window[1][0])/scan_window[1][2]
        for i in range(1,scan_window[0][2]):
            ax.plot([scan_window[0][0]+i*dx]*2,[scan_window[1][0],scan_window[1][1]],'b-',alpha=.4)
        for i in range(1,scan_window[1][2]):
            ax.plot([scan_window[0][0],scan_window[0][1]],[scan_window[1][0]+i*dy]*2,'b-',alpha=.4)
            
    if cluster_dist is None:
        ax.scatter(pos[:,0],pos[:,1],c=cpk_colors[atoms.get_atomic_numbers()[direction_sort]],s=s)
    else:
        scatter=ax.scatter(pos[:,0],pos[:,1],c=counts,s=s)
        plt.colorbar(scatter)
    
    ax.plot([0,0,cell[0],cell[0],0],[0,cell[1],cell[1],0,0],'k')
    ax.axis('equal')
    ax.set_xlim([-boundary,cell[0]+boundary])
    ax.set_ylim([cell[1]+boundary,-boundary])
    ax.set_xlabel('{0} [Angstrom]'.format(labels[0]))
    ax.set_ylabel('{0} [Angstrom]'.format(labels[1]))
    
    plt.tight_layout()

def project_positions(pos,distance=1):
    if isinstance(pos,Atoms):
        pos=pos.get_positions()[:,:2]
    
    clusters = fcluster(linkage(pos), distance, criterion='distance')
    unique,indices=np.unique(clusters, return_index=True)
    pos=np.array([np.mean(pos[clusters==u],axis=0) for u in unique])
    return pos

def draw_scalebar(pil_img,scale_length,sampling,units='nm',placement=[5,5],margin=3,bar_height=3,
                  font=None,bar_color=0,bg_color=None,formatting='1f',anchor='top left'):
    
    from PIL import ImageDraw
    
    placement=list(placement)
    
    draw = ImageDraw.Draw(pil_img)
    bar_length=scale_length/sampling
    
    text='{0:.{formatting}} {1}'.format(scale_length,units,formatting=formatting)
    text_size=draw.textsize(text, font=font)
    text_spacing=0
    
    bg_height=text_spacing+bar_height+text_size[1]
    
    if anchor=='top right':
        placement[0]-=margin*2+bar_length
    elif anchor=='bottom left':
        placement[1]-=margin*2+bg_height
    elif anchor=='bottom right':
        placement[0]-=margin*2+bar_length
        placement[1]-=margin*2+bg_height
    
    if bg_color is not None:
        draw.rectangle([(placement[0],placement[1]),
                (placement[0]+bar_length+2*margin,placement[1]+bg_height+2*margin)], fill=bg_color)
    
    draw.rectangle([(placement[0]+margin,placement[1]+bg_height-bar_height+margin),
                (placement[0]+bar_length+margin,placement[1]+bg_height+margin)], fill=bar_color)
    
    draw.text((placement[0]+margin+bar_length//2-text_size[0]//2,placement[1]+margin),text,bar_color,font=font)
    
    return pil_img
