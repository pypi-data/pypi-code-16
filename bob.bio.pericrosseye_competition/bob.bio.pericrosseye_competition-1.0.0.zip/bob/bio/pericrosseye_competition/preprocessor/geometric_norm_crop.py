from bob.bio.face.preprocessor import Base
from bob.bio.base.preprocessor import Preprocessor
import numpy
import bob.ip.base
#import cv2

#TEMPLATE = numpy.float32([  (0.2, 0.5), (0.6, 0.5), (0.6, 0.5) ])
#TEMPLATE = numpy.float32([  (0.51, 0.2), (0.49, 0.4), (0.5, 0.6) ])
TEMPLATE = numpy.array([[ 0.45111111,  0.37555555],
                        [ 0.40000001,  0.51111114],
                        [ 0.45111111,  0.6477778 ]], dtype="float32")



class GeometricNormCrop (Base):

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

    def get_coordinates(image):
        from skimage.filters import rank
        image = bob.ip.color.rgb_to_gray(image).astype("uint8")

        gradient_image = (rank.gradient(image, disk(5)) < 5).astype("uint8")
        gradient_image[gradient_image == 1] = 255
        gradient_image = do_morph(gradient_image)

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

    def __call__(self, image, annotations = None):
        
        # convert to the desired color channel
        image = self.color_channel(image)
               
        #landmarks = self._get_coordinates(image)

        #return landmaks
        #H = cv2.getAffineTransform(landmarks, self.cropped_image_size[0] * TEMPLATE)
        #return cv2.warpAffine(image.astype("float64"), H, self.cropped_image_size).astype("uint8")
        return image
