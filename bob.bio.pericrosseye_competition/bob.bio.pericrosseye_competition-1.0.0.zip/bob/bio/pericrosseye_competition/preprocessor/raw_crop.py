from bob.bio.face.preprocessor import Base
from bob.bio.base.preprocessor import Preprocessor
import numpy
import bob.ip.base

class RawCrop (Base):

    """
    Just crops the input image to a given size.
    """

    def __init__(self, cropped_image_size, **kwargs):
    
        Base.__init__(self, **kwargs)

        # call base class constructor
        Preprocessor.__init__(
            self,
            cropped_image_size = cropped_image_size,
            **kwargs
        )

        # copy parameters
        self.cropped_image_size = cropped_image_size

    def __call__(self, image, annotations = None):
        
        # convert to the desired color channel
        image = self.color_channel(image)
        dst = numpy.zeros(shape=self.cropped_image_size, dtype="float64")
        bob.ip.base.scale(image, dst)
        
        return dst

