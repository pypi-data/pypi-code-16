import numpy as np
import os
from kmeans import kmeans

# Read in data
f = open('afdata/places.txt', 'r')
data_objects = np.loadtxt(f, delimiter=',')
f.close()

# Perform the clustering
assignments = kmeans(data_objects, 3, 1000)

# Write output
f = open('afdata/clusters.txt', 'w')
for i, assignment in enumerate(assignments):
    f.write('{0} {1}'.format(i, assignment))
    if i < (len(assignments) - 1):
        f.write('\n')
f.close()
