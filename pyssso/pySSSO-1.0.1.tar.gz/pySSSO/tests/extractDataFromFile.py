#!/usr/bin/env python

"""
  This script takes two arguments:
     - input ASCII file
     - word
  and searches all the lines that have the word.
  The lines of interest are written out in a new file.
     
"""

import sys

inFileName1 = sys.argv[1]
inFileName2 = sys.argv[2]

# Compiling species list
#-----------------------
speciesNames = []
f1 = open(inFileName1, 'r')

for line in f1:
    if "max = " in line:
       # get rid of the \n character
       line = line.strip()
       # split the line into a list
       newList = line.split()
       if (newList[1] != "max"):
          name = newList[0] + ' ' + newList[1]
          if (name not in speciesNames):
             speciesNames.append(name)
       else:
          name = newList[0]
          if (name not in speciesNames):
             speciesNames.append(name)

f1.close()

print speciesNames

maxRef = []
minRef = []
maxMod = []
minMod = []

# Min/Max from the Reference File
#--------------------------------

f1 = open(inFileName1, 'r')
for line in f1:
    if (" max = " in line):
       # get rid of the \n character
       line = line.strip()
       # split the line into a list
       newList = line.split()
       if (newList[1] != "max"):
          maxRef.append(float(newList[4]))
          minRef.append(float(newList[7]))
       else:
          maxRef.append(float(newList[3]))
          minRef.append(float(newList[6]))

f1.close()

print

# Min/Max from the Modified File
#--------------------------------

f2 = open(inFileName2, 'r')
for line in f2:
    if (" max = " in line):
       # get rid of the \n character
       line = line.strip()
       # split the line into a list
       newList = line.split()
       if (newList[1] != "max"):
          maxMod.append(float(newList[4]))
          minMod.append(float(newList[7]))
       else:
          maxMod.append(float(newList[3]))
          minMod.append(float(newList[6]))

f2.close()

n = len(speciesNames)

#print len(speciesNames), len(maxMod), len(minMod), len(maxRef), len(minRef)

print "%s" %(92*"-")
print "%-13s %25s %25s %25s" %("Species Name", "Max Reference", "Max-Modified", "Difference")
print "%s" %(92*"-")

num = 0
for k in range(n):
    m = k + n
    diff = maxRef[m]-maxMod[m]
    if (diff != 0.0):
       num += 1
       print "%-13s %25.15E %25.15E %25.15E" %(speciesNames[k], maxRef[m], maxMod[m], diff)

print
print "%d species changed and %d did not!" %(num, n-num)
print

num = 0
print "%s" %(92*"-")
print "%-13s %25s %25s %25s" %("Species Name", "Min Reference", "Min-Modified", "Difference")
print "%s" %(92*"-")

for k in range(n):
    m = k + n
    diff = minRef[m]-minMod[m]
    if (diff != 0.0):
       num += 1
       print "%-13s %25.15E %25.15E %25.15E" %(speciesNames[k], minRef[m], minMod[m], diff)

print
print "%d species changed and %d did not!" %(num, n-num)
print
