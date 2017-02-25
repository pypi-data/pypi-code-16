import numpy as np
from .ldpcalgebra import*
__all__ = ['BinaryProduct', 'InCode', 'BinaryRank','Coding_random','Coding','SparseProduct']


def Coding_random(G,SNR,tG_sparse=None):
    """
    Randomly computes a k-bits message v, where G's shape is (k,n). And sends it
    through the canal.
    
    Message v is passed to G: d = v,G. d is a n-vector turned into a BPSK modulated
    vector x. Then Additive White Gaussian Noise (AWGN) is added. 
    
    SNR is the Signal-Noise Ratio: SNR = 10log(1/variance) in decibels, where variance is the variance of the AWGN.
    Remember: 
        1. d = v.G
        2. x = BPSK(d) (or if you prefer the math: x = pow(-1,d) )
        3. y = x + AWGN(0,snr) 

    ----------------------------

    Parameters:

    G: 2D-Array, Coding Matrix obtained from CodingMatrixG function.
    
    SNR: the Signal-Noise Ratio: SNR = 10log(1/variance) in decibels. 
        >> SNR = 10log(1/variance) 

    -------------------------------

    Returns

    Tuple(v,y) (Returns v to keep track of the random message v)
    """
    k,n = G.shape

    v=np.random.randint(2,size=k)
    if tG_sparse==None:
        d=BinaryProduct(v,G)
    else:
        d = SparseProduct(tG_sparse,v)
    x=pow(-1,d)

    sigma = 10**(-SNR/20)
    
    e = np.random.normal(0,sigma,size=n)
 
    y=x+e

    return(v,y)





def Coding(G,v,SNR,tG_sparse=None):
    """
    Codes a message v with Coding Matrix G, and sends it through a noisy (default)
    channel. 

    G's shape is (k,n). 

    Message v is passed to G: d = v,G. d is a n-vector turned into a BPSK modulated
    vector x. Then Additive White Gaussian Noise (AWGN) is added. 
    
    SNR is the Signal-Noise Ratio: SNR = 10log(1/variance) in decibels, where variance is the variance of the AWGN.
    Remember: 
    
        1. d = v.G
        2. x = BPSK(d) (or if you prefer the math: x = pow(-1,d) )
        3. y = x + AWGN(0,snr) 

    
    Parameters:

    G: 2D-Array, Coding Matrix obtained from CodingMatrixG function.
    v: 1D-Array, k-vector (binary of course ..) 
    SNR: Signal-Noise-Ratio: SNR = 10log(1/variance) in decibels. 

    -------------------------------

    Returns y

    """
    k,n = G.shape

    if len(v)!= k:
        raise ValueError(" Size of message v must be equal to number of Coding Matrix G's rows " )  
    
    if tG_sparse==None:
        d=BinaryProduct(v,G)
    else:
        d = SparseProduct(tG_sparse,v)
    x=pow(-1,d)

    sigma = 10**(-SNR/20)
    e = np.random.normal(0,sigma,size=n)


    y=x+e

    return y
   
