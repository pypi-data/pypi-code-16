#!/usr/bin/python

import sys
import os

# setting all required environment variables
os.environ['PYTHONPATH'] = '/home/user/fitgcp:'+os.environ.get('PYTHONPATH','')

print """
Welcome to the GASiC tutorial
-----------------------------"""
print """
In this tutorial, you will learn how you can use fitGCP on
this virtual machine. We will step though the whole fitGCP
proces and analyze some example data.
"""

while not os.path.exists('/home/user/experiment/exp1.sam'):
    print """
Before we start, you have to initially set up the example
environment by clicking the Desktop button 'Extract Example
Experiment'. Press [Return] when you are finished or 
[Ctrl + C] to abort."""
    raw_input()

print "Now, we change to the directory containing the data:"

print "> cd /home/user/experiment"
os.chdir("/home/user/experiment")

if not os.path.exists('/home/user/experiment/fitGCP.py'):
    print """
To run fitGCP, we have to create a link to the original 
script first:
> ln /home/user/fitgcp/fitGCP.py fitGCP.py
""",
    raw_input()
    os.system('ln /home/user/fitgcp/fitGCP.py /home/user/experiment/fitGCP.py')

print """
This directory contains two SAM files; one from the first 
experiment and the other from the third experiment in the 
fitGCP paper.
> ls -lh
"""
os.system('ls -lh')
print """
Press [Return] to continue."""
raw_input()
print """
We start analyzing the SAM file from the first experiment.

First, we want to take a look at the genome coverage profile
(GCP) and decide which model to fit. This can be done with
the --view option (this may take a while):
> python fitGCP.py --view exp1.sam""",
raw_input()
print
os.system('python fitGCP.py --view exp1.sam')

print """
Let us take a look at the GCP:
> eog exp1.png""",
raw_input()
print
os.system('eog exp1.png')

print """
We observed two peaks, lets try two poisson distributions.
Thus, we specify the model: -d pp
-p creates the plot, -c 0.995 sets a better coverage cutoff.
> python fitGCP.py -p -c 0.995 -d pp exp1.sam""",
raw_input()
print
os.system('python fitGCP.py -p -c 0.995 -d pp exp1.sam')
print """
Let us take a look at the GCP:
> eog exp1_pp.png""",
raw_input()
print
os.system('eog exp1_pp.png')
print """
A more complex model can improve the fit quality here. Lets
try -d zpnt, including a zero, poisson and negative binomial 
distribution with tail. We can also set the start parameters
for the first distribution (poisson) to 1.0 and for the 
second distribution to 10.0 using -m two times. Produce more
accurate fits this time (-t 0.001):
> python fitGCP.py -p -c 0.995 -t 0.001 -d zpnt -m 1.0 -m 10.0 exp1.sam""",
raw_input()
os.system('python fitGCP.py -p -c 0.995 -t 0.001 -d zpnt -m 1.0 -m 10.0
exp1.sam')
print """
Let us take a look at the GCP:
> eog exp1_zpnt.png""",
raw_input()
print
os.system('eog exp1_zpnt.png')
print """
This looks very nice now and we are finished. The results in 
the text files can now be used for further analysis tasks.

Try fitGCP out on the Ruminococcus file!
(Hint: a less complex model is sufficient here)
"""
raw_input()
sys.exit(1)

