# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 14:06:35 2017

@author: Krounet
e-mail:krounet@gmail.com
"""
from numpy import polyfit,poly1d,angle,unwrap,abs,conjugate,ones,pi,array,arange,take,sum,exp,mean,cumsum,concatenate,interp,hanning,hamming,blackman,real,complex128,complex64
from numpy.fft import fft,ifft




class SigTempTreatment:
	"""Python Class with functionnalities to do some treatments on temporal signals
     time : time base
     amplitude : amplitude of the signal"""

	def __init__(self,time=[],amplitude=[]):
		
		self.time=time
		self.amplitude=amplitude
		
		
		
			


	def calcfft(self,dfreq,freqmax,choice):
		"""it's a fft function
          dfreq : delta frequencies
          freqmax : frequencie maximum
          choice = 1=> apply df into the fft calculation
          
          this function return a dictionnary with these keys :
          
          frequencies : list of the frequencies obtained after calculation
          fft : list of the amplitudes obtained after calculation
          nbf : number of points
          df : delta frequency"""
		if type(self.time) and type(self.amplitude) is not type(array([])):
			self.time=array(self.time)
			self.amplitude=array(self.amplitude)
			
		nbt=len(self.amplitude)
		dt=(self.time[1]-self.time[0])
		if choice==1 :
			taillefft=int(1/(dt*dfreq))
			if taillefft<=nbt :
				resultFFT=fft(self.amplitude)
			else :
				resultFFT=fft(self.amplitude,n=taillefft)
		else :
			resultFFT=fft(self.amplitude)
		frequencies=arange(len(resultFFT))/(len(resultFFT)*dt)
		#resultFFT=resultFFT*numpy.exp(-2j*numpy.pi*frequence*time[0])*dt
		resultFFT=resultFFT*dt
		nbf=len(resultFFT)
		df=frequencies[1]-frequencies[0]
		Indicelimitefh=int(freqmax/df)
		resultFFT=take(resultFFT,range(Indicelimitefh))
		frequencies=take(frequencies,range(Indicelimitefh))
		nbf=len(resultFFT)
		df=frequencies[1]-frequencies[0]
		return dict({'frequencies':frequencies,'fft':resultFFT,'nbf':nbf,'df':df})

	def calctfd(self,fmin,fmax,nbf):
		
		"""It's a TFD function
          fmin : frequency min of the TFD calculation
          fmax : frequency max of the TFD calculation
          nbf : number of frequencies points
          
          this function return a dictionnary with these keys :
          
          frequencies : list of the frequencies obtained after calculation
          TFD : list of the amplitudes obtained after calculation
          nbf : number of points
          df : delta frequency
          """

		if type(self.time) and type(self.amplitude) is not type(array([])):
			self.time=array(self.time)
			self.amplitude=array(self.amplitude)
			
		
		dt=(self.time[1]-self.time[0])
		df=(fmax-fmin)/(nbf-1)
		iii=arange(nbf)
		tabfrequencies=fmin+iii*df
		tabresult=array([sum(self.amplitude*dt*exp(-2j*pi*(fmin+jjj*df)*self.time)) for jjj in range(nbf)])
		return dict({'frequencies':tabfrequencies,'TFD':tabresult,'nbf':nbf,'df':df})

	def calcintegrale(self):
		"""It's an Integral calculation
  
          this function return a dictionnary with these keys :
          
          time : time base
          amplitude : amplitudes obtained after calculation
          """

		if type(self.time) and type(self.amplitude) is not type(array([])):
			self.time=array(self.time)
			self.amplitude=array(self.amplitude)			
		
		dt=(self.time[1]-self.time[0])  
		offset=mean(self.amplitude)
		self.amplitude=self.amplitude-offset
		tabresult=cumsum(self.amplitude)*dt
		return dict({'time':self.time,'amplitude':tabresult})

	def calcderivee(self):
		"""It's a Derivative calculation
          
          this function return a dictionnary with these keys :
          
          time : time base
          amplitude : amplitudes obtained after calculation"""

		if type(self.time) and type(self.amplitude) is not type(array([])):
			self.time=array(self.time)
			self.amplitude=array(self.amplitude)			
		
		dt=(self.time[1]-self.time[0])  
		tab1=concatenate([[0],take(self.amplitude,range(0,len(self.amplitude)-1))])
		tab2=concatenate([take(self.amplitude,range(1,len(self.amplitude))),[0]])
		tabresult=(take(tab2-tab1,range(len(self.amplitude))))/(2*dt)
		return dict({'time':self.time,'amplitude':tabresult})

	def calcinterpol(self,timebis):
		"""it's a interpolation function to change the base time of the signal
  
          timebis : the new base time
  
          this function return a dictionnary with these keys :
          
          time : new base time
          amplitude : new amplitude"""

		if type(self.time) and type(self.amplitude) is not type(array([])):
			self.time=array(self.time)
			self.amplitude=array(self.amplitude)
			
		amplitudebis=interp(timebis,self.time,self.amplitude)
		return dict({'time':timebis,'amplitude':amplitudebis})

	def recalt0(self,t0):
		"""It's a temporal offset function
          t0 : time offset"""
		if type(self.time) and type(self.time) is not type(array([])):
			self.time=array(self.time)
			self.amplitude=array(self.amplitude)
			
		dt=(self.time[1]-self.time[0])
		nbt=len(self.time)
		iii=arange(nbt)
		timebis=t0+iii*dt
		amplitudebis=self.amplitude
		return dict({'time':timebis,'tension':amplitudebis})

	def timewindow(self,t1,t2,windowtype):
		"""It's a window function. You can choose between Hanning, Hamming and Blackman window functions
          t1 : starting time of the window calculation
          t2 : end time of the window calculation
          windowtype : 1 => hanning function, 2 => hamming function, 3 => blackman function
          
          this function return a dictionnary with these keys :
          
          time : new base time
          amplitude : new amplitude obtained after calculation"""

		if type(self.time) and type(self.amplitude) is not type(array([])):
			self.time=array(self.time)
			self.amplitude=array(self.amplitude)
			
		dt=(self.time[1]-self.time[0])		
		t0=self.time[0]
		indice1=int((t1-t0)/dt)
		indice2=int((t2-t0)/dt)
		print(t0)
		print(indice1)
		print(indice2)
		timebis=take(self.time,range(indice1,indice2))
		amplitudebis=take(self.amplitude,range(indice1,indice2))
		if windowtype==1 :
			amplitudebis=amplitudebis*hanning(len(amplitudebis))
		elif windowtype==2 :
			amplitudebis=amplitudebis*hamming(len(amplitudebis))
		elif windowtype==3 :
			amplitudebis=amplitudebis*blackman(len(amplitudebis))    
		return dict({'time':timebis,'amplitude':amplitudebis})

	def ddot(self,RC,Aeq,balundBlosses):
		"""It's a function to calculate E-Field from a DDot signal. Don't forget to integrate the DDot signal.
          RC : DDoT impedance
          Aeq : Equivalent area of the DDot
          balundBlosses : Insertion losses of the balun in dB
          
          this function return a dictionnary with these keys :
          
          time :  base time
          amplitude :  E-field amplitude"""

		if type(self.time) and type(self.amplitude) is not type(array([])):
			self.time=array(self.time)
			self.amplitude=array(self.amplitude)
			
		epsilon=8.85e-12		
		balunlosses=10**(balundBlosses/20)
		efield=balunlosses*self.amplitude*(RC*Aeq*epsilon)
		return dict({'time':self.time,'amplitude':efield})

	def bdot(self,Aeq,balundBlosses):
		"""It's a function to calculate H-Field from a DDot signal. Don't forget to integrate the BDot signal.
          Aeq : Equivalent area of the BDot
          balundBlosses : Insertion losses of the balun in dB
          
          this function return a dictionnary with these keys :
          
          time :  base time
          amplitude :  H-field amplitude"""

		if type(self.time) and type(self.amplitude) is not type(array([])):
			self.time=array(self.time)
			self.amplitude=array(self.amplitude)
			
		mu=4*pi*1e-7		
		balunlosses=10**(balundBlosses/20)
		hfield=balunlosses*self.amplitude/(Aeq*mu)
		return dict({'time':self.time,'amplitude':hfield})

class SigFreqTreatment :
	"""Python Class with functionnalities to do some treatments on frequency signals
     frequency : frequency base
     amplitude : amplitude of the signal"""
	
	def __init__(self,frequency=[],amplitude=[]):
		
		self.frequency=frequency
		self.amplitude=amplitude
	
	
	
	def calcifft(self):
		"""It's an inverse fft function
          
          this function return a dictionnary with these keys :
          
          time : time base obtained after inverse fft calculation
          FFTinv : amplitudes obtained after inverse fft calculation"""
          
		if type(self.frequence) and type(self.amplitude) is not type(array([])):
			self.frequence=array(self.frequence)
			self.amplitude=array(self.amplitude)
			if self.amplitude.dtype is not complex64 or complex128:
				raise TypeError("Amplitudes are not complex numbers")
				
		df=self.frequency[1]-self.frequency[0]
		tabfreqneg=take(self.amplitude,range(1,len(self.amplitude)))
		tabfreqneg=tabfreqneg[::-1]
		tabfreqneg=conjugate(tabfreqneg)
		n_amplitude=concatenate((self.amplitude,tabfreqneg))
		resultFFTinv=real(ifft(n_amplitude))
		resultFFTinv=resultFFTinv*len(resultFFTinv)*df
		tabtime=arange(len(resultFFTinv))/(df*len(resultFFTinv))
		return dict({'time':tabtime,'FFTinv':resultFFTinv})
	
	def calcitfdcea(self,tmin,tmax,nbt):
		"""It's an inverse TFD function.
          tmin : start of the time base
          tmax : end of the time base
          nbt : number of points
          
          this function return a dictionnary with these keys :
          
          time : time base obtained after inverse TFD calculation
          TFDinv : amplitudes obtained after inverse TFD calculation
          nbt : number of points
          dt : delta time
          """
		if type(self.frequency) and type(self.amplitude) is not type(array([])):
			self.frequency=array(self.frequency)
			self.amplitude=array(self.amplitude)
			if self.amplitude.dtype is not complex64 or complex128:
				raise TypeError("Amplitudes are not complex numbers")
				
		dt=(tmax-tmin)/(nbt-1)
		df=self.frequence[1]-self.frequence[0]
		iii=arange(nbt)
		tabtime=tmin+iii*dt
		pondere=ones(len(self.frequence))
		pondere=pondere*2
		if self.frequence[0]==0:
			pondere[0]=1
		else:
			pondere[0]=2
		tabresultTFinv=[sum(self.amplitude*df*pondere*exp(2j*pi*(tmin+jjj*dt)*self.frequence)) for jjj in range(nbt)]
		tabresult=real(tabresultTFinv)
		return dict({'time':tabtime,'TFDinv':tabresult,'nbt':nbt,'dt':dt})
	
	def calcintegralef(self):
		"""It's an Integral calculation into the frequency domain
          
          this function return a dictionnary with these keys :
          
          frequency : frequency base
          amplitude : amplitudes obtained after calculation
          """
		if type(self.frequency) and type(self.amplitude) is not type(array([])):
			self.frequency=array(self.frequency)
			self.amplitude=array(self.amplitude)
			if self.amplitude.dtype is not complex64 or complex128:
				raise TypeError("Amplitudes are not complex numbers")
				
		tabresult=self.amplitude/(1j*2*pi*self.frequency)
		return dict({'frequency':self.frequency,'amplitude':tabresult})
	
	def calcderiveef(self):
		"""It's a Derivate calculation into the frequency domain
  
          this function return a dictionnary with these keys :
          
          frequency : frequency base
          amplitude : amplitudes obtained after calculation
          """
		if type(self.frequency) and type(self.amplitude) is not type(array([])):
			self.frequency=array(self.frequency)
			self.amplitude=array(self.amplitude)
			if self.amplitude.dtype is not complex64 or complex128:
				raise TypeError("Amplitudes are not complex numbers")
					
			tabresult=self.amplitude*(1j*2*pi*self.frequency)
			return dict({'frequency':self.frequency,'amplitude':tabresult})

	def calcinterpolf(self,n_frequency):
		"""It's an Interpolation calculation into the frequency domain
          
          n_frequency : new frequency base
          
          this function return a dictionnary with these keys :
          
          frequency : frequency base
          amplitude : amplitude obtained after calculation
          """
		if type(self.frequency) and type(self.amplitude) is not type(array([])):
			self.frequency=array(self.frequency)
			self.amplitude=array(self.amplitude)
			if self.amplitude.dtype is not complex64 or complex128:
				raise TypeError("Amplitudes are not complex numbers")
					
			module=abs(self.amplitude)
			phase=unwrap(angle(self.amplitude))
			n_module=interp(n_frequency,self.frequency,module)
			n_phase=interp(n_frequency,self.frequency,phase)
			n_amplitude=n_module*exp(1j*n_phase)
			return dict({'frequency':n_frequency,'amplitude':n_amplitude})
	
	def calcinterppolyf(self,fmax,dfbis,fmin,order):
		"""It's a Polynomial Interpolation calculation into the frequency domain
  
          fmax : frequency max
          fmin : frequency min
          dfbis : new delta frequency
          order : order of the polynomial interpolation
          
          this function return a dictionnary with these keys :
          
          frequency : frequency base
          amplitude : amplitude obtained after calculation"""
          
		if type(self.frequency) and type(self.amplitude) is not type(array([])):
			self.frequency=array(self.frequency)
			self.amplitude=array(self.amplitude)
			if self.amplitude.dtype is not complex64 or complex128:
				raise TypeError("Amplitudes are not complex numbers")
					
			df=self.frequency[1]-self.frequency[0]
			Indicelimitefh=int(fmax/df)
			self.frequency=take(self.frequency,range(Indicelimitefh))
			module=take(abs(self.amplitude),range(Indicelimitefh))
			phase=unwrap(take(angle(self.amplitude),range(Indicelimitefh)))
			polymodule=poly1d(polyfit(self.frequency,module,order))
			polyphase=poly1d(polyfit(self.frequency,phase,order))
			nbf=int((fmax-fmin)/dfbis)+1
			n_frequency=arange(nbf)*dfbis+fmin
			n_amplitude=polymodule(n_frequency)*exp(1j*polyphase(n_frequency))
			return dict({'frequency':n_frequency,'amplitude':n_amplitude})
		
	def freqwindow(self,f1,f2,windowtype):
		"""It's a window function into the frequency domain. You can choose between Hanning, Hamming and Blackman window functions
  
          f1 : start frequency
          f2 : end frequency
          windowtype : 1 => hanning function, 2 => hamming function, 3 => blackman function
          
          this function return a dictionnary with these keys :
          
          frequency : frequency base
          amplitude : amplitude obtained after calculation"""
          
		if type(self.frequency) and type(self.amplitude) is not type(array([])):
			self.frequency=array(self.frequency)
			self.amplitude=array(self.amplitude)
			if self.amplitude.dtype is not complex64 or complex128:
				raise TypeError("Amplitudes are not complex numbers")
				
		df=(self.frequency[1]-self.frequency[0])		
		f0=self.frequency[0]
		indice1=int((f1-f0)/df)
		indice2=int((f2-f0)/df)
		print(f0)
		print(indice1)
		print(indice2)
		n_frequency=take(self.frequency,range(indice1,indice2))
		n_amplitude=take(self.amplitude,range(indice1,indice2))
		if windowtype==1 :
			n_amplitude=n_amplitude*hanning(len(n_amplitude))
		elif windowtype==2 :
			n_amplitude=n_amplitude*hamming(len(n_amplitude))
		elif windowtype==3 :
			n_amplitude=n_amplitude*blackman(len(n_amplitude))    
		return dict({'frequency':n_frequency,'amplitude':n_amplitude})
