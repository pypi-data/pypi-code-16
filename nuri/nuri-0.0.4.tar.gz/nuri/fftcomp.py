from .settings import *
from .extract  import *

class fftcomp(object):
    
    def showhelp(self):
    
        print ""
        print "-------------------------------------------------------------------------"
        print ""
        print "description:"
        print ""
        print "  This operation will plot the Fourier transform of given time series."
        print "  The time series and FFT are shown interactively so the user can select"
        print "  a desired time slot and get the FFT from that region."
        print ""
        print "required arguments:"
        print ""
        print "   --start          Starting date to retrieve data from."
        print "   --end            Ending date to retrieve data from."
        print "   --station        Station name"
        print ""
        print "optional arguments:"
        print ""
        print "   --discard        Discard first selected seconds"
        print "   --fmin           Minimum frequency to display"
        print "   --fmax           Maximum frequency to display"
        print "   --nogps          No GPS provided, create time array using sample rate"
        print "   --orientation    Orientation to extract if single (all by default)"
        print "   --path           Custom repository where data are stored."
        print "   --sample         Specify the data to be field sample, not regular."
        print "   --scale          Rescale y axis"
        print "   --unit           Time unit for plot."
        print ""
        print "example:"
        print ""
        print "  nuri fftcomp --start 2017-03-09-15-58 --end 2017-03-10 \ "
        print "               --path /Users/vincent/ASTRO/data/others/sample1_background_noise/ \ "
        print "               --start2 2017-03-09-16-2 --end2 2017-03-09-16-4 \ "
        print "               --path2 /Users/vincent/ASTRO/data/others/sample2_magnet_test1/ \ "
        print "               --station magnet --sample --unit secs --nogps \ "
        print "               --discard 1 --fmin 1 --down 12 --seaborn"
        print ""
        print "-------------------------------------------------------------------------"
        print ""
        quit()

    def __init__(self):
        
        if '--help' in sys.argv or '-h' in sys.argv:
            self.showhelp()
        elif setup.station==None or setup.start==None or setup.end==None:
            print '\nERROR: station or start or end dates not specified...\n'
            quit()
            
        t1,x1,y1,z1,f1,fft_x1,fft_y1,fft_z1 = self.get_data(setup.start,setup.end,setup.path)
        t2,x2,y2,z2,f2,fft_x2,fft_y2,fft_z2 = self.get_data(setup.start2,setup.end2,setup.path2)
        self.plot_data(t1,x1,t2,x2,f1,fft_x1,f2,fft_x2,'X')
        self.plot_data(t1,y1,t2,y2,f1,fft_y1,f2,fft_y2,'Y')
        self.plot_data(t1,z1,t2,z2,f1,fft_z1,f2,fft_z2,'Z')

    def plot_data(self,t1,y1,t2,y2,f1,fft_y1,f2,fft_y2,direction):
        # Initialise axis
        fig = figure(figsize=(15,10))
        plt.subplots_adjust(left=0.07,right=0.95,bottom=0.1,top=0.95,hspace=0.2,wspace=0.05)
        # Plot time series
        ax1 = subplot(221)
        ax1.plot(t1,y1)
        ax1.set_xlabel('Time [%s]'%setup.unit)
        ax1.set_ylabel('Magnetic field [uT]')
        ax1.set_title('Without Magnet - %s direction'%direction)
        # Plot time series
        ax2 = subplot(222,sharex=ax1,sharey=ax1)
        ax2.plot(t2,y2)
        ax2.set_xlim(t2[0],t2[-1])
        ax2.set_xlabel('Time [%s]'%setup.unit)
        ax2.set_title('With Magnet - %s direction'%direction)
        plt.setp(ax2.get_yticklabels(),visible=False)
        # Plot FFT for x direction
        ax3 = subplot(223)
        ax3.semilogy(f1,fft_y1)
        ax3.set_xlabel('Frequency [Hz]')
        ax3.set_ylabel('|Y(f)|')
        # Plot FFT for y direction
        ax4 = subplot(224,sharex=ax3,sharey=ax3)
        ax4.semilogy(f2,fft_y2)
        ax4.set_xlim(1,f2[-1])
        ax4.set_xlabel('Frequency [Hz]')
        plt.setp(ax4.get_yticklabels(),visible=False)
        # Save figure
        plt.savefig('%s-fft-%s.png'%(setup.station,direction))
        plt.close(fig)

    def get_data(self,start,end,path):
    
        t,x,y,z = magfield(start,end,rep=path)
        # Discard selected data
        t = t[setup.rate*setup.discard:]
        x = x[setup.rate*setup.discard:]
        y = y[setup.rate*setup.discard:]
        z = z[setup.rate*setup.discard:]
        # Decimate magnetic field data to 1 sample/second
        down_factor = [setup.down] if setup.down<13 else \
                      [11,9,4] if setup.down==396 else [11,10,9,4]
        for i in down_factor:
            x = signal.decimate(x,i,zero_phase=True)
            y = signal.decimate(y,i,zero_phase=True)
            z = signal.decimate(z,i,zero_phase=True)
        # Extract time every 3960 sample
        l = len(t)/setup.down
        l = l if l*setup.down==len(t) else l+1
        t = [t[n*setup.down] for n in range(l)]
        if setup.nogps: t = [float(n)*setup.down/setup.rate for n in range(len(x))]
        # Convert every timing points to scale (hr,min,sec) units
        s = 1. if setup.unit=='secs' else 60. if setup.unit=='mins' else 3600.
        t = [(t[i]-t[0])/s for i in range(len(t))]
        # Create FFT of data
        N = len(t)
        T = 1.0 / (setup.rate/setup.down)
        f = np.linspace(0.0, 1.0/(2.0*T), N/2)
        i1 = abs(f-setup.fmin).argmin()
        i2 = len(f) if setup.fmax==None else abs(f-setup.fmax).argmin()
        f = f[i1:i2]
        fft_x = 2.0/N * np.abs(fft(x)[:N//2])[i1:i2]
        fft_y = 2.0/N * np.abs(fft(y)[:N//2])[i1:i2]
        fft_z = 2.0/N * np.abs(fft(z)[:N//2])[i1:i2]
        return t,x,y,z,f,fft_x,fft_y,fft_z
