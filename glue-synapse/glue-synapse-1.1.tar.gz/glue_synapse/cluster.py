from __future__ import absolute_import, division, print_function
from glue.logger import logger
from sklearn.cluster import DBSCAN
import numpy as np
import os
from scipy.spatial import distance_matrix

from glue.core import Data, Subset
from glue.viewers.scatter.qt import ScatterWidget
from glue.viewers.histogram.qt import HistogramWidget
import matplotlib as mpl

from glue_vispy_viewers.scatter.scatter_viewer import VispyScatterViewer
from glue.core import Data, DataCollection, Subset, SubsetGroup
from glue.core.util import facet_subsets
from glue.core.component_link import ComponentLink
import qtpy

from pyqtgraph.console import ConsoleWidget

if qtpy.PYQT4:
	from PyQt4 import QtGui, uic
elif qtpy.PYQT5:
	import PyQt5.QtWidgets as QtGui
	from PyQt5 import uic

import pandas
pandas.options.mode.chained_assignment = None 

cluster_ui = None
to_save = None

def to_df(item):
	if type(item) == Data:
		return item.to_dataframe()
	else:
		return item.data.to_dataframe()[item.to_mask()]

def can_save_txt(app):
	global to_save
	qapp = QtGui.qApp
	data = {}
	for a in app.data_collection:
		data[a.label] = a
		for b in a.subsets:
			try:
				b.to_mask()
				data[a.label + ' - ' + b.label] = b
			except:
				pass
	
	ret, val = QtGui.QInputDialog.getItem(None, "Export Data", "Which data group would you like to export?", [str(i) for i in data.keys()], editable=False)
	if not val:
		return False
	to_save = to_df(data[ret])
	return True

def save_txt(application, **args):
	path = QtGui.QFileDialog.getSaveFileName(None, 'Export to .txt file', '', filter='*.txt')
	to_save.to_csv(path, index=None, sep='\t')

def closestpairs(L, maximum=np.inf):
	def sqdist(p,q): return np.linalg.norm(np.subtract(p, q))
	used = set()

	L = L.sort_values(by='Xc').values
		
	pairs = pandas.DataFrame([], columns=['ID1', 'ID2', 'Distance'])
	
	# check whether pair (p,q) forms a closer pair than one seen already
	def testpair(a,b):
		if a[4] in used or b[4] in used or a[0] == b[0]:
			return
		p, q = a[5:], b[5:]
		d = sqdist(p,q)
		if d < best[0]:
			best[0] = d
			best[1] = a,b
			
	# merge two sorted lists by y-coordinate
	def merge(A,B):
		i = 0
		j = 0
		while i < len(A) or j < len(B):
			if j >= len(B) or (i < len(A) and A[i][1] <= B[j][1]):
				yield A[i]
				i += 1
			else:
				yield B[j]
				j += 1

	# Find closest pair recursively; returns all points sorted by y coordinate
	def recur(L):
		if len(L) < 2:
			return L
		split = len(L)//2
		splitx = L[split][0]
		L = list(merge(recur(L[:split]), recur(L[split:])))

		# Find possible closest pair across split line
		# Note: this is not quite the same as the algorithm described in class, because
		# we use the global minimum distance found so far (best[0]), instead of
		# the best distance found within the recursive calls made by this call to recur().
		# This change reduces the size of E, speeding up the algorithm a little.
		#
		E = [p for p in L if abs(p[0]-splitx) < best[0]]
		for i in range(len(E)):
			for j in range(1,20):
				if i+j < len(E) and E[i][4] not in used and E[i+j][4] not in used:
					testpair(E[i], E[i+j])
		return L

	best = [0, (None, None)]
	while best[0] < maximum:
		indA = min(set(np.where(L[:, 0] != L[0, 0])[0]) - used)
		indB = min(set(np.where(L[:, 0] == L[0, 0])[0]) - used)
		best = [sqdist(L[indA, 5:], L[indB, 5:]), (L[indA], L[indB])]
		recur(L)
		if best[1][0][4] in used:
			break
		ids = best[1][0][4], best[1][1][4]
		used |= set(ids)
		pairs.loc[-1] = [ids[0], ids[1], best[0]]
		pairs.index += 1
	return pairs

def wavelength_to_rgb(wavelength, gamma=0.8):

	'''This converts a given wavelength of light to an 
	approximate RGB color value. The wavelength must be given
	in nanometers in the range from 380 nm through 750 nm
	(789 THz through 400 THz).

	Based on code by Dan Bruton
	http://www.physics.sfasu.edu/astro/color/spectra.html
	'''

	wavelength = float(wavelength)
	if wavelength >= 380 and wavelength <= 440:
		attenuation = 0.3 + 0.7 * (wavelength - 380) / (440 - 380)
		R = ((-(wavelength - 440) / (440 - 380)) * attenuation) ** gamma
		G = 0.0
		B = (1.0 * attenuation) ** gamma
	elif wavelength >= 440 and wavelength <= 490:
		R = 0.0
		G = ((wavelength - 440) / (490 - 440)) ** gamma
		B = 1.0
	elif wavelength >= 490 and wavelength <= 510:
		R = 0.0
		G = 1.0
		B = (-(wavelength - 510) / (510 - 490)) ** gamma
	elif wavelength >= 510 and wavelength <= 580:
		R = ((wavelength - 510) / (580 - 510)) ** gamma
		G = 1.0
		B = 0.0
	elif wavelength >= 580 and wavelength <= 645:
		R = 1.0
		G = (-(wavelength - 645) / (645 - 580)) ** gamma
		B = 0.0
	elif wavelength >= 645 and wavelength <= 750:
		attenuation = 0.3 + 0.7 * (750 - wavelength) / (750 - 645)
		R = (1.0 * attenuation) ** gamma
		G = 0.0
		B = 0.0
	else:
		R = 0.0
		G = 0.0
		B = 0.0
	R *= 255
	G *= 255
	B *= 255
	return (int(R), int(G), int(B))

def toHex(R, G, B):
	R = hex(int(R))[2:]
	if len(R) == 1:
		R = '0' + R
	G = hex(int(G))[2:]
	if len(G) == 1:
		G = '0' + G
	B = hex(int(B))[2:]
	if len(B) == 1:
		B = '0' + B
	return '#%s%s%s' % (R, G, B)

def colorFor(a):
	if a.isdigit():
		return toHex(*wavelength_to_rgb(int(a)))
	else:
		return "#%06x" % np.random.randint(0, 0xFFFFFF)

def getTwoChannelDistances(points, mode, cutoff = np.inf):
	'''
	Takes a pandas dataframe of centroid points, with channel at column 0, and coords at columns 5:
	return list of distances between points with the given pairing mode
	0: all closest pairs below the cutoff, no recycling
	1: nearest neighbor for all X in Y, recycles points
	2: all distances from a point in X to every point in Y
	'''
	if mode == 0:
		return closestpairs(points, cutoff)['Distance'].values

	arr = points.values
	matrix = distance_matrix(arr[arr[:, 0] == arr[0, 0], 5:], arr[arr[:, 0] != arr[0, 0], 5:]).astype(float)
	if mode == 2: # all distances between channels
		matrix = matrix.flatten()
	elif mode == 1: # all shortest distances between channels
		matrix = np.min(matrix, axis=0 if matrix.shape[0] > matrix.shape[1] else 1)
	
	return matrix[matrix <= cutoff]

class SynapseWidget(QtGui.QMainWindow):
	def __init__(self, session, data):
		QtGui.QMainWindow.__init__(self)
		uic.loadUi(os.path.join(os.path.dirname(__file__), 'cluster_ui.ui'), self)
		self.data = data
		self.session = session
		self.data_facets = []
		self.centroid_facets = []
		self.centroid_data = None
		self.centroid_viewer = None
		self.distance_data = None
		self.distances_viewer = None

		def comboClicked(sender):
			self.setDataOptions(sender)
			QtGui.QComboBox.showPopup(sender)

		self.allCombo.showPopup = lambda : comboClicked(self.allCombo)
		self.allCombo.currentIndexChanged.connect(self.showColumns)
		
		self.setDataOptions(self.allCombo)
		self.allClusterBtn.pressed.connect(self.pipeline)
		self.previewBtn.pressed.connect(lambda : self.pipeline(preview = True))


	def showColumns(self):
		self.allChannel.clear()
		data = self.allCombo.itemData(self.allCombo.currentIndex())
		i = 0
		channel_ind = -1
		if data == None:
			return
		for n in data.components:
			self.allChannel.addItem(n.label, n)
			if n.label == 'Channel Name':
				channel_ind = i
			i += 1
		if channel_ind > 0:
			self.allChannel.setCurrentIndex(channel_ind)

	def facet(self, data_collection, cid, channels, suffix=''):
		states = []
		labels = []
		for i in channels:
			states.append((cid == i))
			labels.append(str(i))

		result = []
		for lbl, s in zip(labels, states):
			sg = data_collection.new_subset_group(label=lbl + suffix, subset_state=s)
			result.append(sg)
		return result

	def plotChannels(self, centers, zc):
		if not zc:
			scatter = self.session.application.new_data_viewer(ScatterWidget)
			scatter.add_data(centers)
			scatter.xatt = centers.id['Xc']
			scatter.yatt = centers.id['Yc']
		else:
			scatter = self.session.application.new_data_viewer(VispyScatterViewer)
			scatter.add_data(centers)
			layer = scatter.layers[0]
			layer.size = 3
			layer.alpha = .8
			layer.cmap_attribute = centers.id['Channel Name']
			layer.color_mode = "Linear"
			layer.vispy_widget.options.z_stretch = .1
			try:
				layer.cmap = mpl.colors.ListedColormap(np.array([[1, 0, 0], [0, 1, 0]]))
			except Exception:
				pass
			layer.vispy_widget.options.x_att = centers.id['Xc']
			layer.vispy_widget.options.y_att = centers.id['Yc']
			layer.vispy_widget.options.z_att = centers.id['Zc']
		return scatter

	def pipeline(self, preview=False):
		self.statusBar().showMessage("Calculating centroids")
		data = self.allCombo.itemData(self.allCombo.currentIndex())
		columnName = self.allChannel.itemData(self.allChannel.currentIndex())
		zc = self.allZcCheck.isChecked()
		args = (self.allEpsilon.value(), self.allMinSamples.value(), self.allMinDensity.value())
		cols = ['Xc', 'Yc', 'Zc'] if zc else ['Xc', 'Yc']
		columnVals = np.unique(data.get_component(columnName).data)

		if len(self.data_facets) > 0:
			for group in self.data_facets:
				self.data.remove_subset_group(group)
		self.data_facets = self.facet(self.data, columnName, columnVals)
		
		data_df = data.to_dataframe()
		if self.centroid_data != None:
			for i in range(len(self.centroid_facets)):
				try:
					self.data.remove_subset_group(self.centroid_facets[i])
				except:
					pass
			self.centroid_facets = []
			self.data.remove(self.centroid_data)

		n = data.shape[0]
		ids = np.zeros(n, dtype=int) - 1
		init = 0
		for uniq in columnVals:
			mask = data_df[str(columnName)] == uniq
			clust_ids = self.cluster(data_df[mask], zc, *args)
			clust_ids[clust_ids != -1] += init
			ids[np.where(mask)] = clust_ids
			init = max(ids) + 1


		if any([c.label == "Cluster ID" for c in data.components]):
			data.update_components({data.id["Cluster ID"]: ids})
		else:
			data.add_component(label="Cluster ID", component=ids)
		data_df = data.to_dataframe()
		centroids = []
		
		for clust in range(1, max(ids)+1):
			vals = data_df[data_df['Cluster ID'] == clust]
			center = np.average(vals[cols], 0)
			columnVal = vals[str(columnName)].values[0]
			row = list(center)
			row.extend([columnVal, clust, "Centroid"])
			centroids.append(row)
		
		centroid_df = pandas.DataFrame(centroids, columns=(cols + [str(columnName), 'Cluster ID', "PointType"]))
		self.centroid_data = Data(label="Cluster Centroids", **centroid_df)

		self.data.append(self.centroid_data)

		links = [ComponentLink([data.id['Xc']], self.centroid_data.id['Xc']), ComponentLink([data.id['Yc']], self.centroid_data.id['Yc'])]
		if zc:
			links.append(ComponentLink([data.id['Zc']], self.centroid_data.id['Zc']))
		self.data.set_links(links)

		self.centroid_facets = self.facet(self.data, self.centroid_data.id[str(columnName)], columnVals, suffix=' Centroids')

		try:
			self.centroid_viewer.close(False)
			self.centroid_viewer = None
		except Exception as e:
			pass
		
		def fix_layer(layer, size, alpha, color):
			layer.size = 3
			layer.alpha = .8
			layer.color = color
			layer.vispy_widget.options.z_stretch = .1

		if not zc:
			scatter = self.session.application.new_data_viewer(ScatterWidget)
			l = scatter.add_data(data)
			scatter.xatt = data.id['Xc']
			scatter.yatt = data.id['Yc']
		else:
			scatter = self.session.application.new_data_viewer(VispyScatterViewer)
			scatter.add_data(data)
			layer = scatter.layers[0]
			fix_layer(layer, 3, .8, "#ffffff")
			try:
				layer.cmap = mpl.colors.ListedColormap(np.array([[1, 0, 0], [0, 1, 0]]))
			except Exception:
				pass
			layer.vispy_widget.options.x_att = data.id['Xc']
			layer.vispy_widget.options.y_att = data.id['Yc']
			layer.vispy_widget.options.z_att = data.id['Zc']

		for sub in self.data_facets:
			for fac in sub.subsets:
				if fac.data == data:
					scatter.add_subset(fac)
					if zc:
						fix_layer(scatter.layers[-1], 3, .8, colorFor(fac.label))

		for sub in self.centroid_facets:
			for fac in sub.subsets:
				if fac.data == self.centroid_data:
					scatter.add_subset(fac)
					if zc:
						fix_layer(scatter.layers[-1], 5, .8, colorFor(fac.label))

		scatter._layer_artist_container.remove(scatter.layers[0]) 
		self.centroid_viewer = scatter
		self.statusBar().showMessage("Successfully calculated centroids")
		if not preview:
			self.statusBar().showMessage("Calculating distances")
			mode = self.allMode.currentIndex()
			
			sim = self.allSimulateDistancesCheck.isChecked()
		
			centroids = []
			for col in columnVals:
				centroids.append(centroid_df[centroid_df[str(columnName)] == col][cols])

			if self.distances_viewer != None:
				self.distances_viewer.close()
				self.distances_viewer = None

			self.distances_viewer = self.plotDistances(self.centroid_data.to_dataframe(), zc, mode, simulate=sim)
			self.statusBar().showMessage("Successfully calculated centroid distances")


	def setDataOptions(self, sender):
		sender.clear()
		for a in self.data:
			sender.addItem(a.label, a)
				

	def plotDistances(self, data, zc, mode, data2=[], simulate=False):
		cols = ['Xc', 'Yc', 'Zc'] if zc else ['Xc', 'Yc']
		
		cutoff = self.cutoffSpin.value()
		if cutoff < 0:
			cutoff = np.inf
		distances = getTwoChannelDistances(data, mode, cutoff)
		self.dists = distances

		label = 'Centroid Distances'

		if zc:
			label += ' (3D)'

		if self.distance_data != None:
			self.data.remove(self.distance_data)
			self.distance_data = None

		self.distance_data = Data(label, distance=distances)
		self.data.append(self.distance_data)

		self.hist = self.session.application.new_data_viewer(HistogramWidget)
		self.hist.add_data(self.distance_data)

		if simulate:
			min1 = data.min()[cols].values
			max1 = data.max()[cols].values
			vals = np.random.random((data.shape[0], 2+zc)) * (max1-min1) + min1
			vals = dict(zip(cols, np.transpose(vals)))
			self.simDist = Data("Simulated 1", **vals)
			
			if len(data2) > None:
				min2 = data2.min()[cols].values
				max2 = data2.max()[cols].values
				vals = np.random.random((data2.shape[0], 2+zc)) * (max2-min2) + min2
				vals = dict(zip(cols, np.transpose(vals)))
				self.simDist2 = Data("Simulated 2", **vals)
				self.plotDistances(self.simDist, zc, mode, data2=self.simDist2)
			else:
				self.plotDistances(self.simDist, zc, mode)

	def cluster(self, data, zc, eps, minSamples, minDensity):

		num = data.shape[0]
		cols = ['Xc', 'Yc', 'Zc'] if zc else ['Xc', 'Yc']

		pts1 = data[cols]
		args = (eps, minSamples, minDensity)
		clusters = cluster(pts1, *args)

		return clusters


def show_gui(session, data):
	global cluster_ui
	if cluster_ui is None:
		cluster_ui = SynapseWidget(session, data)
	cluster_ui.show()
	
def cluster(points, epsilon, minSamples, minDensity):
	ndim = np.shape(points)[1]

	scanner = DBSCAN(eps=epsilon, min_samples=minSamples)
	labels = scanner.fit_predict(points)
	n = max(labels)
	for i in range(0, n + 1):
		count = len(labels[labels == i])
		if count < minDensity:
			labels[labels == i] == -1
	return labels

def setup():
	from glue.config import menubar_plugin as mbar
	mbar.add('Cluster Widget', show_gui)
	from glue.config import exporters
	exporters.add('Text File', save_txt, can_save_txt)

if __name__ == '__main__':
	qApp = QtGui.QApplication([])
	cluster_ui = SynapseWidget(None, [])
	cluster_ui.show()
	cluster_ui.console = ConsoleWidget()
	arr = np.load("C:/Users/Brett/Desktop/cents.txt")
	cluster_ui.console.localNamespace.update({'self': cluster_ui, "arr":arr})
	cluster_ui.console.localNamespace.update(locals())
	cluster_ui.console.localNamespace.update(globals())
		
	cluster_ui.console.show()
	qApp.exec_()