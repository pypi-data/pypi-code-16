#!/usr/bin/env python
# -*- coding: utf-8 -*-

##########################################################################
#  
#  Copyright (C) 2011-2016 Dr Adam S. Candy
# 
#  Shingle:  An approach and software library for the generation of
#            boundary representation from arbitrary geophysical fields
#            and initialisation for anisotropic, unstructured meshing.
# 
#            Web: https://www.shingleproject.org
#
#            Contact: Dr Adam S. Candy, contact@shingleproject.org
#
#  This file is part of the Shingle project.
#  
#  Shingle is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  
#  Shingle is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with Shingle.  If not, see <http://www.gnu.org/licenses/>.
#
##########################################################################

import os
import sys
sys.path.insert(0, os.path.realpath(os.path.join(os.path.realpath(os.path.dirname(os.path.realpath(__file__))), os.path.pardir)))
from Reporting import error, report

#from Reporting import report, error

class Mesh:
    """This is a class for storing nodes and elements.

    Members:
    nodes -- A dict of the form { nodeID: [ xcoord, ycoord, zcoord] }
    elements -- A dict of the form { elemID: (type, [tags], [nodeIDs]) }

    Methods:
    read(file) -- Parse a Gmsh version 1.0 or 2.0 mesh file
    write(file) -- Output a Gmsh version 2.0 mesh file
    """

    def __init__(self):
        self.nodes = {}
        self.elements = {}

    def readbinary(self, mshfile):
        import struct
        #print 'Binary read'
        error = 0
        readmode = 0
        report('%(blue)sReading mesh file:%(end)s %(yellow)s%(filename)s%(end)s', var = {'filename': mshfile.name}, indent=1) 

        mshfile.readline()
        mshfile.readline()
        mshfile.readline()
        mshfile.readline()
        mshfile.readline()
        totalnodes = int(mshfile.readline())

        #byte = mshfile.read(1)
        for j in range(totalnodes):
            n = struct.unpack('i', mshfile.read(4))[0]
            pos = struct.unpack('ddd', mshfile.read(24))
            #print struct.unpack('d', mshfile.read(8))[0]
            #print struct.unpack('d', mshfile.read(8))[0]
            #print struct.unpack('iddd', mshfile.read(28))[0]
            #print n, pos
            self.nodes[n] = pos
        #while byte != b"":
        #  # Do stuff with byte.
        #  byte = f.read(1)

        mshfile.readline()
        mshfile.readline()
        mshfile.readline()
        totalelements = int(mshfile.readline())

        eletype  = {1:'line', 2:'triangle', 3:'quad', 4:'tet', 5:'hex', 6:'prism', 7:'pyramid' }
        elenodes = {1:2     , 2:3         , 3:4     , 4:4    , 5:8    , 6:6      , 7:5         }

        #for j in range(totalelements):
        #for j in range(1):
        ele = 0
        while ele <= totalelements:
            elmtype = struct.unpack('i', mshfile.read(4))[0]
            nele = struct.unpack('i', mshfile.read(4))[0]
            ntags = struct.unpack('i', mshfile.read(4))[0] 

            for n in range(nele):
                id  = struct.unpack('i', mshfile.read(4))[0] 
                tags = []
                for i in range(ntags):
                    tags.append(struct.unpack('i', mshfile.read(4))[0]) 
                nodes = []
                for i in range(elenodes[elmtype]):
                    nodes.append(struct.unpack('i', mshfile.read(4))[0]) 

                self.elements[id] = (elmtype, tags, nodes)
                ele = ele + 1
                #print ele, id, self.elements[id]
                if ele == totalelements:
                    break
            if ele == totalelements:
                break

        #print 'Total nodes:', totalnodes
        #print 'Total elements:', totalelements


    def read(self, filename, binary=False):
        """Read a Gmsh .msh file.

        Reads Gmsh format 1.0 and 2.0 mesh files, storing the nodes and
        elements in the appropriate dicts.
        """
        # May need to open with 'b' here?
        mshfile = open(filename, 'r')
        if binary:
            self.readbinary(mshfile)
        else:
            self.readplain(mshfile)
        mshfile.close()

    def readplain(self, mshfile, binary=False):
        error = 0
        readmode = 0
        nodedata = ''
        report('%(blue)sReading mesh file:%(end)s %(yellow)s%(filename)s%(end)s', var = {'filename': mshfile.name}, indent=1) 
        for line in mshfile:
            line = line.strip()
            if line.startswith('$'):
                #print '-  ', line
                if line == '$NOD' or line == '$Nodes':
                    readmode = 1
                    totalread = False
                elif line == '$ELM':
                    readmode = 2
                elif line == '$Elements':
                    readmode = 3
                    totalread = False
                elif line == '$EndNodes':
                    if not binary:
                        continue
                    #print 'nodedata', nodedata
                    #print len(nodedata)
                    floatlength = ((len(nodedata) / totalnodes) - 4 ) / 3
                    i = 27
                    #4 + 3 * 8
                    for j in range(128):
                        #print i, struct.unpack('i', nodedata[i:i+4])[0]
                        i = i + 28

                    #print struct.unpack('iddd', nodedata[i:i+28])
                    i = i + 32
                    #print struct.unpack('iddd', nodedata[i:i+32])
                    i = i + 4
                    #print struct.unpack('d', nodedata[i:i+8])


                else:
                    readmode = 0
            elif readmode:
                #print readmode, ' - ', line
                if readmode == 1:
                    if not totalread:
                        totalnodes = int(line)
                        totalread = True
                        #print 'Total nodes:', totalnodes
                        #report('%(blue)sTotal nodes:%(end)s %(yellow)s%(totalnodes)d%(end)s', var = {'totalnodes': totalnodes}, indent=2) 
                        continue

                    if binary:
                        #print line
                        nodedata = nodedata + line

                    if not binary:
                        # ascii
                        columns = line.split()
                        if len(columns) == 4:
                            # Version 1.0 or 2.0 Nodes
                            try:
                                self.nodes[int(columns[0])] = map(float, columns[1:])
                            except ValueError:
                                print 'read error'
                                print('Node format error: '+line, ERROR)
                                readmode = 0
                                error = error + 1
                elif readmode > 1:
                    if not totalread:
                        totalelements = int(line)
                        totalread = True
                        #report('%(blue)sTotal elements:%(end)s %(yellow)s%(totalelements)d%(end)s', var = {'totalelements': totalelements}, indent=2) 
                        continue

                    if not binary:
                        # ascii 
                        columns = line.split()
                        if len(columns) > 5:
                            # Version 1.0 or 2.0 Elements 
                            try:
                                columns = map(int, columns)
                            except ValueError:
                                print('Element format error: '+line, ERROR)
                                readmode = 0
                                error = error + 1
                            else:
                                (id, type) = columns[0:2]
                                if readmode == 2:
                                    # Version 1.0 Elements
                                    tags = columns[2:4]
                                    nodes = columns[5:]
                                else:
                                    # Version 2.0 Elements
                                    ntags = columns[2]
                                    tags = columns[3:3+ntags]
                                    nodes = columns[3+ntags:]
                                self.elements[id] = (type, tags, nodes)
        #print('  %d Nodes'%len(self.nodes))
        #print('  %d Elements'%len(self.elements))
        report('%(blue)sDiscretisation characteristics:%(end)s %(yellow)s%(nodes)d%(end)s %(blue)snodes,%(end)s %(yellow)s%(yellow)s%(elements)d%(end)s %(blue)selements%(end)s', var = {'nodes': len(self.nodes), 'elements': len(self.elements)}, indent=2) 
        return error

    def write(self, file):
        """Dump the mesh out to a Gmsh 2.0 msh file."""
        f = open (file, 'w')
        f.write('$MeshFormat\n2.0 0 8\n$EndMeshFormat')
        f.write('$Nodes\n%d'%len(self.nodes))
        for (id, coord) in self.nodes.items():
            f.write(id, ' '.join(map(str, coord)))
        f.write('$EndNodes')
        f.write('$Elements\n%d'%len(self.elements))
        for (id, elem) in self.elements.items():
            (type, tags, nodes) = elem
            f.write(id, type, len(tags) + ' '.join(map(str, tags)) + ' '.join(map(str, nodes)))
        f.write('$EndElements')
        f.close()


