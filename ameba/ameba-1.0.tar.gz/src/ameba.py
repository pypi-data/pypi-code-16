#!/usr/bin/env python
#-*- coding:utf-8 -*-

# Copyright 2012-2014 Rene Rex and Alexander Riemer

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

#Dieses Programm ist Freie Software: Sie können es unter den Bedingungen
#der GNU General Public License, wie von der Free Software Foundation,
#Version 3 der Lizenz oder (nach Ihrer Option) jeder späteren
#veröffentlichten Version, weiterverbreiten und/oder modifizieren.

#Dieses Programm wird in der Hoffnung, dass es nützlich sein wird, aber
#OHNE JEDE GEWÄHRLEISTUNG, bereitgestellt; sogar ohne die implizite
#Gewährleistung der MARKTFÄHIGKEIT oder EIGNUNG FÜR EINEN BESTIMMTEN ZWECK.
#Siehe die GNU General Public License für weitere Details.

#Sie sollten eine Kopie der GNU General Public License zusammen mit diesem
#Programm erhalten haben. Wenn nicht, siehe <http://www.gnu.org/licenses/>.

'''AMEBA: Advanced MEtabolic Branchpoint Analysis'''

__author__ = "Rene Rex"
__version__ = "2014.08.12.1425"

programName = "AMEBA: Advanced MEtabolic Branchpoint Analysis"

import sys
import os

import argparse
from copy import deepcopy, copy
from collections import deque
from ConfigParser import NoOptionError, NoSectionError, ParsingError, SafeConfigParser

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk # use GTK+ 3
import networkx as nx
from xdot import DotWindow

try:
    from metano.metabolicmodel import MetabolicModel
    from metano.metabolicflux import MetabolicFlux
    from metano.reactionparser import ReactionParser
except ImportError:

    try:
        from metabolicmodel import MetabolicModel
        from metabolicflux import MetabolicFlux
        from reactionparser import ReactionParser
#        print >> sys.stderr, "Warning: metano package not available - using legacy metano modules."
    except ImportError as e:

        sys.exit("Sorry, BPA requires metano >= 0.9. Please install it "
                 "from metano.tu-bs.de and add it to your python path.\n"
                 "Original error message: "+e.message)

edgeWidth = 3
edgeColor =	"#000000"
edgeArrow = "standard"
newline = "&#010;" # ISO 8859-1, required by the GML specification

substanceShape = "rectangle"
defaultSubstanceColor = "#A9DDFC"

reactionShape = "roundrectangle"
defaultReactionColor = "#FFFF66"

edgeGraphics = {
                    # gml
                    "graphics": {
                        "width":edgeWidth,
                        "fill":edgeColor,
                        "targetArrow":edgeArrow
                     },
                     # graphviz defaults are ok

                }

edgeGraphicsIntermediate = {
                    # gml
                    "graphics": {
                        "width":edgeWidth,
                        "fill":"#808080",
                        "targetArrow":edgeArrow,
                        "style":"dashed"
                         },
                     # graphviz
                     "style":"dashed"
                }


class BPAconfiguration(object):

    def __init__(self):

        self.clear_and_rebuild()

    def clear_and_rebuild(self):

        self.maxDepth = 2
        self.exclude = []
        self.disconnect = []
        self.disconnectOtherMetabolites = False
        self.deleteIntermediates = True
        self.largestComponentOnly = True
        self.difference = False
        self.threshold = 0.
        self.outputFile = None
        self.showLabels = True
        self.showAbsoluteFluxes = True
#        self.removeDeadEnds = False
        self.postReduceFunction = None
        self.removeNodesWithNoFlux = True
        self.substanceColor = defaultSubstanceColor
        self.reactionColor = defaultReactionColor

    def toString(self):

        return "\n".join(p+": "+str(v) for p,v in vars(self).iteritems())

    def setConfigFromFile(self, configFile):

        # default to the current attributes of the configuration object
        defaultConfig = dict((p, str(v)) for p,v in vars(self).iteritems())
        # fix the string representation of the lists
        defaultConfig["exclude"] = ", ".join(self.exclude)
        defaultConfig["disconnect"] = ", ".join(self.disconnect)

        try:
            configparser = SafeConfigParser(defaultConfig)
            configparser.read(configFile)

        except ParsingError as e:
            print e
            print "Please check the configuration file."
            exit()

        try: # TODO use attribute iteration, too?
            maxDepth = configparser.get("bpa", "maxDepth")
            exclude = configparser.get("bpa", "exclude")
            disconnect = configparser.get("bpa", "disconnect")
            disconnectOtherMetabolites = configparser.get("bpa", "disconnectOtherMetabolites")
            deleteIntermediates = configparser.get("bpa", "deleteIntermediates")
            largestComponentOnly = configparser.get("bpa", "largestComponentOnly")
            difference = configparser.get("bpa", "difference")
            threshold = configparser.get("bpa", "threshold")
            showLabels = configparser.get("bpa", "showLabels")
            showAbsoluteFluxes = configparser.get("bpa", "showAbsoluteFluxes")
            removeNodesWithNoFlux = configparser.get("bpa","removeNodesWithNoFlux")
        except NoOptionError as e:
            print e
            print "Please check the configuration file"
            exit()
        except NoSectionError as e:
            print e
            print "Please check the configuration file"
            exit()

        # Optional options
        try:
            substanceColor = configparser.get("bpa","metaboliteColor")
            reactionColor = configparser.get("bpa","reactionColor")
        except NoOptionError, NoSectionError:
            substanceColor = defaultSubstanceColor
            reactionColor = defaultReactionColor

        # TODO catch potential errors
        try:
            self.maxDepth = int(maxDepth)
            self.exclude = exclude.split(", ")
            self.disconnect = disconnect.split(", ")
            self.disconnectOtherMetabolites = disconnectOtherMetabolites == "True"
            self.deleteIntermediates = deleteIntermediates == "True"
            self.largestComponentOnly = largestComponentOnly == "True"
            self.difference = difference == "True"
            self.threshold = float(threshold)
            self.showLabels = showLabels == "True"
            self.showAbsoluteFluxes = showAbsoluteFluxes == "True"
            self.removeNodesWithNoFlux = removeNodesWithNoFlux == "True"
            self.substanceColor = substanceColor
            self.reactionColor = reactionColor
        except Exception as e:
            print e
            print "Please check the configuration file"
            exit()

class BranchPointAnalysis(object):

    def __init__(self, model, solutions=None, configuration=None, verbosityLevel=0):

        self.model = model
        self.verbosityLevel = verbosityLevel
        self.splitRatioGraph = None

        if configuration is None:
            self.setConfiguration(BPAconfiguration())
        else:
            self.setConfiguration(configuration)

        if solutions is None:
            # create a dummy solution and hide edge labels
            solutions = [MetabolicFlux(model,[1]*len(model))]
            self.configuration.showLabels = False

        self.splitRatios = self.computeSplitRatios(solutions)

    def setConfiguration(self, configuration):

        self.configuration = configuration

    def computeSplitRatios(self, solutions):

        # compute the split ratios for each solution
        splitRatios = []
        for solution in solutions:

            if len(solution)<=0:
                raise ValueError("Error: At least one flux solution is empty.")
#            print "computeSplitratios:", type(self.configuration.removeNodesWithNoFlux), self.configuration.removeNodesWithNoFlux), self.configuration.removeNodesWithNoFlux==False
            splitRatios.append(
                solution.computeAllSplitRatios(
                    self.model,
                    cutoff=self.configuration.threshold,
                    cutoffIsAbsolute=False,
                    listAll=self.configuration.removeNodesWithNoFlux==False)
            )

        return splitRatios

    def findNeighbors(self, graph, nodes, maxDepth=1):
        """ Recursively find neighbors of all given nodes until maxDepth is reached.
        """
        if maxDepth == 0 or len(nodes) <= 0:
            return nodes

        neighbors = set()
        for node in nodes:
            neighbors.update(graph.successors(node))
            neighbors.update(graph.predecessors(node))

        neighbors.update(self.findNeighbors(graph, neighbors, maxDepth - 1))
        neighbors.update(nodes)

        return neighbors

    def _copyNode(self, graph, node, newNode):

        graph.add_node(newNode, copy(graph.node[node]))

    def disconnectNodes(self, graph, nodes):

        for node in nodes:

            if node not in graph:
                continue

            if graph.degree(node) <= 1:
                continue # node does not need to be disconnected

            i = 0 # counter to attach a number the new disconnected nodes

            for successor in graph.successors(node):

                # create a new, disconnect node with the same attributes and labels
                # as the original node
                newNode = node + str(i)
                self._copyNode(graph, node, newNode)

                graph.add_edge(newNode, successor, graph[node][successor])
                graph.edge[newNode][successor]["disconnected"] = True
                graph.remove_edge(node, successor)

                i = i + 1

            for predecessor in graph.predecessors(node):

                # create a new, disconnect node with the same attributes and labels
                # as the original node
                newNode = node + str(i)
                self._copyNode(graph, node, newNode)

                graph.add_edge(predecessor, newNode, graph[predecessor][node])
                graph.edge[predecessor][newNode]["disconnected"] = True
                graph.remove_edge(predecessor, node)

                i = i + 1

            graph.remove_node(node)

    def deleteIntermediateNodes(self, graph, exclude=None):
        """ Iteratively delete all intermediate nodes and connect the
            corresponding neighbors. Excluded nodes will never be deleted.
        """

        if not exclude:
            exclude = []

        nodeRemoved = True
        while(nodeRemoved):

            nodeRemoved = False

            for node in graph.nodes():

                if node in exclude:
                    continue

                if graph.in_degree(node) < 1 or graph.out_degree(node) < 1:
                    continue # do not delete end nodes

                # check if the node is an intermediate node, do not take edges to
                # or from disconnected nodes into account
                outNodes = [v for u, v in graph.out_edges(node) if not graph[u][v].get("disconnected", False)]
                inNodes = [u for u, v in graph.in_edges(node) if not graph[u][v].get("disconnected", False)]

                if len(outNodes) == 1 and len(inNodes) == 1:

                    p = inNodes[0]
                    s = outNodes[0]

                    # create a direct connection only if all split ratios are 1.0
                    if not all(map(lambda x:x==1., graph[p][node]["splitRatio"])):
                        continue
                    if not all(map(lambda x:x==1., graph[node][s]["splitRatio"])):
                        continue

                    if p != s: # prevent self loops
                        graph.add_edge(p, s, edgeGraphicsIntermediate)
                        graph[p][s]["splitRatio"] = [1.0] * len(self.splitRatios)

                    graph.remove_node(node)
                    nodeRemoved = True

                    if self.verbosityLevel > 1:
                        print "deleted intermediate node:", node

    def reduceGraph(self, nodes=None):
        """ reduce the graph according to the given parameters, returns a copy
        """

        if self.splitRatioGraph is None:
            # build the split ratio graph
            self.createSplitRatioGraph()

        # plausibility checks of the input parameters

        graphNodes = set(self.splitRatioGraph.nodes())
        selectedNodes = set(nodes)
        if not graphNodes.issuperset(selectedNodes):
            raise ValueError("The following selected nodes are not part of the graph: "+", ".join(selectedNodes-graphNodes))

        if nodes and self.configuration.exclude:
            selectedRemoved = set(nodes).intersection(set(self.configuration.exclude))
            if len(selectedRemoved) > 0:
                raise ValueError("The following nodes are selected but should be removed, too:\n" + ", ".join(selectedRemoved))

        if nodes and self.configuration.disconnect:
            selectedDisconnect = set(nodes).intersection(set(self.configuration.disconnect))
            if len(selectedDisconnect) > 0:
                raise ValueError("The following nodes are selected but should be disconnected, too:\n" + ", ".join(selectedDisconnect))

        if self.configuration.disconnectOtherMetabolites and nodes is None:
            raise ValueError("Cannot disconnect all other nodes if no nodes are selected.")

        # make a copy of the orginal graph
        graph = deepcopy(self.splitRatioGraph)

        if self.configuration.exclude:
            graph.remove_nodes_from(self.configuration.exclude)

        if self.configuration.disconnect is not None:
            # disconnect given nodes only
            self.disconnectNodes(graph, self.configuration.disconnect)

        if self.configuration.disconnectOtherMetabolites:
            # disconnect all other metabolite nodes
            allMetabolites = [node for node in graph.nodes() if graph.node[node]["isMetabolite"]]
            otherMetabolites = set(allMetabolites) - set(nodes)
            self.disconnectNodes(graph, otherMetabolites)

        if self.configuration.deleteIntermediates:
            # delete all intermediate nodes, except selected nodes
            self.deleteIntermediateNodes(graph, exclude=nodes)
        if nodes:
            # delete all nodes except neighbors of the selected nodes
            graph = graph.subgraph(self.findNeighbors(graph, nodes, self.configuration.maxDepth))

        if self.configuration.largestComponentOnly:
            # select the largest connected component only
            graph = list(nx.weakly_connected.weakly_connected_component_subgraphs(graph))[0]

        if self.configuration.postReduceFunction is not None:
            self.configuration.postReduceFunction(graph, nodes)

        return graph

    def createSplitRatioGraph(self):
        # Prepare data structures for GML / GraphViz output
        substanceGraphics = {
                             # gml
                            "graphics": {
                                "type":substanceShape,
                                "fill":self.configuration.substanceColor},
                             # graphviz
                              "shape":"box",
                              "style":"filled",
                              "fillcolor":self.configuration.substanceColor,
                              "color":self.configuration.substanceColor}

        reactionGraphics = {
                            # gml
                            "graphics": {
                                "type":reactionShape,
                                "fill":self.configuration.reactionColor},

                             # graphviz
                              "shape":"box",
                              "style":"filled,rounded",
                              "fillcolor":self.configuration.reactionColor,
                              "color":self.configuration.reactionColor}

        # create the complete split ratio graph

        if len(self.model)<=0:
            raise ValueError("Model is empty.")

        self.splitRatioGraph = nx.DiGraph(name="AMEBA")

        splitRatioIndex = 0
        nSplitRatios = len(self.splitRatios)
        for splitRatios in self.splitRatios:

            if len(splitRatios)<=0:
                raise ValueError("Fluxes are empty.")

            for metabolite, splitRatio in splitRatios.iteritems():

                if self.verbosityLevel > 1:
                    print metabolite

                isOutRatio = True
                for ratios in splitRatio: # add out ratios first, in rations second

                    totalFlux=0
                    for reaction, ratioFlux in ratios.iteritems():

                        if self.verbosityLevel > 1:
                            print reaction, ("-" if isOutRatio else "") + \
                                  str(ratioFlux[0]), "("+str(ratioFlux[1])+")"

                        totalFlux = totalFlux + ratioFlux[1]

                        if isOutRatio:
                            # [metabolite] --> [reaction]
                            self.splitRatioGraph.add_edge(metabolite, reaction, edgeGraphics)
                            splitRatioList = self.splitRatioGraph[metabolite][reaction].get("splitRatio",[0.]*nSplitRatios)
                            splitRatioList[splitRatioIndex]=ratioFlux[0]
                            self.splitRatioGraph[metabolite][reaction]["splitRatio"] = splitRatioList
                        else:
                            # [reaction] --> [metabolite]
                            self.splitRatioGraph.add_edge(reaction, metabolite, edgeGraphics)
                            splitRatioList = self.splitRatioGraph[reaction][metabolite].get("splitRatio",[0.]*nSplitRatios)
                            splitRatioList[splitRatioIndex]=ratioFlux[0]
                            self.splitRatioGraph[reaction][metabolite]["splitRatio"] = splitRatioList

                        # set node attributes
                        self.splitRatioGraph.node[metabolite].update(substanceGraphics)
                        self.splitRatioGraph.node[reaction].update(reactionGraphics)
                        self.splitRatioGraph.node[metabolite]["isMetabolite"] = True
                        self.splitRatioGraph.node[reaction]["isMetabolite"] = False

                        totalFluxList = self.splitRatioGraph.node[metabolite].get("totalFlux",[0.]*nSplitRatios)
                        totalFluxList[splitRatioIndex]=totalFlux
                        totalFluxList = self.splitRatioGraph.node[metabolite]["totalFlux"] =  totalFluxList

                    isOutRatio = False

                if self.verbosityLevel > 1:
                    print # print a newline after each metabolite

            splitRatioIndex = splitRatioIndex+1

        # set all node labels
        for node in self.splitRatioGraph.nodes():
            self.splitRatioGraph.node[node]["label"]=node

        if self.configuration.showLabels and self.configuration.showAbsoluteFluxes:

            # set node labels
            for node in self.splitRatioGraph.nodes():

                # metabolite labels
                if self.splitRatioGraph.node[node]["isMetabolite"]:

                    # calculate the difference between the absolute fluxes
                    if self.configuration.difference and nSplitRatios==2:

                        diff = self.splitRatioGraph.node[node]["totalFlux"][1] - self.splitRatioGraph.node[node]["totalFlux"][0]

                        label = node +newline+ "%.4f" %  diff

                        if abs(diff)<0.0001:
                            fontcolor = "black"
                        elif diff>0:
                            fontcolor = "red"
                        elif diff<0:
                            fontcolor = "blue"

                    # display raw absolute flux values
                    else:

                        totalFluxString = newline.join(["%.4f" %f for f
                                   in self.splitRatioGraph.node[node]["totalFlux"]])
                        label =  node +newline+ totalFluxString
                        fontcolor = "black"

                    self.splitRatioGraph.node[node].update(
                                             {"label":label, "fontcolor":fontcolor})

        if self.configuration.showLabels:

            # set edge labels
            for a, b in self.splitRatioGraph.edges():

                # edge label is the difference of the percentage of the relative
                # flux fraction
                if self.configuration.difference and nSplitRatios==2:

                    diff = ((self.splitRatioGraph[a][b]["splitRatio"][1] -
                                   self.splitRatioGraph[a][b]["splitRatio"][0])*100)
                    label = "%.2f%%" %  diff

                    if abs(diff)<0.01:
                        fontcolor = "black"
                    elif diff>0:
                        fontcolor = "red"
                    elif diff<0:
                        fontcolor = "blue"

                # edge label is the percentage of the relative flux fraction
                else:

                    label = newline.join(["%.2f%%" % (sr*100) for sr
                                       in self.splitRatioGraph[a][b]["splitRatio"]])
                    fontcolor = "black"

                self.splitRatioGraph[a][b].update(
                                             {"label":label, "fontcolor":fontcolor})


#        if self.verbosityLevel>0:
#            print "The full split ratio graph has", len(self.splitRatioGraph), "nodes"

    def writeReducedGraph(self, reducedGraph):
        """ write the reduced graph to the output file or stdout
        """

        if self.configuration.outputFile.endswith(".gml"):

            # layout the graph using dot
            layoutDict = nx.graphviz_layout(reducedGraph,prog="dot")

            for node in reducedGraph.nodes():

                # set node position
                # the graphics needs to be copied to avoid a bug
                graphicsDict = copy(reducedGraph.node[node]["graphics"])
                graphicsDict["x"] = layoutDict[node][0]
                graphicsDict["y"] = -layoutDict[node][1] # invert y coords
                reducedGraph.node[node]["graphics"] = graphicsDict

                # delete unnecessary node attributes which would create
                # invalid GML entries
                for key in ["isMetabolite", "totalFlux"]:
                    if key in reducedGraph.node[node]:
                        del reducedGraph.node[node][key]

            # delete unnecessary edge attributes which would create
            # invalid GML entries
            for a, b in reducedGraph.edges():
                del reducedGraph[a][b]["splitRatio"]
                if "disconnected" in reducedGraph[a][b]:
                    del reducedGraph[a][b]["disconnected"]

            nx.write_gml(reducedGraph, self.configuration.outputFile)

        else: # assume graphviz dot
            a=nx.drawing.nx_agraph.to_agraph(reducedGraph)
            # set default font
            a.node_attr.update({"fontname":"Helvetica", "labelfontname":"Helvetica"})
            a.edge_attr.update({"fontname":"Helvetica", "labelfontname":"Helvetica"})
            if self.configuration.outputFile == "stdout":
                a.write(sys.stdout)
            else:
                a.write(self.configuration.outputFile)

    def writeSplitRatiosToGML(self, gmlFile):

        if self.splitRatioGraph is None:
            # build the split ratio graph
            self.createSplitRatioGraph()

        nx.write_gml(self.splitRatioGraph, gmlFile)

class bpaGUI(DotWindow, BranchPointAnalysis):

    def __init__(self, model, solutions, configuration=None, verbosityLevel=0):


        BranchPointAnalysis.__init__(self, model, solutions, configuration,
                                                                 verbosityLevel)

        # If file output is selected, displaying of the GUI is suppressed
        self.displayGUI = self.configuration.outputFile is None

        if self.displayGUI:
            DotWindow.__init__(self)
            self.dotwidget.connect('clicked', self._node_clicked)

        self.historySize = 3
        self.historyColors = ["#FF0000", "#FF7777", "#FFCCCC"]
        self.history = deque(maxlen=self.historySize)

    def show(self, nodes):
        if not self.displayGUI:
            if self.verbosityLevel > 0:
                print "GUI display not available (file output selected)"
            return

        if self.splitRatioGraph is None:

            self.createSplitRatioGraph()

            # add names as URL attributes to allow click event handling
            for node in self.splitRatioGraph:
                self.splitRatioGraph.node[node]["URL"] = node

        try:

            reducedGraph = self.reduceGraph(nodes)

            # to avoid the overwriting of the color remove the node if it is in
            # the history already
            for node in nodes:
                if node in self.history:
                    self.history.remove(node)

            self.history.extend(nodes)

            i = 0
            for node in reversed(self.history):
                if node in reducedGraph:
                    reducedGraph.node[node]["color"] = self.historyColors[i]
                    reducedGraph.node[node]["penwidth"] = 3
                    i += 1

        except ValueError as ve:
            dialog = Gtk.MessageDialog(self,Gtk.DialogFlags.MODAL,Gtk.MessageType.INFO,
                                       Gtk.ButtonsType.OK,ve.message)
            dialog.run()
            dialog.destroy()
        else:
            self.set_dotcode(nx.drawing.nx_agraph.to_agraph(reducedGraph).to_string())
            self.set_title(programName)

    def _node_clicked(self, widget, url, event):

        if self.verbosityLevel > 0:
            print url

        # the "URL" of the clicked node is the node name
        self.show(nodes=[url])

    @staticmethod
    def start(model, solutions, startNodes, configuration=None, verbosityLevel=0):

        bpa = bpaGUI(model, solutions, configuration, verbosityLevel)

        if bpa.displayGUI:
            # show the GUI
            bpa.show(startNodes)
            bpa.connect('destroy', Gtk.main_quit)
            Gtk.main()
        else:
            reducedGraph = bpa.reduceGraph(startNodes)
            bpa.writeReducedGraph(reducedGraph)


def main(argv=None):

    if argv is None:
        argv = sys.argv

    # create a default configuration
    configuration = BPAconfiguration()

    parser = argparse.ArgumentParser()

    parser.add_argument("-r", "--reactionFile", required=True,
                                help="file containg all reactions of the model")
    parser.add_argument("-n", "--nodes", required=True, nargs="+",
                                     help="start the BPA at the given %(dest)s, NOTE: If the resulting subgraphs are not connected, only the largest subgraph will be displayed.")
    parser.add_argument("-s", "--solutionFiles", required=False, nargs="+",
                                         help="parse the given FBA solution(s) and compute split ratios, if omitted all fluxes are assumed to be 1.")
    parser.add_argument("-c", "--configurationFile", default=None,
                            help="use the configuration given in this %(dest)s")
    parser.add_argument("-o", "--outputFile", default=None,
                            help="do not display the GUI - instead write the graph to the %(dest)s. Give 'stdout' to write to the standard output stream. If the files ends with .gml the format is GML and graphviz dot otherwise")
    parser.add_argument("-d", "--difference", action="store_const", const=True,
              help="show the difference of the relative fluxes as edge labels if two solutions are given, default: "+str(configuration.difference))
    parser.add_argument("-t", "--threshold", type=float,
              help="minimum relative flux value to show, 0 <= %(dest)s <=1, default: "+str(configuration.threshold))
    parser.add_argument("-m", "--maxDepth", type=int,
              help="maximum depth of the subgraph shown in the GUI, default: "+str(configuration.maxDepth))
    parser.add_argument("-i", "--toggleDeleteIntermediates", action="store_const", const=True,
              help="delete intermediate nodes and connect its neighbors by a dashed line, toggles the value given in the configuration file or the default: "+str(configuration.deleteIntermediates))
    parser.add_argument("-v", "--verbosityLevel", type=int, default=1,
              help="sets the verbosity level (0, 1 or 2), default: %(default)s")
    parser.add_argument("-x", "--removeNodesWithNoFlux", action="store_const", const=True,
              help="Do _not_ remove nodes without a flux")
#    parser.add_argument("-e", "--removeDeadEnds", action="store_const", const=True,
#              help="recursively remove all dead end reactions and metabolites from the model before displaying it, only valid if no solution file is given, default: "+str(configuration.removeDeadEnds))

    options = parser.parse_args()

    if options.verbosityLevel>0 and options.outputFile != "stdout":
        print
        print programName
        print "Version:", __version__
        print "Copyright 2012-2014 Rene Rex and Alexander Riemer (al.riemer@tu-bs.de)"
        print "License: GPLv3"
        print
        print "NetworkX version:", nx.__version__
       # print "PyGraphviz version:", nx.pygraphviz.__version__
#        print  __file__
        print

    # read configuration from file
    if options.configurationFile is not None:
        configuration.setConfigFromFile(options.configurationFile)

    # command line parameters overwrite the settings from the configuration file
    if options.toggleDeleteIntermediates:
        configuration.deleteIntermediates = not configuration.deleteIntermediates
    if options.difference is not None:
        configuration.difference = options.difference
    if options.threshold is not None:
        configuration.threshold = options.threshold
    if options.maxDepth is not None:
        configuration.maxDepth = options.maxDepth
    if options.removeNodesWithNoFlux is not None:
        configuration.removeNodesWithNoFlux = False
#    if options.removeDeadEnds is not None:
#        configuration.removeDeadEnds = options.removeDeadEnds
    if options.outputFile is not None:
        configuration.outputFile = options.outputFile
        if options.outputFile == "stdout":
            # set the verbosity level to zero, the output would be invalid
            # otherwise
            options.verbosityLevel = 0

    if options.verbosityLevel>0:
        print "Configuration:"
        print configuration.toString()
        print

    if configuration.difference and len(options.solutionFiles)!=2:
        print "Error: The difference option can be used for two solutions only."
        exit()

    if configuration.difference and configuration.threshold!=0:
        print "Sorry, the current implementation does not support the simultaneous usage of the difference and the threshold option."
        exit()

    # Parse reaction file
    rparser = ReactionParser()
    model = MetabolicModel()
    try:
        model.addReactionsFromFile(options.reactionFile, rparser)
    except IOError:
        print ("An error occurred while trying to read file %s:" %
               os.path.basename(options.reactionFile))
        exit()
    except SyntaxError:
        print ("Error in reaction file %s:" %
               os.path.basename(options.reactionFile))
        exit()

    # Parse solution files
    solutions = None
    if options.solutionFiles is not None:
        solutions = []
        for solutionFile in options.solutionFiles:
            solution = MetabolicFlux()
            try:
                solution.readFromFile(solutionFile)
                solutions.append(solution)
            except IOError:
                print ("An error occurred while trying to read file %s:" %
                       os.path.basename(solutionFile))
                exit()
            except SyntaxError:
                print ("Error in solution file %s:" %
                       os.path.basename(solutionFile))
                exit()

    bpaGUI.start(model, solutions, options.nodes, configuration,
                                                         options.verbosityLevel)

    return 0

if __name__ == "__main__":
    sys.exit(main())
