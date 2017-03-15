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

            distances = [50, 100, 150, 200],
            n_points = 5,
            landmark_offset=20
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
        self.landmark_offset = landmark_offset

    def do_morph(self, image, disk_radio=30):
        structure = disk(disk_radio)
        return opening(image, structure)


    def get_landmarks(self, image, offset = 20):
        """
        Compute landmarks using the gradient image
        
         **Parameters**
         
           image:
           offset: This offset is used as the patch size to compute the gradient
        """

        def has_one_peak(signature):
          """
          Check the amount of peaks in a image projection
          """
          deltas = numpy.array([signature[i+1] - signature[i] for i in range(len(signature)-1)])
          if (sum(deltas) == (len(signature)-1)):
              return True
          else:
              return False

        from skimage.filters import rank

        # Compute the gradient image and set a very rigotous threshold
        gradient_image = (rank.gradient(image, disk(20)) < 3).astype("uint8")
        
        # Do 5 attempts to get the landmarks
        real_offset = offset
        for i in range(4):
            column_sum = numpy.sum(gradient_image, axis=0)
            indexes = numpy.where(column_sum > 0)[0]

            # If the image has one peak we are good
            if has_one_peak(indexes):
                break
                
            # If not, let's do Mathematical morphology to remove some noise
            gradient_image = self.do_morph(gradient_image, disk_radio=real_offset)
            real_offset += offset

        if i==4:
            raise Exception("Was not possible to find the eye")
        
        #gradient_image[gradient_image == 1] = 255
        
        # Here we'll do a morphological operator to remove noise.
        # `offset` parameter difines of the size of the disk.
        # With this approach, we hope to have only one connected component in the image.
        # In case we have more than one, 

        left = (numpy.where(gradient_image[:, indexes[0]] > 0)[0][0], indexes[0] - real_offset)
        right = (numpy.where(gradient_image[:, indexes[-1]] > 0)[0][0], indexes[-1] + real_offset)

        center_up_y = int((left[1] + right[1]) / 2)
        center_up_x = numpy.where(gradient_image[:, center_up_y] > 0)[0][0]
        center_up = (center_up_x - real_offset, center_up_y)

        center_down_y = int((left[1] + right[1]) / 2)
        center_down_x = numpy.where(gradient_image[:, center_down_y] > 0)[0][-1]
        center_down = (center_down_x + real_offset, center_down_y)

        return numpy.array([left, center_up, right, center_down], dtype='float32')

    def get_graph(self, radius, n_points=4, delta=(0.5 * numpy.pi, 1.5 * numpy.pi)):
        step = (delta[1] - delta[0]) / n_points
        offset = delta[0]
        points = []
        for i in range(n_points + 1):
            points.append((radius * numpy.sin(offset), radius * numpy.cos(offset)))
            offset += step
        return numpy.array(points)

    def get_jets_coords(self, landmarks, image):
    
        def clip(coord):
            """
            Remove all negative coordinates
            """
            
            coord[0] = 0 if coord[0] < 0 else coord[0]
            coord[1] = 0 if coord[1] < 0 else coord[1]
            
            coord[0] = image.shape[0]-1 if coord[0] >= image.shape[0] else coord[0]
            coord[1] = image.shape[1]-1 if coord[1] >= image.shape[1] else coord[1]
            
            return coord
    
    
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
            points = self.get_graph(r, delta=delta[0], n_points=self.n_points)
            for p in points:
                coords.append(tuple(clip(left + p).astype("int")))
          
            points = self.get_graph(r, delta=delta[1], n_points=self.n_points)
            for p in points:
                coords.append(tuple(clip(right - p).astype("int")))

            points = self.get_graph(r, delta=delta[2], n_points=self.n_points)
            for p in points:
                coords.append(tuple(clip(center_up - p).astype("int")))

            points = self.get_graph(r, delta=delta[3], n_points=self.n_points)
            for p in points:
                coords.append(tuple(clip(center_down - p).astype("int")))

        return coords

    def __call__(self, image):

        image = image.astype("uint8")

        self.trafo_image = numpy.ndarray((self.gwt.number_of_wavelets, image.shape[0], image.shape[1]),
                                         numpy.complex128)
        landmarks = self.get_landmarks(image, offset=self.landmark_offset)
        coords = self.get_jets_coords(landmarks, image)
        
        self._graph = bob.ip.gabor.Graph(nodes=coords)

        # perform Gabor wavelet transform
        self.gwt.transform(image, self.trafo_image)
        
        jets = self._graph.extract(self.trafo_image)
        
        del self.trafo_image        
        del self._graph
        
        # normalize the Gabor jets of the graph only
        if self.normalize_jets:
          [j.normalize() for j in jets]
        
        return jets
