import abc
import six


class Authentication(six.with_metaclass(abc.ABCMeta, object)):
    """Abstract class for a general authentication system."""

    def __init__(self, preprocessor, feature_extractor):
        """**Contructor Documentation**"""

        self.preprocessor = preprocessor
        self.feature_extractor = feature_extractor
        # self.algorithm          = algorithm

    @abc.abstractmethod
    def enroll(self, image, output_path):
        """
        Enrols a client
        """

        NotImplementedError("This function must be implemented in your derived class.")

    @abc.abstractmethod
    def scoring(self, image, output_path):
        """
        Enrols a client
        """

        NotImplementedError("This function must be implemented in your derived class.")

    @abc.abstractmethod
    def load_background_model(self, path):
        """
        Enrols a client
        """

        NotImplementedError("This function must be implemented in your derived class.")

    @abc.abstractmethod
    def load_client_model(self, path):
        """
        Load client model
        """

        NotImplementedError("This function must be implemented in your derived class.")
