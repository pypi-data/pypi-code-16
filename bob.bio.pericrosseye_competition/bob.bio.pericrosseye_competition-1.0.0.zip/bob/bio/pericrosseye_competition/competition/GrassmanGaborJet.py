import bob.learn.linear
import numpy
from .Authentication import Authentication
import bob.bio.face
import math
from bob.learn.linear import GFKMachine

class GrassmanGaborJet(Authentication):
    """Abstract class for a general authentication system."""

    def __init__(self, preprocessor, feature_extractor, background_model_path):
        """**Contructor Documentation**"""

        self.preprocessor = preprocessor
        self.feature_extractor = feature_extractor

        self.gfk_machine = []
        self.jet_machine = bob.bio.face.algorithm.GaborJet('PhaseDiffPlusCanberra',
                                                      multiple_feature_scoring = 'average',
                                                      gabor_directions = 8,
                                                      gabor_scales = 5,
                                                      gabor_sigma = 2. * math.pi,
                                                      gabor_maximum_frequency = math.pi / 2.,
                                                      gabor_frequency_step = math.sqrt(.5),
                                                      gabor_power_of_k = 0,
                                                      gabor_dc_free = True)

        # Loading background model
        self.load_background_model(background_model_path)


    def enroll(self, image, output_path):
        """
        Enrols a client
        """
        preprocess_image = self.preprocessor(image)
        features = self.feature_extractor(preprocess_image)
        model = self.jet_machine.enroll([features])
        self.jet_machine.write_model(model, output_path)


    def scoring(self, image, biometric_reference_path):
        """
        Scoring
        """
        #preprocess_image = self.preprocessor(image)
        #probe_features = self.feature_extractor(preprocess_image)
        probe_features = self.jet_machine.read_model(image)

        model = self.jet_machine.read_model(biometric_reference_path)

        # Kernalized dot product per jet
        local_scores = [numpy.dot(
                        numpy.dot(
                        (m[0].abs - machine.source_machine.input_subtract) / machine.source_machine.input_divide, machine.G), 
                        (p[0].abs - machine.target_machine.input_subtract) / machine.target_machine.input_divide)
                        for m, p ,machine in zip(model, probe_features, self.gfk_machine)]
                        
                        
        return numpy.average(local_scores)
        

    def load_background_model(self, path):
        """
        Load the GFK Background model
        """
        
        hdf5 = bob.io.base.HDF5File(path, 'r')
        nodes = hdf5.get("nodes")
        hdf5 = bob.io.base.HDF5File(path)
        for k in range(nodes):
            node_name = "node{0}".format(k)
            hdf5.cd(node_name)
            self.gfk_machine.append(GFKMachine(hdf5))
            hdf5.cd("..")
            
    def load_client_model(self, biometric_reference_path):
        raise NotImplemented("Method not implemented")

