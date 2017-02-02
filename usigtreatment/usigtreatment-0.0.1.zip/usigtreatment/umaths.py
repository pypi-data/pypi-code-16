# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 14:06:35 2017

@author: Krounet
e-mail:krounet@gmail.com
"""

from numpy import array,log10,cos,sin,arcsin,pi

class maths_utils:
    
    """Python class with some others functionnalities usefull in signal treatments
    
    magdbpower : power magnitude in db
    magdbvoltage : voltage magnitude in db
    maglin : linear magnitude
    phdeg : phase in degree
    phrad : phase in radian
    vector_complex : complex signal"""
    
    def __init__(self,magdBpower=0,magdBvoltage=0,phdeg=0,phrad=0,vector_complex=[],maglin=0):
        
        
        
        self.magdBpower=magdBpower
        self.magdBvoltage=magdBvoltage
        self.maglin=maglin
        self.phdeg=phdeg
        self.phrad=phrad
        self.vector_complex=vector_complex
        
    def magdbpower_phdeg_to_vectorcomplex(self):
        
        """(magdbpower,phdeg) => vector complex (a+jb)
        
        this function return a dictionnary with these keys :
        
        vectorcomplex : vector complex obtained after calculation"""
        
        if type(self.magdBpower)  is not type(array([])):
            self.magdBpower=array(self.magdBpower)
        if type(self.phdeg) is not type(array([])):
            self.phdeg=array(self.phdeg)
            
        n_maglin=10**(self.magdBpower/10)
        n_phrad=self.phdeg*180/pi
        return dict({'vectorcomplex':n_maglin*array([complex(cos(n_phrad[i]),sin(n_phrad[i])) for i in range(len(n_phrad))])})
        
    def magdbvoltage_phdeg_to_vectorcomplex(self):
        
        """(magdbvoltage,phdeg) => vector complex (a+jb)
        
        this function return a dictionnary with these keys :
        
        vectorcomplex : vector complex obtained after calculation"""
        
        if type(self.magdBvoltage) is not type(array([])) :
            self.magdBvoltage=array(self.magdBvoltage)
        if type(self.phdeg) is not type(array([])):
            self.phdeg=array(self.phdeg)
            
        n_maglin=10**(self.magdBvoltage/20)
        n_phrad=self.phdeg*pi/180
        return dict({'vectorcomplex':n_maglin*array([complex(cos(n_phrad[i]),sin(n_phrad[i])) for i in xrange(len(n_phrad))])})
        
    def magdbpower_phrad_to_vectorcomplex(self):
        
        """(magdbpower,phrad) => vector complex (a+jb)
        
        this function return a dictionnary with these keys :
        
        vectorcomplex : vector complex obtained after calculation"""
        
        if type(self.magdBpower)  is not type(array([])):
            self.magdBpower=array(self.magdBpower)
        if type(self.phrad)  is not type(array([])):
            self.phrad=array(self.phrad)
            
        n_maglin=10**(self.magdBpower/10)
        return dict({'vectorcomplex':n_maglin*array([complex(cos(self.phrad[i]),sin(self.phrad[i])) for i in range(len(n_maglin))])})
        
    def magdbvoltage_phrad_to_vectorcomplex(self):
        
        """(magdbvoltage,phrad) => vector complex (a+jb)
        
        this function return a dictionnary with these keys :
        
        vectorcomplex : vector complex obtained after calculation"""
        
        if type(self.magdBvoltage) is not type(array([])):
            self.magdBpower=array(self.magdBvoltage)
        if type(self.phrad) is not type(array([])):
            self.phdeg=array(self.phrad)
            
        n_maglin=10**(self.magdBvoltage/20)
        return dict({'vectorcomplex':n_maglin*array([complex(cos(self.phrad[i]),sin(self.phrad[i])) for i in range(len(n_maglin))])})
        
    def maglin_phdeg_to_vectorcomplex(self) :
        
        """(maglin,phdeg) => vector complex (a+jb)
        
        this function return a dictionnary with these keys :
        
        vectorcomplex : vector complex obtained after calculation"""
        
        if type(self.maglin)  is not type(array([])):
            self.maglin=array(self.maglin)
        if type(self.phdeg)  is not type(array([])):
            self.phdeg=array(self.phdeg)
            
        n_phrad=self.phdeg*180/pi
        return dict({'vectorcomplex':self.maglin*array([complex(cos(n_phrad[i]),sin(n_phrad[i])) for i in xrange(len(n_phrad))])})
        
    def vector_complex_to_magdbpower_phrad(self):
        
        """vector complex => (magdbpower,phrad)
        
        this function return a dictionnary with these keys :
        
        magdBpower : power magnitude in dB
        phrad : phase in radian"""
        
        if type(self.vector_complex) is not type(array([])):
            self.vector_complex=array(self.vector_complex)
            
        return dict({'magdBpower':10*log10(abs(self.vector_complex)),'phrad':arcsin(self.vector_complex.imag/abs(self.vector_complex))})
        
    def vector_complex_to_magdbpower_phdeg(self):
        
        """vector complex => (magdbpower,phdeg)
        
        this function return a dictionnary with these keys :
        
        magdBpower : power magnitude in dB
        phdeg : phase in degree"""
        
        if type(self.vector_complex) is not type(array([])):
            self.vector_complex=array(self.vector_complex)
        return dict({'magdBpower':10*log10(abs(self.vector_complex)),'phdeg':180*arcsin(self.vector_complex.imag/abs(self.vector_complex))/pi})
        
    def vector_complex_to_magdbvoltage_phrad(self):
        
        """vector complex => (magdbvoltage,phrad)
        
        this function return a dictionnary with these keys :
        
        magdBvoltage : power magnitude in dB
        phrad : phase in radian"""
        
        if type(self.vector_complex) is not type(array([])):
            self.vector_complex=array(self.vector_complex)
        return dict({'magdBvoltage':20*log10(abs(self.vector_complex)),'phdrad':arcsin(self.vector_complex.imag/abs(self.vector_complex))})
        
    def vector_complex_to_magdbvoltage_phdeg(self):
        
        """vector complex => (magdbvoltage,phdeg)
        
        this function return a dictionnary with these keys :
        
        magdBvoltage : power magnitude in dB
        phdeg : phase in degree"""
        
        if type(self.vector_complex) is not type(array([])):
            self.vector_complex=array(self.vector_complex)
        return dict({'magdBvoltage':20*log10(abs(self.vector_complex)),'phdeg':180*arcsin(self.vector_complex.imag/abs(self.vector_complex))/pi})