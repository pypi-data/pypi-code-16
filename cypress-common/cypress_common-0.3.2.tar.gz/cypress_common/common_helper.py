# This Python file uses the following encoding: utf-8
import numpy as np
from PIL import Image
from scipy import misc


class CypressCommonHelper:
    def __init__(self):
        pass

    @staticmethod
    def np_bytes_to_np_array(np_bytes, axis_0, axis_1):
        """
        Convert a flatterned numpy array to multi-dimensional numpy array. This method is used to reconstruct RGB image
           numpy array from Redis record. Caller can use cv2.imwrite(nparray) to get the image file.
        :param np_bytes: flattened numpy.ndarray.
        :param axis_0: dimension 0
        :param axis_1: dimension 1
        :return: multi-dimensional numpy array of a image
        """
        try:
            return np.frombuffer(np_bytes, dtype=np.uint8).reshape(axis_0, axis_1, 3)
        except:
            return "cannot convert flatterned numpy array"

    @staticmethod
    def np_img_to_np_bytes(np_img):
        """
        Flattern an image Numpy array to an one-dimensional numpy array. The input image can be got by cv2.imread(<img file>)
        :param np_img: numpy array of image.
        :return: np_array_bytes, axis_0, axis_1
        """
        try:
            axis_0, axis_1, _ = np_img.shape
            np_array_bytes = np_img.tobytes()
            return np_array_bytes, axis_0, axis_1
        except:
            return "cannot flat numpy array to numpy array bytes"

    @staticmethod
    def img_rgb2bgr(image_rgb):
        """
        Convert a 'RGB' image to a 'BGR' image.
        :param image_rgb: the image object that is in 'RGB' or 'RGBA' mode
        :type image_rgb: `~PIL.Image.Image` object
        :return: the image object in 'BGR' mode
        :rtype: `~PIL.Image.Image` object
        """
        if image_rgb.mode == 'RGBA':
            r, g, b, _ = image_rgb.split()
        elif image_rgb.mode == 'RGB':
            r, g, b = image_rgb.split()
        else:
            raise IOError('Input image is either RGBA or RGB image.')

        image_bgr = Image.merge("RGB", (b, g, r))
        return image_bgr

    @staticmethod
    def np_bgr2rgb(np_bgr):
        """
        Convert a 'BGR' image numpy array to a 'RGB' image numpy array.
        :param image_np: the numpy array of the image in mode 'BGR'
        :type image_np: numpy array
        :return: numpy array of the image in mode 'RGB'
        :rtype: numpy array
        """
        image_bgr = misc.toimage(np_bgr)
        b, g, r = image_bgr.split()
        image_rgb = Image.merge("RGB", (r, g, b))
        return misc.fromimage(image_rgb)

    @staticmethod
    def img_rgb_2_np_bgr(image_rgb):
        """
        Convert a 'RGB' image object to a 'BGR' image numpy array.
        :param image_rgb: the image object that is in 'RGB' or 'RGBA' mode
        :type image_rgb: `~PIL.Image.Image` object
        :return: numpy array of the image in mode 'BGR'
        :rtype: numpy array
        """
        if image_rgb.mode == 'RGBA':
            r, g, b, _ = image_rgb.split()
        elif image_rgb.mode == 'RGB':
            r, g, b = image_rgb.split()
        else:
            raise IOError('Input image is either RGBA or RGB image.')

        image_bgr = Image.merge("RGB", (b, g, r))
        np_bgr = misc.fromimage(image_bgr)
        return np_bgr
