#! usr/bin/python3                                                                                                                              

import ld

Sig=[]
with open(input('Input file with significant SNPs: ')) as f: #INPUT significant snps file
    for line in f.readlines():
        Sig.append(line.rstrip())
        

cl=[]
cs=[]
with open(input('Input control data: ')) as f: 
    for line in f.readlines():
        cl.append(line.split())
        
with open(input('Input cases data: ')) as f:
    for line in f.readlines():
        cs.append(line.split())

All=[]
for l in cl:
    All.append(l[0]) #this list includes all the samples for all the snps

'''
The following loop compares pairwise each significant snp with its neighbours.
To do that we set a limit. Lets say our significant snp is "snp4". If the limit is 3
the loop will check for snps with numbers between [1,3] and [5,7] 
and perform an LD check for each with the snp4. 
The LD list is appended only if the r value is bigger than 0.8 (or whatever threshold we choose)
Then a condition follows and if the LD is determined to be empty 
(which means no r value was found bigger than 0.8 hence no LD between any of its neighbours) 
it will break and go for the next significant snp.

But if it is not empty, then we set a bigger limit while keeping the old one so as to check the next neighbours
We keep the old one so as to apply a condition where the snps we have already checked will not be checked again
(apart from saving time, this will save us from an infinite loop)

There are two loops one for each side, left and right.
'''
threshold=int(input('Set threshold for bin size of LD checks: ')) 
rlimit=float(input('Set the minimum r^2 value that will define an LD occurence: '))
with open('LDanalysis.txt', 'w') as output:
    output.write('')
for s in Sig:
    Limit=threshold #This is what will determine how big the bin will be for checking neighbouring LDs
    OldLimit=0
    LD={}
    LD[s]=[]
    while True:
        lLD=[] #the temporal LD list will reset in each loop until it can no longer find new snps with LD
        for x in All:
            if int(x[4:])<(int(s[4:])-Limit): #this is not necessary, but it probably saves time
                 continue
            if OldLimit!=0 and int(x[4:])>=(int(s[4:])-OldLimit): #this is extremely important as it skips lines checked in a previous loop
                 break
            if int(x[4:])==int(s[4:]): #the left side stops here 
                 break
            if int(x[4:])>=(int(s[4:])-Limit): #in order to get the nearby snps
                 Dp,r = ld.ld(s,x,cl,cs)
                 
                 if r>rlimit:
                     lLD.append(x)
        if lLD==[]:
            break
        else:
            LD[s].append(lLD)
            OldLimit=Limit #the old limit will help us skip previous LD checks
            Limit=Limit+threshold

    with open('LDanalysis.txt', 'a') as output:
        output.write(str(LD)+'\n')
    
    #the following is the same as above but for the right side, so some conditions change
    Limit=threshold #This is what will determine how big the bin will be for checking neighbouring LDs
    OldLimit=0
    LD={}
    LD[s]=[]
    while True:
        rLD=[] 
        for x in All:            
            if int(x[4:])<=int(s[4:]): #we skip all snps until we reach the significant
                continue
            if OldLimit!=0 and int(x[4:])<=(int(s[4:])+OldLimit):
                continue
                 
            if int(x[4:])<=(int(s[4:])+Limit): #we check the ones that are on the right side within the limit
                 Dp,r = ld.ld(s,x,cl,cs)
                 if r>rlimit:
                     rLD.append(x)
        if rLD==[]:
            break
        else:
            LD[s].append(rLD)
            OldLimit=Limit #the old limit will help us skip previous LD checks
            Limit=Limit+threshold

    with open('LDanalysis.txt', 'a') as output:
        output.write(str(LD)+'\n')