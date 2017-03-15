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
from Universe import universe
from Reporting import error, report
from GmshData import Mesh

class H2Ocean(object):

    def __init__(self, spatial_discretisation=None, representation=None, mesh=None, folder=None):
        self.spatial_discretisation = spatial_discretisation
        self.representation = representation
        self.mesh_source = mesh
        self.mesh = None
        self.folder = self.OutputFolder(folder)
        self.Output()

    def OutputFolder(self, folder=None):
        from os.path import exists
        if folder is None:
            folder = './'
        if self.representation is not None:
            fullpath = self.spatial_discretisation.PathRelative(folder)
        else:
            fullpath = folder
        return fullpath

    def Output(self):
        path = '/postprocess/format/h2ocean'
        #if specification.have_option('%(path)s/value' % {'path':path}):
        #  value = specification.get_option('%(path)s/value' % {'path':path})
        report('%(blue)sWriting H2Ocean output to folder:%(end)s %(yellow)s%(folder)s%(end)s', var = {'folder':self.folder}, indent=1) 
        self.mesh = Mesh()
        self.mesh.read(self.mesh_source.Output())

        self.boundary = self.DetermineBoundaryNodes()

        self.WriteElementFile()
        self.WriteNodeFile()
        self.WriteWaterLevelInitFile()
        self.WriteBathymetryFile()

    def WriteNodeFile(self):
        from os import linesep
        nodes = self.mesh.nodes
        filename = self.folder + '/nod2D.txt'
        report('%(blue)sWriting H2Ocean node file:%(end)s %(yellow)s%(filename)s%(end)s', var = {'filename': filename}, indent=2) 
        f = open(filename, 'w')
        f.write( ( '%(node_total_number)d 2 0 1' + linesep ) % {'node_total_number':len(nodes)})
        for i in range(len(nodes)):
            # Number in [0,1,3] - whether ocean, boundary (type?), dry?
            end = self.GetIdentity(i + 1)
            position = nodes[i + 1]
            f.write( ( '%(node_number)d %(x)f %(y)f %(end)d' + linesep ) % {'node_number':i + 1, 'x':position[0], 'y':position[1], 'end':end})
        f.close()
        # Add comments

    def DetermineBoundaryNodes(self):
        elements = self.mesh.elements
        boundary = {}
        for i in range(len(elements)):
            entry = elements[i + 1]
            if entry[0] != 1: continue
            identity = entry[1][0]
            nodes = entry[2]
            if identity not in boundary.keys():
                boundary[identity] = []
            for node in nodes:
                if node not in boundary[identity]:
                    boundary[identity].append(node)
        # print boundary.keys()
        # for identity in boundary.keys():
        #   print identity, boundary[identity]
        return boundary

    def GetIdentity(self, node):
        for identity in self.boundary.keys():
            if node in self.boundary[identity]:
                return identity
        return 0

    def WriteElementFile(self):
        from os import linesep
        elements = self.mesh.elements
        filename = self.folder + '/elem2D.txt'
        report('%(blue)sWriting H2Ocean element file:%(end)s %(yellow)s%(filename)s%(end)s', var = {'filename': filename}, indent=2) 
        f = open(filename, 'w')
        e = []
        for i in range(len(elements)):
            entry = elements[i + 1]
            if entry[0] != 2: continue
            connectivity = entry[2]
            e.append(connectivity)
        f.write( ( '%(element_total_number)d  3  0' + linesep ) % {'element_total_number':len(e)})
        for i in range(len(e)):
            connectivity = e[i]
            f.write( ( '%(element_number)d %(a)d %(b)d %(c)d' + linesep ) % {'element_number':i+1, 'a':connectivity[0], 'b':connectivity[1], 'c':connectivity[2]})
        f.write('Generated by Shingle') # Add futher comments?
        f.close()

    def WriteWaterLevelInitFile(self):
        from os import linesep
        from numpy import zeros, array, size
        nodes = self.mesh.nodes
        filename = self.folder + '/Init.txt'
        report('%(blue)sWriting H2Ocean water level init file:%(end)s %(yellow)s%(filename)s%(end)s', var = {'filename': filename}, indent=2) 
        f = open(filename, 'w')
        f.write( ( '%(node_total_number)d' + linesep ) % {'node_total_number':len(nodes)})



        sys.path.insert(0, os.path.realpath(os.path.expanduser('~/tmp/src/fluidity/python')))
        import vtktools
        datafile = os.path.expanduser('~/tmp/dataset/chile/uplistdata.vtu')
        data = vtktools.vtu(datafile)





        loc = zeros([len(nodes), 3], float)
        for i in range(size(loc,0)):
            position = nodes[i+1]
            loc[i,:] = [position[0], position[1], 0.0]

        #print loc

        field = data.ProbeData(loc, 'Eta')

        #print field

        for i in range(len(nodes)):
            position = nodes[i + 1]
            longitude = position[0]
            latitude  = position[1]
            eta = field[i]



            f.write( ( '%(eta)f' + linesep ) % {'eta':eta})
        f.close()
        # Add comments

    def WriteBathymetryFile(self):
        from os import linesep
        nodes = self.mesh.nodes
        filename = self.folder + '/Bathymetry.txt'
        report('%(blue)sWriting H2Ocean bathymetry file:%(end)s %(yellow)s%(filename)s%(end)s', var = {'filename': filename}, indent=2) 
        f = open(filename, 'w')
        f.write( ( '%(node_total_number)d' + linesep ) % {'node_total_number':len(nodes)})

        import era

        filename='/Users/acandy/tmp/dataset/chile/ChilePacificWide.nc'
        data = era.Era15(filename=filename, longitudeName='lon', latitudeName='lat')
        time = 0.0
        fieldname = 'z'

        for i in range(len(nodes)):
            position = nodes[i + 1]
            longitude = position[0]
            latitude  = position[1]
            bathymetry = data.InterpolatedValue(fieldname, latitude, longitude, time)
            #print( ( '%(number)d %(longitude)f %(latitude)f %(bathymetry)f' ) % {'bathymetry':bathymetry, 'number':i+1, 'longitude':longitude, 'latitude':latitude})

            # TODO: Interpolation
            #  use vtk intermediate?  - see Greenland scripts
            f.write( ( '%(bathymetry)f' + linesep ) % {'bathymetry':bathymetry})
        f.close()
        # Add comments

















