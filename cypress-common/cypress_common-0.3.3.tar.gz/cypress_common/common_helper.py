# This Python file uses the following encoding: utf-8
import json
import numpy as np
import uuid
import time
from PIL import Image
from scipy import misc

from .kafka_helper import send_message, KAFKA_SEARCH_TOPIC

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

    @staticmethod
    def reload_search_engine(kafka_producer, cache, timeout, sleep_time):
        """
        Reload the in memory profiles database for search engine, to get the latest profiles data from Redis database.
        :param kafka_producer: kafka producer object
        :param cache: CypressCache object
        :param timeout: server's timeout in seconds, the time to wait for the result of reload request
        :param sleep_time: the time interval for each result check, in seconds
        :return: (True, None) if reload successfully; (False, '<failure reason>') if reload failed.
        :rtype: tuple
        """
        task_id = str(uuid.uuid4())
        start_time = time.time()
        try:
            msg = {'usage': "reload", 'task_id': task_id}

            send_message(kafka_producer, KAFKA_SEARCH_TOPIC, msg)
            while time.time() - start_time < timeout:
                search_result = cache.get_engine_search_task(task_id)
                # from search engine, status is either 'done' or 'error'
                # if status is 'done', result is None; if status is 'error', result is the traceback of the error msg
                if search_result:
                    ret = search_result["status"]
                    if ret == "done":
                        return True, None
                    else:
                        error_msg = json.loads(search_result["result"])
                        return False, str(error_msg)
                time.sleep(sleep_time)
            return False, 'timeout!'
        except Exception:
            raise
        finally:
            cache.delete_engine_search_task(task_id)
