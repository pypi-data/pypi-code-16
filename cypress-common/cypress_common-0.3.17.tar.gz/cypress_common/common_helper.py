# This Python file uses the following encoding: utf-8
import numpy as np
import uuid
import time
from PIL import Image
from scipy import misc
from .kafka_helper import KAFKA_SEARCH_TOPIC
import os

# system default image type
DEFAULT_IMAGE_TYPE = 'jpeg'
# system supported image types
SUPPORTED_IMAGE_TYPES = ["jpeg", "jpg", "png", "bmp", "tiff"]
# path to save original image when profile creation failed
FAILED_PROFILE_PATH = '/images/profile_failed'
# path to save original image after profile creation succeed
ORIG_SUCCEED_PROFILE_PATH = '/images/profile_original'
# path to save cropped face after profile creation succeed
CROPPED_SUCCEED_PROFILE_PATH = '/images/profile_cropped'
# path to save original image after target face (internal db) creation succeed
ORIG_TARGET_PATH = '/images/target_original'
# path to save cropped face after target face (internal db) creation succeed
CROPPED_TARGET_PATH = '/images/target_cropped'
# path to save cropped faces from video process (matched and unmatched):
MATCHED_VIDEO_PROCESSED_FACE_PATH = '/images/video_processed/matched'
UNMATCHED_VIDEO_PROCESSED_FACE_PATH = '/images/video_processed/unmatched'


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
        :param np_bgr: the numpy array of the image in mode 'BGR'
        :type np_bgr: numpy array
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
    def np_bgr_2_img_rgb(np_bgr):
        """
        Convert a 'BGR' image numpy array to a 'RGB' image object.
        :param np_bgr: the numpy array of the image in mode 'BGR'
        :type np_bgr: numpy array
        :return: the image object in 'RGB' mode
        :rtype: `~PIL.Image.Image` object
        """
        np_rgb = CypressCommonHelper.np_bgr2rgb(np_bgr)
        return misc.toimage(np_rgb)

    @staticmethod
    def save_file_to_fs(file_path, file_name, file_obj):
        """
        Save a file to file system.
        :param file_path: The absolute path to the directory the file should be saved, excluding the file name
        :type file_path: str
        :param file_name: The file name including extension
        :type file_name: str
        :param file_obj: The file object must implement :py:meth:`~file.read`,
                    :py:meth:`~file.seek`, and :py:meth:`~file.tell` methods, and be opened in binary mode.
        :return:
        """
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        if file_name.split(".")[-1].lower() not in SUPPORTED_IMAGE_TYPES:
            raise IOError("File type not supported, must be one of jpeg, jpg, bmp, tiff or png.")

        full_path = os.path.join(file_path, file_name)
        with open(full_path, 'wb') as f:
            f.write(file_obj)

    @staticmethod
    def save_np_bgr_to_fs(file_path, file_name, np_bgr):
        """
        Save a numpy array in BGR order as an image file to file system.
        :param file_path: The absolute path to the directory the file should be saved, excluding the file name
        :type file_path: str
        :param file_name: The file name including extension
        :type file_name: str
        :param np_bgr: the numpy array of the image in mode 'BGR'
        :param np_bgr: the numpy array of the image in mode 'BGR'
        :return:
        """
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        image_type = file_name.split(".")[-1]
        if image_type not in SUPPORTED_IMAGE_TYPES:
            raise IOError("File type not supported, must be one of jpeg, jpg, bmp, tiff or png.")

        img_rgb = CypressCommonHelper.np_bgr_2_img_rgb(np_bgr)
        img_rgb.save(os.path.join(file_path, file_name), format=image_type)

    @staticmethod
    def remove_file_from_fs(file_name):
        """
        Remove a file from file system.
        :param file_name: The absolute path of the file to delete, including file name with extension
        :type file_name: str
        :return:
        """
        if not os.path.isfile(file_name):
            raise IOError("The file : {} doesn't exist.".format(file_name))

        os.remove(file_name)

    @staticmethod
    def reload_search_engine(kafka_producer_obj, cache, timeout, sleep_time, task_name=None):
        """
        Reload the in memory profiles database for search engine, to get the latest profiles data from Redis database.
        :param kafka_producer_obj: PythonKafkaProducer object from kafka_helper
        :param cache: CypressCache object
        :param timeout: server's timeout in seconds, the time to wait for the result of reload request
        :param sleep_time: the time interval for each result check, in seconds
        :param task_name: 'create_profile', 'delete_profile', 'db_import', etc. Default to None.
        :return: (True, None) if reload successfully; (False, '<failure reason>') if reload failed.
        :rtype: tuple
        """
        task_id = str(uuid.uuid4())
        start_time = time.time()
        try:
            msg = {'usage': "reload", 'task_id': task_id, 'task_name': task_name}

            kafka_producer_obj.send_message(KAFKA_SEARCH_TOPIC, msg)
            while time.time() - start_time < timeout:
                search_result = cache.get_engine_search_task(task_id)
                # from search engine, status is either 'done' or 'error'
                # if status is 'done', result is None; if status is 'error', result is the traceback of the error msg
                if search_result:
                    ret = search_result["status"]
                    if ret == "done":
                        return True, None
                    else:
                        error_msg = search_result["result"]
                        return False, str(error_msg)
                time.sleep(sleep_time)
            return False, 'timeout!'
        except Exception:
            raise
        finally:
            cache.delete_engine_search_task(task_id)

    @staticmethod
    def get_current_time_ms():
        return int(round(time.time() * 1000))
