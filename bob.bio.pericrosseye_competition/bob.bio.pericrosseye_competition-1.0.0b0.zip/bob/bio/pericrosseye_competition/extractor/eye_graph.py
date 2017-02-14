from bob.bio.face.extractor import GridGraph
import numpy
import bob.ip.base
import bob.ip.color
import math
from skimage.morphology import erosion, disk, dilation, closing, opening


class EyeGraph (GridGraph):

    """
    Just crops the input image to a given size.
    """

    def __init__(
            self,
            # Gabor parameters
            gabor_directions=8,
            gabor_scales=5,
            gabor_sigma=2. * math.pi,
            gabor_maximum_frequency=math.pi / 2.,
            gabor_frequency_step=math.sqrt(.5),
            gabor_power_of_k=0,
            gabor_dc_free=True,
            # what kind of information to extract
            normalize_gabor_jets=True,
            # setup of the aligned grid

            distances = [50],
            n_points = 5
    ):

        # call base class constructor
        GridGraph.__init__(
            self,
            gabor_directions=gabor_directions,
            gabor_scales=gabor_scales,
            gabor_sigma=gabor_sigma,
            gabor_maximum_frequency=gabor_maximum_frequency,
            gabor_frequency_step=gabor_frequency_step,
            gabor_power_of_k=gabor_power_of_k,
            gabor_dc_free=gabor_dc_free,
            normalize_gabor_jets=normalize_gabor_jets,
            eyes=None,
            node_distance=10
        )

        self.distances = distances
        self.n_points = n_points

    def do_morph(self, image):
        structure = disk(10)
        return opening(image, structure)

    def get_landmarks(self, image):
        from skimage.filters import rank

        gradient_image = (rank.gradient(image, disk(5)) < 5).astype("uint8")
        gradient_image[gradient_image == 1] = 255
        gradient_image = self.do_morph(gradient_image)

        column_sum = numpy.sum(gradient_image, axis=0)
        indexes = numpy.where(column_sum > 0)[0]

        left = (numpy.where(gradient_image[:, indexes[0]] > 0)[0][0], indexes[0])
        right = (numpy.where(gradient_image[:, indexes[-1]] > 0)[0][0], indexes[-1])

        center_up_y = int((left[1] + right[1]) / 2)
        center_up_x = numpy.where(gradient_image[:, center_up_y] > 0)[0][0]
        center_up = (center_up_x, center_up_y)

        center_down_y = int((left[1] + right[1]) / 2)
        center_down_x = numpy.where(gradient_image[:, center_down_y] > 0)[0][-1]
        center_down = (center_down_x, center_down_y)

        return numpy.array([left, center_up, right, center_down], dtype='float32')

    def get_graph(self, radius, n_points=4, delta=(0.5 * numpy.pi, 1.5 * numpy.pi)):
        step = (delta[1] - delta[0]) / n_points
        offset = delta[0]
        points = []
        for i in range(n_points + 1):
            points.append((radius * numpy.sin(offset), radius * numpy.cos(offset)))
            offset += step
        return numpy.array(points)

    def get_jets_coords(self, landmarks):
        delta = [(0.5 * numpy.pi, 1.5 * numpy.pi),
                 (1.5 * numpy.pi, 0.5 * numpy.pi),
                 (0, numpy.pi),
                 (numpy.pi, 2 * numpy.pi)]

        left = landmarks[0]
        center_up = landmarks[1]
        right = landmarks[2]
        center_down = landmarks[3]

        coords = []
        for r in self.distances:
            points = self.get_graph(r, delta=delta[0])
            for p in points:
                coords.append( tuple((left + p).astype("int")) )

            points = self.get_graph(r, delta=delta[1])
            for p in points:
                coords.append( tuple( (right - p).astype("int")))

            points = self.get_graph(r, delta=delta[2])
            for p in points:
                coords.append(tuple((center_up - p).astype("int")))

            points = self.get_graph(r, delta=delta[3])
            for p in points:
                coords.append(tuple((center_down - p).astype("int")))

        return coords

    def __call__(self, image):

        image = image.astype("uint8")

        #import ipdb; ipdb.set_trace();

        self.trafo_image = numpy.ndarray((self.gwt.number_of_wavelets, image.shape[0], image.shape[1]),
                                         numpy.complex128)
        landmarks = self.get_landmarks(image)
        coords = self.get_jets_coords(landmarks)
        
        self._graph = bob.ip.gabor.Graph(nodes=coords)

        # perform Gabor wavelet transform
        self.gwt.transform(image, self.trafo_image)
        
        jets = self._graph.extract(self.trafo_image)

        # normalize the Gabor jets of the graph only
        if self.normalize_jets:
          [j.normalize() for j in jets]

        return jets
