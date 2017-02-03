from random import randrange
import numpy as np
from numpy.linalg import svd

def happyface(x):
    # Head
    arch = math.sqrt(1.0 - x*x)
    components = [arch, -arch]
    
    # Eyes
    eyeWidth = 0.2
    eyeHeight = eyeWidth * 0.6
    eyeX = 1.0 / 3.0
    eyeY = 0.25
    eyeCoord = (abs(x) - eyeX) / eyeWidth
    if eyeCoord > -1.0 and eyeCoord < 1.0:
        eyeArch = math.sqrt(1.0 - eyeCoord*eyeCoord)
        components.append(eyeY + eyeHeight * eyeArch)
        #components.append(eyeY - eyeHeight * eyeArch)
    
    # Mouth
    mouthRads = math.pi * 0.7
    mouthLowerRadius = 0.85
    mouthUpperRadius = 3
    mouthYoffset = 0.15
    mouthW2 = mouthLowerRadius * math.sin(mouthRads / 2.0)
    if abs(x) < mouthW2:
        # Lower lip
        mouthLowerCoord = x / mouthLowerRadius
        mouthLowerArch = math.sqrt(1.0 - mouthLowerCoord*mouthLowerCoord)
        components.append(-mouthLowerRadius*mouthLowerArch + mouthYoffset)
        
        # Upper lip
        mouthUpperH = math.sqrt(mouthUpperRadius*mouthUpperRadius - mouthW2*mouthW2) - mouthLowerRadius * math.cos(mouthRads / 2.0)
        mouthUpperCoord = x / mouthUpperRadius
        mouthUpperArch = math.sqrt(1.0 - mouthUpperCoord*mouthUpperCoord)
        components.append(mouthUpperH - mouthUpperRadius*mouthUpperArch + mouthYoffset)

    # Pick one of the components
    i = numpy.random.randint( len(components), size = 1)
    return components[i]
    
def random_dataset( D, N,):
    """
        D: int
            number of features

        N: int
            number of samples 

        B: int
            number of blocks 
    """
    X = numpy.random.uniform(low=-1,high=1 ,size=(D,N))
    Y = numpy.random.uniform(low=-1,high=1,size=(D,N))
    A = numpy.zeros( (D,D) )
    return X,Y,A    
def orthogonalize_matrix(w):
    U, s, V =  svd(w.T, full_matrices=False)
    S = numpy.diag(s)
    #print U.shape, V.shape, s.shape
    #print (numpy.dot(U,S)).shape
    #print np.allclose(w.T, np.dot(U, np.dot(S, V)))
    return numpy.dot(U,S).T
def imbalanced_synthetic_dataset_uniform(D, N, B, cluster_percentage = 1, within_noise = 0.5, between_noise = 0.5, association_type = 'parabola' ):
    """
        D: int
            number of features

        N: int
            number of samples 

        B: int
            number of blocks 
    """
    
    X = numpy.random.uniform(low=-1,high=1 ,size=(D,N))
    Y = numpy.random.uniform(low=-1,high=1,size=(D,N))
    
    common_base = numpy.random.uniform(low=-1,high=1 ,size=(B+1,N))
    X_base = numpy.random.uniform(low=-1,high=1 ,size=(D,N))
    Y_base = numpy.random.uniform(low=-1,high=1 ,size=(D,N))
    
    X_base = orthogonalize_matrix(X_base)
    Y_base = orthogonalize_matrix(Y_base)
    #X = orthogonalize_matrix(X)
    #Y = orthogonalize_matrix(Y)
    #common_base = orthogonalize_matrix(common_base)
    A = numpy.zeros( (D,D) )
    blockSize = int(round(D/B))
    #print D, B, blockSize
    '''for i in range(0,D,blockSize):
        for j in range(i,i+blockSize):
            if j < D:
                X[j]= [X[i,k]  + numpy.random.normal(0,.1,1) for k in range(len(X[j]))]
    '''
    if association_type == "L":
        common_base = numpy.hstack((numpy.random.uniform(low=-1.0,high=-1.0 ,size=(B+1,N/2)), numpy.random.uniform(low=-1,high=50 ,size=(B+1,N/2))))
        for l in range(B+1):
            common_base[l]= numpy.random.permutation(common_base[l])
    else:
        common_base = numpy.random.uniform(low=-1,high=1 ,size=(B+1,N))
    if association_type == "L":
        common_base_Y = numpy.random.uniform(low=-1,high=1 ,size=(B+1,N))
        for l in range(B+1):
            common_base_Y[l] = [numpy.random.uniform(low=l,high=100, size=1)  if common_base[l,k] < -0.999 else numpy.random.uniform(low=l,high=l, size=1) for k in range(N)]
        common_base_Y = orthogonalize_matrix(common_base_Y)
    #common_base = orthogonalize_matrix(common_base)
    
    number_associated_blocks =  max([int(B * cluster_percentage) , 1])
    assoc1 = [[] for i1 in range(number_associated_blocks)]
    assoc2 = [[] for j1 in range(number_associated_blocks)]
    
    for i in range(int(D*cluster_percentage)):
        l= randrange(0,number_associated_blocks)
        numpy.random.seed()
        if association_type == "L":
                    X[i]= [common_base[l,k]+ within_noise * numpy.random.uniform(low=-.1,high=.1, size=1) for k in range(N)]
        elif association_type == "log":
            X[i]= [math.fabs(common_base[l,k])  + within_noise * numpy.random.uniform(low=0,high=1 ,size=1) for k in range(N)]
        else:    
            X[i]= [common_base[l,k]  + within_noise * numpy.random.uniform(low=-1,high=1 ,size=1) for k in range(N)]
        #X[i]= [common_base[l][k] +  within_noise * numpy.random.uniform(low=-1,high=1 ,size=1) for k in range(N)]
        assoc1[l].append(i)
    
    noise_num = numpy.random.randint(N, size=int(N*between_noise))
    for i in  range(int(D*cluster_percentage)):
        l= randrange(0,number_associated_blocks)
        #slope = 1.0 +numpy.random.random_sample()#slope = numpy.random.random_sample()
        numpy.random.seed()
        if association_type == "parabola":
            Y[i]= [common_base[l,k]*common_base[l,k]  + within_noise *math.sqrt(math.fabs(numpy.random.uniform(low=-1,high=1 ,size=1))) for k in range(N)]
        elif association_type == "line":
            Y[i]= [common_base[l,k]  + within_noise * numpy.random.uniform(low=-1,high=1 ,size=1) for k in range(N)]
        elif association_type == "sine":
            Y[i]= [.5* math.sin(math.pi * common_base[l,k]*1.5)  + within_noise * numpy.random.uniform(low=-1,high=1 ,size=1)  for k in range(N)]
        elif association_type == "log":
            Y[i]= [math.log(math.fabs(common_base[l,k]))  + within_noise *math.fabs(numpy.random.uniform(low=0,high=1 ,size=1)) for k in range(N)]
        elif association_type == "step":
            p1 = numpy.percentile(common_base[l], 25)
            p2 = numpy.percentile(common_base[l], 50)
            p3 = numpy.percentile(common_base[l], 75)
            #NOISE = within_noise *numpy.random.uniform(low=-1,high=1 ,size=1)
            #Y[j]= [ 0 if common_base[l,k] <p1 else  1 + within_noise *numpy.random.uniform(low=-1,high=1 ,size=1)\
            #     if common_base[l,k] <p2 else 2+within_noise *numpy.random.uniform(low=-1,high=1 ,size=1)\
            #     if common_base[l,k] <p3 else 3 + within_noise *numpy.random.uniform(low=-1,high=1 ,size=1)  for k in range(N)]
            Y[i]= [ 2.0 +within_noise *numpy.random.uniform(low=-1,high=1 ,size=1) if common_base[l,k] < p1 else  1.0 + within_noise *numpy.random.uniform(low=-1,high=1 ,size=1)\
                if common_base[l,k] < p2 else  3.0 + within_noise *numpy.random.uniform(low=-1,high=1 ,size=1) if common_base[l,k] < p3  else
                0.0 + within_noise *numpy.random.uniform(low=-1,high=1 ,size=1) for k in range(N)]
        elif association_type == "L":
            Y[i] = [ common_base_Y[l,k] + within_noise * numpy.random.uniform(low=-1,high=1, size=1) for k in range(N)]
            #Y[j]= [ numpy.random.uniform(low=10,high=100, size=1) * common_base[l,k] if common_base[l,k] < -0.8 else numpy.random.uniform(low=.2,high=.5, size=1) for k in range(N)]
        elif association_type =="happyface":
            Y[i] = [ happyface(common_base[l,k]) + within_noise * numpy.random.uniform(low=-.1,high=.1, size=1) for k in range(N)]
            
        for index,b in enumerate(noise_num):
            Y[i][b] = Y[i][index]
        assoc2[l].append(i)

    for a in range(number_associated_blocks):
        #print assoc1[a], assoc2[a]
        for i, j in itertools.product(assoc1[a], assoc2[a]):
            A[i][j] = 1
    return X,Y,A

def balanced_synthetic_dataset_uniform(  D, N, B, within_noise = 0.5, between_noise = 0.1, cluster_percentage = 1, association_type = 'parabola' ):
    """
        D: int
            number of features

        N: int
            number of samples 

        B: int
            number of blocks 
    """
    
    
    X = numpy.random.uniform(low=-1,high=1,size=(D,N))
    Y = numpy.random.uniform(low=-1,high=1,size=(D,N))
    A = numpy.zeros( (len(X),len(Y)) )
    blockSize = int(round(D/B+.5))
    print (D, B, blockSize)
    if association_type == "L":
        common_base = numpy.hstack((numpy.random.uniform(low=-1.0,high=-1.0 ,size=(B+1,N/2)), numpy.random.uniform(low=-1,high=10 ,size=(B+1,N/2))))
        for l in range(B+1):
            common_base[l]= numpy.random.permutation(common_base[l])
    else:
        common_base = numpy.random.uniform(low=-1,high=1 ,size=(B+1,N))
    common_base = orthogonalize_matrix(common_base)
    
    assoc = [[] for i in range((B+1))]
    l = 0
    for i in range(0,int(D*cluster_percentage),blockSize):
        for j in range(i,i+blockSize):
            if j < D:
                numpy.random.seed(j)
                if association_type == "L":
                    X[j]= [common_base[l,k]+ within_noise * numpy.random.uniform(low=-.1,high=.1, size=1) for k in range(N)]
                elif association_type == "log":
                    X[j]= [math.fabs(common_base[l,k])  + within_noise * numpy.random.uniform(low=0,high=1 ,size=1) for k in range(N)]
                else:    
                    X[j]= [common_base[l,k]  + within_noise * numpy.random.uniform(low=-1,high=1 ,size=1) for k in range(N)]
                assoc[l].append(j)
        l += 1
    if association_type == "L":
        common_base_Y = numpy.random.uniform(low=-1,high=1 ,size=(B+1,N))
        for l in range(B+1):
            common_base_Y[l] = [numpy.random.uniform(low=l,high=10, size=1)  if common_base[l,k] < -0.99 else l+ within_noise * numpy.random.uniform(low=-.1,high=.1, size=1) for k in range(N)]

    l= 0
    for i in range(0,int(D*cluster_percentage),blockSize):
        numpy.random.seed()
        noise_num = numpy.random.randint(N, size=int(N*between_noise))
        for j in range(i,i+blockSize):
            if j < D:
                numpy.random.seed()
                if association_type == "parabola":
                    Y[j]= [common_base[l,k]*common_base[l,k]  + within_noise *math.sqrt(math.fabs(numpy.random.uniform(low=-1,high=1 ,size=1))) for k in range(N)]
                elif association_type == "line":
                    Y[j]= [common_base[l,k]  + within_noise * numpy.random.uniform(low=-1,high=1 ,size=1) for k in range(N)]
                elif association_type == "sine":
                    Y[j]= [.5* math.sin(math.pi * common_base[l,k]*1.5)  + within_noise * numpy.random.uniform(low=-1,high=1 ,size=1)  for k in range(N)]
                elif association_type == "log":
                    Y[j]= [math.log(math.fabs(common_base[l,k]))  + within_noise *math.fabs(numpy.random.uniform(low=0,high=1 ,size=1)) for k in range(N)]
                elif association_type == "step":
                    p1 = numpy.percentile(common_base[l], 25)
                    p2 = numpy.percentile(common_base[l], 50)
                    p3 = numpy.percentile(common_base[l], 75)
                    #NOISE = within_noise *numpy.random.uniform(low=-1,high=1 ,size=1)
                    #Y[j]= [ 0 if common_base[l,k] <p1 else  1 + within_noise *numpy.random.uniform(low=-1,high=1 ,size=1)\
                    #     if common_base[l,k] <p2 else 2+within_noise *numpy.random.uniform(low=-1,high=1 ,size=1)\
                    #     if common_base[l,k] <p3 else 3 + within_noise *numpy.random.uniform(low=-1,high=1 ,size=1)  for k in range(N)]
                    Y[j]= [ 2.0 +within_noise *numpy.random.uniform(low=-1,high=1 ,size=1) if common_base[l,k] < p1 else  1.0 + within_noise *numpy.random.uniform(low=-1,high=1 ,size=1)\
                        if common_base[l,k] < p2 else  3.0 + within_noise *numpy.random.uniform(low=-1,high=1 ,size=1) if common_base[l,k] < p3  else
                        0.0 + within_noise *numpy.random.uniform(low=-1,high=1 ,size=1) for k in range(N)]
                elif association_type == "L":
                    Y[j] = [ common_base_Y[l,k] + within_noise * numpy.random.uniform(low=-1,high=1, size=1) for k in range(N)]
                    #Y[j]= [ numpy.random.uniform(low=10,high=100, size=1) * common_base[l,k] if common_base[l,k] < -0.8 else numpy.random.uniform(low=.2,high=.5, size=1) for k in range(N)]
                elif association_type =="happyface":
                    Y[j] = [ happyface(common_base[l,k]) + within_noise * numpy.random.uniform(low=-.1,high=.1, size=1) for k in range(N)]
                    
                for index,b in enumerate(noise_num):
                    Y[j][b] = Y[j][index]
        l += 1
    for r in range(0,B+1):
        for i, j in itertools.product(assoc[r], assoc[r]):
            A[i][j] = 1
    return X,Y,A
def balanced_synthetic_dataset_norm( D, N, B, within_noise = 0.5, between_noise = 0.1, cluster_percentage = 1, association_type = 'parabola' ):
    """
        D: int
            number of features

        N: int
            number of samples 

        B: int
            number of blocks 
    """
    X = numpy.random.normal(0, 1,size=(D,N))
    common_base = numpy.random.normal(0, 1,size=(B+1,N))
    common_base = orthogonalize_matrix(common_base)
    Y = numpy.random.normal(0, 1,size=(D,N))
    A = numpy.zeros( (len(X),len(Y)) )
    blockSize = int(round(D/B+.5))
    print (D, B, blockSize)
    assoc = [[] for i in range((B+1))]
    l = 0
    for i in range(0, int(D*cluster_percentage), blockSize):
        numpy.random.seed()
        for j in range(i,i+blockSize):
            if j < D :
                X[j]= [common_base[l,k]  + numpy.random.normal(0, within_noise, size=1) for k in range(N)]
                assoc[l].append(j)
        l += 1
    l= 0
    for i in range(0, int(D*cluster_percentage), blockSize):
        #print N, int(N*between_noise)
        numpy.random.seed()
        noise_num = numpy.random.randint(N, size= int(N*between_noise) )
        #print noise_num
        for j in range(i,i+blockSize):
            if j < D :
                #print j, i
                Y[j]= [common_base[l,k]  + numpy.random.normal(0, within_noise,size=1) for k in range(N)]
                for index,b in enumerate(noise_num):
                    Y[j][b] = Y[j][index]#print l
        l += 1
        
    for r in range(0,B+1):
        for i, j in itertools.product(assoc[r], assoc[r]):
            A[i][j] = 1
    return X,Y,A    
def imbalanced_synthetic_dataset_norm(  D, N, B, within_noise = 0.5, between_noise = 0.1, association_type = 'parabola' ):
    """
        D: int
            number of features

        N: int
            number of samples 

        B: int
            number of blocks 
    """
    X = numpy.random.normal(0, 1,size=(D,N))
    X_base = numpy.random.normal(0, 1,size=(D,N))
    common_base = numpy.random.normal(0, 1,size=(B+1,N))
    common_base = orthogonalize_matrix(common_base)
    Y = numpy.random.normal(0, 1,size=(D,N))
    Y_base = numpy.random.normal(0, 1,size=(D,N))
    A = numpy.zeros( (len(X),len(Y)) )
    blockSize = int(round(D/B+.5))
    #print D, B, blockSize
    
    
    number_associated_blocks = max([int(B/4) , 1])
    assoc1 = [[] for i in range(number_associated_blocks)]
    assoc2 = [[] for i in range(number_associated_blocks)]
    
    for i in range(D):
        r = randrange(0,B)
        X[i]= [X_base[r,k]  + within_noise * numpy.random.normal(0, within_noise, size=1) for k in range(N)]
        
    for i in range(D):
        r = randrange(0,B)
        Y[i]= [Y_base[r,k]  + within_noise * numpy.random.normal(0, within_noise, size=1) for k in range(N)]
        
    r = numpy.random.randint(D, size=int(blockSize* number_associated_blocks))
    for i in r:
        l= randrange(0,int(number_associated_blocks))
        X[i]= [common_base[l][k] +  within_noise * numpy.random.normal(0, within_noise, size=1) for k in range(N)]
        assoc1[l].append(i)
    
    noise_num = numpy.random.randint(N, size=int(N*between_noise))
    for i in r:
        numpy.random.seed()
        l= randrange(0,int(number_associated_blocks))
        #slope = 1.0 +numpy.random.random_sample()#slope = numpy.random.random_sample()
        if association_type == "parabola":
            Y[i]= [common_base[l][k] * common_base[l][k]  + within_noise * math.sqrt(math.fabs(numpy.random.normal(0, within_noise, size=1)))  for k in range(N)]
            for index,b in enumerate(noise_num):
                Y[i][b] = Y[i][index]
            assoc2[l].append(i)
        elif association_type == "linear":
            Y[i]= [common_base[l][k] + within_noise * numpy.random.normal(0, within_noise, size=1)  for k in range(N)]
            for index,b in enumerate(noise_num):
                Y[i][b] = Y[i][index]
            assoc2[l].append(i)

    for a in range(number_associated_blocks):
        #print assoc1[a], assoc2[a]
        for i, j in itertools.product(assoc1[a], assoc2[a]):
            A[i][j] = 1
    return X,Y,A 
def main():
    pass
if __name__ == "__main__":
    main( )   