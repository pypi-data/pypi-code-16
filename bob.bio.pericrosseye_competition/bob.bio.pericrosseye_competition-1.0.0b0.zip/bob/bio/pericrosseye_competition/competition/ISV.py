import bob.learn.em
import numpy

from .Authentication import Authentication


class ISV(Authentication):
    """Abstract class for a general authentication system."""

    def __init__(self, preprocessor, feature_extractor, background_model_path, relevance_factor=4):
        """**Contructor Documentation**"""

        self.preprocessor = preprocessor
        self.feature_extractor = feature_extractor

        self.isv_base = None
        self.ubm = None

        self.relevance_factor = relevance_factor

        # Loading background model
        self.load_background_model(background_model_path)

    def enroll(self, image, output_path):
        """
        Enrols a client
        """

        # Extracting features
        preprocess_image = self.preprocessor(image)
        features = self.feature_extractor(preprocess_image)

        gmm_stats = bob.learn.em.GMMStats(self.ubm.shape[0], self.ubm.shape[1])

        for i in range(len(features)):
            self.ubm.acc_statistics(features[i], gmm_stats)

        isv_machine = bob.learn.em.ISVMachine(self.isv_base)
        isv_trainer = bob.learn.em.ISVTrainer(self.relevance_factor)
        isv_trainer.enroll(isv_machine, [gmm_stats], 1)

        hdf5_file = bob.io.base.HDF5File(output_path, 'w')
        isv_machine.save(hdf5_file)
        del hdf5_file


    def scoring(self, image, biometric_reference_path):
        """
        Scoring
        """
        preprocess_image = self.preprocessor(image)
        features = self.feature_extractor(preprocess_image)
        gmm_stats = bob.learn.em.GMMStats(self.ubm.shape[0], self.ubm.shape[1])

        for i in range(len(features)):
            self.ubm.acc_statistics(features[i], gmm_stats)

        estimated_Ux = numpy.ndarray(shape=(self.ubm.shape[0] * self.ubm.shape[1]), dtype=numpy.float64)
        isv_machine = self.load_client_model(biometric_reference_path)
        isv_machine.estimate_ux(gmm_stats, estimated_Ux)
        score = isv_machine.forward_ux(gmm_stats, estimated_Ux)

        return score

    def load_background_model(self, path):
        """
        Load the ISV Background model
        """

        # Loading UBM
        hdf5_file = bob.io.base.HDF5File(path)
        hdf5_file.cd("Projector")
        self.ubm = bob.learn.em.GMMMachine(hdf5_file)

        # Loading ISV Base
        U = hdf5_file.read('/Enroller/U')
        d = hdf5_file.read('/Enroller/d')

        self.isv_base = bob.learn.em.ISVBase(self.ubm, U.shape[1])
        self.isv_base.u = U
        self.isv_base.d = d

        del hdf5_file

    def load_client_model(self, biometric_reference_path):
        """
        Load the client model
        """

        isv_machine = bob.learn.em.ISVMachine(self.isv_base)
        hdf5file = bob.io.base.HDF5File(biometric_reference_path)
        isv_machine.z = hdf5file.read('/z')
        del hdf5file

        return isv_machine
