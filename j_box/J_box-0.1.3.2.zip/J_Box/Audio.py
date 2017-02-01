import numpy as np
import math
import wave
import random
import scipy
from scipy.signal import butter
from scipy.signal import lfilter
import pylab as pl
import scipy.io.wavfile
from scipy.fftpack import fft
import dspUtil


#perplexity necessarily requires an input of a probability distribution. the input should sum to 1 or else it is incorrect
def Perplexity(p):
    perp = np.array(np.log2(p)*p)
    perp = (-1)*perp.sum()
    perp = 2**perp
    return perp

#this basically just takes an array and puts it into a form usable by perplexity function
def UniqueCounter(p):
    #this assumes p is a numpy array
    #this will also normalize p to make it a probability density
    trash,counts = np.unique(p,return_counts=True)
    counts = np.array(counts)
    total = counts.sum()
    if total>0:
        counts = np.float64(counts)/np.float64(total)

    return np.array(counts)

#This takes an input of frequency clip and outputs an array of features
def SignalFeatureFinder(f0):
    #f0 = FixF0(f0)
    perplexity = Perplexity(UniqueCounter(f0))
    f0_mean = f0.mean()
    f0_var = f0.var()
    f0_max = f0.max()
    #i'd lke to add a perplexity variance but that would require windowing. I'm not sure if that's worth it at the moment
    
    return [f0_mean,f0_var,f0_max,perplexity]

#Dynamic Time warping algo. this is the windowed version (which will speed up the runtime by making the assumption 
#that a point within the window and a point outside the window have a very low probability of matching up and thereby only warps
#locally

#I suggest a rather large window size.

#p is signal 1
#q is signal 2
#w is window size
#signals should be of same length
def DTWDistance(p,q,w):
    DTW = {}
    
    #makes sure the window size is valid basically
    w = max(w,abs(len(p)-len(q)))
    
    #initialize a matrix
    for i in range(-1,len(p)):
        for j in range(-1,len(q)):
            DTW[(i,j)] = float('inf')
    DTW[(-1,-1)] = 0
    
    #fill it with distances. basically an adjacency matrix of euclidian distance around the windowed area
    for i in range(len(p)):
        #make sure it stays within bounds 
        for j in range(max(0,i-w),min(len(q),i+w)):
            dist = (p[i]-q[j])**2
            #warp the local area and check
            DTW[(i,j)] = dist + min(DTW[(i-1,j)],DTW[(i,j-1)],DTW[(i-1,j-1)])
    
    #sqrt on the min squared distance to get the true euclidian distance (after warping)
    return math.sqrt(DTW[len(p)-1, len(q)-1])


##LB Keogh lower bound is something to also help speed up dtw. useful when using the windowed version
#r is the "reach". basically just another window. I'd default it to be just bigger than DTW window size. probably 5 to 10
def LBK(p,q,r):
    LB_sum = 0
    
    for ind,i in enumerate(p):
        
        lower_bound = min(q[(ind-r if ind-r>=0 else 0):(ind+r)])
        upper_bound = max(q[(ind-r if ind-r>=0 else 0):(ind+r)])
        
        if i>upper_bound:
            LB_sum = LB_sum+(i-upper_bound)**2
        if i<lower_bound:
            LB_sum = LB_sum+(i-lower_bound)**2

    return math.sqrt(LB_sum)


#let's add kmeans while i'm at it
def kmeans(data,num_clust,num_iter,w,lbw):
    centroids=random.sample(data,num_clust)
    counter=0

    for n in range(num_iter):
        counter+=1
        
        assignments={}
        #assign data points to clusters
        for ind,i in enumerate(data):
            min_dist=float('inf')
            closest_clust=None
            for c_ind,j in enumerate(centroids):
                if LBK(i,j,lbw)<min_dist:
                    cur_dist=DTWDistance(i,j,w)
                    if cur_dist<min_dist:
                        min_dist=cur_dist
                        closest_clust=c_ind
            if closest_clust in assignments:
                assignments[closest_clust].append(ind)
            else:
                assignments[closest_clust]=[]

        #recalculate centroids of clusters
        for key in assignments:
            clust_sum=0
            for k in assignments[key]:
                clust_sum=clust_sum+data[k]
   
            centroids[key]=[m/len(assignments[key]) for m in clust_sum]
            
    return centroids

# Runs STFT on the data for use in examining the spectrogram
# Output: M x N matrix, M being time and N being frequencies
def stft(data, fftsize=1024, overlap=4):   
    w = scipy.hanning(fftsize+1)[:-1]
    return np.array([np.fft.rfft(w*data[i:i+fftsize]) 
                for i in range(0, len(data)-fftsize, fftsize / overlap)])

# Runs the YAAPT algorithm to pull out fundamental frequencies for each time
def yaapt(data, sample_rate):
    # Separate out the signal into the regular and the non-linearly
    # transformed signal, afterwards bandpass filtering both.
    #signal, signal_nonlinear = data, data ** 2
    signal, signal_nonlinear = stft(data).T, stft(data).T ** 2

    # Other stuff...
    return signal,signal_nonlinear

# Implements special harmonics correlation. This can likely be optimized.
# Input: M x N matrix, with M being frequencies and N being time.
#   a window_length in frequencies.
# Output: M x N matrix, with M being frequencies and N being time.
def shc(signal, window_length=40., number_harmonics=3):
    # This function finds what frequency corresponds to what index
    freq_idx = lambda f: int(np.floor(float(f) / (16000. / 1024.)))

    # This will hold the output
    shc_signal = np.zeros(signal.shape)

    # Loop through the window length
    for f in [-1, 0, 1]:
        for freq in range(signal.shape[0]):
            # Calculate the indices for the harmonics to consider
            harmonics = [r*freq+f for r in range(number_harmonics)
                         if r*freq+f < signal.shape[0]]
            # Compute the product of the amplitudes of this frequency
            # multiplied by the amplitudes of the harmonics.
            h = np.prod(np.array([signal[h,:] for h in harmonics]), axis=0)
            shc_signal[freq, :] += h

    return shc_signal


# Imports a .wav file (vocal) and clips sections where no voice is detected. 
def CustomVAD(Wav_File_Full_Path):


    #### Data Aquisition ####
    for f in wav_data:
        fs, wav = scipy.io.wavfile.read(Wav_File_Full_Path)

    #### Data Windowing ####
    #20ms Hamming Window Weights
    N = (fs/1000) * 20                    #Number of samples in 20ms
    Weight = np.hamming(N)                #Hamming window weights

    #20ms Windowing (10ms overlap) with Hamming Weights
    step = N/2                            #Number of values in a 10ms window
    end = len(wav)-(N/2)-1                #Starting point of the last window

    Windows = []
    for i in range(0,end,step):
        temp = wav[i:i+N]
        temp = np.multiply(temp,Weight)   #Applies Hamming weights to windows
        Windows.append(temp)

    Windows = np.array(Windows)
    Windows = Windows[1:len(Windows)]


    #### Data Pre-Processing #### 

    S = 1.00/float(fs)                                    #Sample Spacing
    xf = np.linspace(0.0, 1.0/(2.0*S), N/2)               #FFT List Index to Frequency Relationships (in Hz)

    ####Finding Mel-Scale Frequency Per Index of fft vector (Transforming ^ into Mel-Scale)####
    def MelTransform(FHz): #Transforms Frequency in Hz to Mel-Scale Frequency
        FMel = (1000/np.log(2))*(1+(FHz/1000))
        return FMel

    xMel = []
    for i in xf:
        temp = MelTransform(i)
        xMel.append(temp)

    ####Finding index of Frequency range between: 0kHz - 4kHz####
    ####print xMel                                           ####
    ####for i,val in enumerate(xMel):                        ####
    ####    if val > 4000:                                   ####
    ####        print i                                      ####
    ######## INDEX for 0-4kHz == [0:35] in fft vector############ 


    ####Log Spectral Energy of Each Window####

    #For quick evaluation*
    # j = [] #global min
    # k = [] #global max

    #Loop Preallocations:
    windows = []
    for i in range(0,len(Windows)):
        temp = Windows[i]
        temp = fft(temp)
        temp = temp[0:(len(temp)/2)]   #Restrict Range to Single Sided Spectrum
        temp = temp[0:35]              #Evaluates only the values in the 0-4kHz Mel-Scale frequency range (valaid vocal ranges)
        temp = np.absolute(temp)
        temp = np.square(temp)
        temp = np.log10(temp)
        windows.append(temp)

    #* Quick Evaluation (cont)       
    #     temp2 = min(windows[i])
    #     temp3 = max(windows[i])
    #     j.append(temp2)
    #     k.append(temp3)
    # print min(j)
    # print max(k)


    #Divide each Window into 5 smaller Sub-Bands
    def chunks(l, n):
        n = max(1, n)
        return [l[i:i + n] for i in range(0, len(l), n)]

    windows = [chunks(x,7) for x in windows]
    #^^^ This "7" will give you a lot of problems later, find a better way to define Size of sub-bands SOON.



    ####Speech Detection Algorithm Initialization####
    #Base Threshold (T)
    list = windows[0][0]
    for x in range(1,5):
        list = np.append(list, windows[0][x],0)

    T = np.mean(list)
    Ts = T                           #Speech Threshold
    Tp = 1.2*T                       #Pause Threshold

    #Identify first "Silent Segment"
    first_silent = []
    for i in range(1,len(windows)):
        val_present = len([x for x in windows[i][0] if x<T])
        if  val_present > 0:
            first_silent.append(i)
            break

    ####Calculate Speech to Noise Ratio (SNR)####

    #Mean of all prior speech sections
    Prior_list = np.array([])
    for i in range(0,first_silent[0]):
        temp_list = windows[i][0]
        for x in range(1,5):
            temp_list = np.append(list, windows[0][x],0)
        Prior_list = np.append(Prior_list,temp_list,0)
    Prior_mean = np.mean(Prior_list)

    #Mean of first "Silent Section"
    Silent_mean = np.mean(windows[first_silent[0]][:])

    #SNR calculation (lambd)
    lambd = Prior_mean / Silent_mean


    ####Iterative Thresholding Re-Classification Function####
    def Thresh(Mean,Tp_):
        if (Mean < Tp_):
            new_Ts = Mean
            new_Tp = 1.2 * new_Ts
            return new_Ts , new_Tp
        return None

    def GammaClassify(Frame_mean,Ts_,Tp_):
        if Frame_mean < Tp_:
            Gamma = 1.6             #Use "Non-Speech" gamma
        if Frame_mean > Ts_:
            Gamma = 1               #Use "Speech" gamma
        return Gamma

    #### Algorithm Computation ####


    ####Re-thresholding and Gamma Calculations####
    mean_arr = []
    for data in windows:
        sum_agg = 0
        for x in data:
            sum_agg+= sum(x) /  float(len(windows[0])*len((windows[0][0])))
        mean_arr.append(sum_agg)

    Gamma_list = []
    moving_ts = Ts
    moving_tp = Tp
    tp_list = []
    for i,data in enumerate(mean_arr):
        Gamma = GammaClassify(data,moving_ts,moving_tp)        #Gamma Classification for Tk Calculation
        Gamma_list.append(Gamma)
        thresh = Thresh(data,moving_tp) 
        if thresh != None:
            (moving_ts,moving_tp) = thresh                     #Re-Thresholding of Ts and Tp
        tp_list.append(moving_tp)

    #### Threshold Correction (Fc) from Spectral Flatness Function
    Fc_windows = []
    for i in range(0,len(Windows)):
        temp = Windows[i]
        temp = fft(temp)
        temp = temp[0:(len(temp)/2)]      #Restrict Range to Single Sided Spectrum
        temp = temp[0:35]                 #Evaluates only the values in the 0-4kHz Mel-Scale frequency range (valaid vocal ranges)
        temp = np.absolute(temp)
        temp = dspUtil.calculateSpectralFlatness(temp)   #Computes Fc from Spectral Flatness Function
        Fc_windows.append(temp)



    #### Tk Calculations ####   
    first_pause_window_index = None
    for i,gamma in enumerate(Gamma_list):
        if gamma==1.6:
            first_pause_window_index = i
            break


    def final_classifier(Tk,Tp):
        if Tk > Tp:
            return 1
        return 0

    last_pause_mean = np.mean(windows[first_pause_window_index][0])
    # Skip the first pause window
    first_pause_window_index+=1
    results = []
    for i in range(first_pause_window_index,len(Gamma_list)):      
            if Gamma_list[i] == 1.6:
                last_pause_mean = np.mean(windows[i][0])
            Tk = lambd*last_pause_mean + (Gamma_list[i])*(1 - Fc_windows[i])
            results.append(final_classifier(Tk,tp_list[i]))


    #### Time at Each Classified Section ####
    Time_Total = (len(wav)/fs) * 1000
    end_time = Time_Total
    start_time = Time_Total - (len(results)*10)

    Time_Vect = range(start_time, end_time,10)

    Results = zip(results, Time_Vect)
    # print Results
    
    CVAD = []
    for i in range (0,(Time_Vect[0]/10)):
        temp = 0
        CVAD.append(temp)
    CVAD.extend(results)

    #### Quick-View Results ####
    # print wav_data[Q]

    # print sum(results)
    # print len(results)
    # print results
    
    return CVAD

#counts how many data points are in each cluster
def cluster_counter(data,clusters,w):
    #create a vector of zeros that are the same length as the number of clusters. 
    count = np.zeros(len(clusters))
    
    #go through each data point and check the dtw distance between each cluster
    for i in data:
        distances = []
        for j in clusters:
            distances.append(DTWDistance(i,j,w))
        temp = np.array(distances)
        count[temp.argmax(axis=0)]+=1
    
    return count

#creates a matrix where each row corresponds to the same number row of the data. each row in "count" is a one-shot encoding 
#designating which cluster the corresponding data sample belongs to.
def cluster_labler(data,clusters,w):
    #create a vector same length as the number of data, wich each row being a one-hot encoding to designate cluster
    count = []
    l = len(clusters)
    #go through each data point and check the dtw distance between each cluster
    for i in data:
        distances = []
        for j in clusters:
            distances.append(DTWDistance(i,j,w))
        one_hot = [0]*l
        ind = np.array(distances)
        ind = ind.argmax(axis=0)
        one_hot[ind]=1
        count.append(one_hot)
    
    return count

#this shall return the overall mean and variance of each cluster

#eventually I should expand this to give the statistics overall and by each axis
def cluster_basic_statistics(data,clusters,w):
    
    #I need to make this section sexier
    #format: [cluster_label][distance]
    distances = []
    for i in clusters:
        distances.append([0])
    for i in data:
        cluster_label = cluster_labler([i],clusters,w)
        cluster_label = np.array(cluster_label[0])
        cluster_label = cluster_label.argmax(axis=0)
        dist = DTWDistance(i,clusters[cluster_label],w)
        distances[cluster_label].append(dist)
        
    distances = np.array(distances)
    
    #format: [mean,median,range,variance]
    stats = [];
    for i in distances:
        if len(i)>1:
            stats.append([np.mean(i[1:]),np.median(i[1:]),np.max(i[1:])-np.min(i[1:]),np.var(i[1:])])
        else:
            stats.append([0,0,0,0])
    
    return stats

