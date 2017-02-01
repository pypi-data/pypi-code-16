"""
Cypress Cache module provides a common library for cache objects using Redis cache.
"""
import numpy
import redis
import time
from .logger_helper import get_logger

CATEGORY_PREFIX = 'profile:category:'
PROFILE_NP_PREFIX = 'profile:np:'
CATEGORY_HASH_NAME = 'profile:category'
VECTOR_HASH_NAME = 'profile:vector'

TARGET_NP_PREFIX = 'target:np:'
TARGET_VECTOR_HASH_NAME = 'target:vector'

ENGINE_SEARCH_HASH_NAME_PREFIX = 'engine:search:'
ENGINE_DETECTION_HASH_NAME_PREFIX = 'engine:detection:'
ENGINE_RECOGNITION_HASH_NAME_PREFIX = 'engine:recognition:'

DATA_IMPORT_HASH_NAME = 'data_import'
DB_IMPORT_ERROR = 'error'
DB_IMPORT_SUCCESS = 'success'
DB_IMPORT_TOTAL = 'total'

PROCESSOR_TASK_PREFIX = 'worker:'
VIDEO_TOTAL_FRAMES_PREFIX = 'video_frames:'


class CypressCache(object):
    """
    CypressCache class for using Redis as cache server
    """
    def __init__(self, host='localhost', port=6379, encoding='utf-8', unittest=False):
        """
        Connect to the Redis server.
        :param host: Redis server host name or IP.
        :type host: basestring
        :param port: Redis server port number.
        :type port: int
        :param encoding: Redis encoding.
        :type encoding: basestring
        """
        self.unittest = unittest
        self.logger = get_logger(self.__class__.__name__, verbose=True)
        self.host = host
        self.port = port
        self.encoding = encoding
        self.redis = None
        self.connect_to_redis()

    ##############################################################
    ###### General Functions ######
    ##############################################################

    def connect_to_redis(self):
        redis_retry_counter = 0
        while True:
            try:
                self.redis = redis.Redis(host=self.host, port=self.port, encoding=self.encoding)
                ret = self.redis.ping()
                if ret:
                    break
            except redis.RedisError and redis.ConnectionError:
                time.sleep(1.0)
                redis_retry_counter += 1
                self.logger.info("Retry connect to Redis host [{0}:{1}]. Retry [{2}]"
                                 .format(self.host, self.port, str(redis_retry_counter)))
                continue

    def is_key_exists(self, name):
        """
        Returns a boolean indicating whether a key "name" exists.
        :param name: the name of the key
        :return: True if the key exists; False if the key doesn't exists.
        """
        redis_retry_counter = 0
        while True:
            try:
                return self.redis.exists(name)
            except redis.ConnectionError:
                redis_retry_counter += 1
                self.connect_to_redis()

    def is_key_exists_in_hash(self, name, key):
        """
        Returns a boolean indicating if "key" exists within hash "name".
        :param name: the hash name
        :param key: the key within the hash name
        :return: True if the key exists within hash "name"; False if the key doesn't exists within hash "name".
        """
        redis_retry_counter = 0
        while True:
            try:
                return self.redis.hexists(name, key)
            except redis.ConnectionError:
                redis_retry_counter += 1
                self.connect_to_redis()

    def get_keys_by_hash_name(self, name):
        """
        Return the list of keys within hash ``name``
        :param name: hash name
        :return: the list of keys within hash ``name``
        """
        redis_retry_counter = 0
        while True:
            try:
                return self.redis.hkeys(name)
            except redis.ConnectionError:
                redis_retry_counter += 1
                self.connect_to_redis()

    def get_all_by_hash_name(self, name):
        """
        Return a Python dict of the hash's name/value pairs
        :param name: The hash name to query
        :return: The object mapped to the hash name as a python dictionary
        """
        redis_retry_counter = 0
        while True:
            try:
                return self.redis.hgetall(name)
            except redis.ConnectionError:
                redis_retry_counter += 1
                self.connect_to_redis()

    def get_kv_by_hash_name(self, name, key):
        """
        Return the value of ``key`` within the hash ``name``
        :param name: hash name to query
        :param key: key within the hash name to get the value for
        :return: the value of ``key`` within the hash ``name``
        """
        redis_retry_counter = 0
        while True:
            try:
                return self.redis.hget(name, key)
            except redis.ConnectionError:
                redis_retry_counter += 1
                self.connect_to_redis()

    def set_kv_to_hash(self, name, key, value):
        """
        Set a key value pair to a hash name.
        :param name: hash name to be set
        :param key: the key within the hash name to add/update
        :param value: the value of the key to be set
        :return:
        """
        redis_retry_counter = 0
        while True:
            try:
                return self.redis.hset(name, key, value)
            except redis.ConnectionError:
                redis_retry_counter += 1
                self.connect_to_redis()

    def set_mkv_to_hash(self, name, mapping):
        """
        Set key to value within hash ``name`` for each corresponding key and value from the ``mapping`` dict.
        :param name: hash name to be set
        :param mapping: a dictionary object contains one ore more key value pairs
        :return:
        """
        redis_retry_counter = 0
        while True:
            try:
                return self.redis.hmset(name, mapping)
            except redis.ConnectionError:
                redis_retry_counter += 1
                self.connect_to_redis()

    def get_value_by_key(self, key):
        """
        Return the value at key ``key``, or None if the key doesn't exist
        :param key: key to query
        :return: the value at key ``key``, or None if the key doesn't exist
        """
        redis_retry_counter = 0
        while True:
            try:
                return self.redis.get(key)
            except redis.ConnectionError:
                redis_retry_counter += 1
                self.connect_to_redis()

    def set_value_to_key(self, key, value):
        """
        Set the value at key ``key`` to ``value``
        :param key: the key to set
        :param value: the value of the key to set
        :return:
        """
        redis_retry_counter = 0
        while True:
            try:
                return self.redis.set(key, value)
            except redis.ConnectionError:
                redis_retry_counter += 1
                self.connect_to_redis()

    def delete_keys(self, *key):
        """
        Delete one or more keys specified by ``names``
        :param key: the key to delete
        :type key: string or tuple or list
        :return:
        """
        redis_retry_counter = 0
        while True:
            try:
                return self.redis.delete(*key)
            except redis.ConnectionError:
                redis_retry_counter += 1
                self.connect_to_redis()

    def delete_keys_from_hash(self, name, *key):
        """
        Delete one or more ``keys`` from hash ``name``
        :param name: the hash name
        :param key: the key within the hash name to delete
        :type key: string or tuple or list
        :return:
        """
        redis_retry_counter = 0
        while True:
            try:
                return self.redis.hdel(name, *key)
            except redis.ConnectionError:
                redis_retry_counter += 1
                self.connect_to_redis()

    ##############################################################
    ###### Video Processor Functions ######
    ##############################################################
    def add_task_to_worker(self, worker_id, task_id, task):
        """
        Add an offline processor task
        :param worker_id: the id of the offline processor worker
        :type worker_id: basestring or uuid
        :param task: video file name with extension
        :type task: basestring
        :return:
        """
        key = PROCESSOR_TASK_PREFIX + str(worker_id)
        self.set_kv_to_hash(key, "task_id", task_id)
        self.set_kv_to_hash(key, "task", task)

    def get_task_by_worker_id(self, worker_id):
        """
        Get the task by worker id
        :param worker_id: the id of the offline processor worker
        :type worker_id: basestring or uuid
        :return:
        """
        key = PROCESSOR_TASK_PREFIX + str(worker_id)
        return self.get_kv_by_hash_name(key, "task")

    def get_task_id_by_worker_id(self, worker_id):
        """
        Get the task by worker id
        :param worker_id: the id of the offline processor worker
        :type worker_id: basestring or uuid
        :return:
        """
        key = PROCESSOR_TASK_PREFIX + str(worker_id)
        return self.get_kv_by_hash_name(key, "task_id")

    def remove_worker_task(self, worker_id):
        """
        Delete the worker task
        :param worker_id: the id of the offline processor worker
        :type worker_id: basestring or uuid
        :return:
        """
        key = PROCESSOR_TASK_PREFIX + str(worker_id)
        self.delete_keys(key)

    def set_task_total_frames(self, task_id, total):
        key = VIDEO_TOTAL_FRAMES_PREFIX+str(task_id)
        self.set_value_to_key(key, total)

    def get_task_total_frames(self, task_id):
        key = VIDEO_TOTAL_FRAMES_PREFIX + str(task_id)
        return self.get_value_by_key(key)

    def delete_task_total_frames_key(self, task_id):
        key = VIDEO_TOTAL_FRAMES_PREFIX + str(task_id)
        self.delete_keys(key)

    ##############################################################
    ###### AC Utility Functions ######
    ##############################################################

    def get_category_id(self, image_id):
        """
        Get category id by image id.
        :param image_id: the id of the image to check
        :type image_id: basestring or UUID
        :return: category id if image exists; None if image does not exist
        """
        image_id = str(image_id)
        category_id = self.get_kv_by_hash_name(CATEGORY_HASH_NAME, image_id)
        return category_id

    def is_category_exists(self, category_id):
        """
        Check if category exists in database
        :param category_id: the 2 digits represents the category
        :type category_id: basestring
        :return: True if exists; False if not exist
        """
        key = CATEGORY_PREFIX + str(category_id)
        return self.is_key_exists(key)

    def add_category(self, category_id, description):
        """
        Add a new category to the database.
        i.e. {"sclb:02":  "XJ"}
        :param category_id: The 2 digits string represents the category
        :type category_id: basestring
        :param description: the description of the category
        :type description: basestring
        :return: False with a http code (as a tuple) if failed to add a category; True with a 201 code if added successfully.
        :rtype: tuple
        """
        key = CATEGORY_PREFIX + str(category_id)
        if self.is_key_exists(key):
            self.logger.warning('Category already exists: ' + key)
            return False, 409
        if self.set_value_to_key(key, description) == 1:
            return True, 201
        self.logger.error('Failed to add category: {} to the database.'.format(category_id))
        return False, 500

    def get_all_categories(self):
        """
        Get a list of category ids in the database.
        i.e. ['00','01','03']
        :return: a list of category ids from the database. Empty list if there's no category found.
        """
        results = []
        match = CATEGORY_PREFIX+'*'
        for k in self.redis.keys(pattern=match):
            category_id = k.split(':')[-1]
            results.append(category_id)
        return results

    def get_category_description(self, category_id):
        """
        Get a category description by category id.
        :param category_id: The id of the category to query
        :type category_id: basestring
        :return: The description of the input category. None if category does not exist.
        """
        category_id = str(category_id)
        if not self.is_category_exists(category_id):
            self.logger.warning('Category does not exist: {0}'.format(category_id))
            return None

        key = CATEGORY_PREFIX + category_id
        desc = self.get_value_by_key(key)
        return desc

    def clear_category(self, category_id):
        """
        Delete all category associated image information from database, without deleting the category information.
        -1. delete from profile vector hash table
        -2. delete from profile category hash table
        -3. delete profile np hash table
        :param category_id: The id of the category to delete
        :type category_id: basestring
        :return: True if cleared successfully (no matter it exist or not)
        """
        category_id = str(category_id)
        if not self.is_category_exists(category_id):
            self.logger.warning('Category does not exist in category table: {0}'.format(category_id))

        profile_ids = self.get_profile_ids_by_category(category_id)

        if profile_ids:
            cat_profile_ids = []
            np_profile_hashes = []
            for image_id in profile_ids:
                cat_profile_ids.append(category_id + ':' + image_id)
                np_profile_hashes.append(PROFILE_NP_PREFIX + image_id)

            # 1. delete from profile vector hash table
            self.delete_keys_from_hash(VECTOR_HASH_NAME, *cat_profile_ids)
            # 2. delete from profile category hash table
            self.delete_keys_from_hash(CATEGORY_HASH_NAME, *profile_ids)
            # 3. delete from profile np hash table
            self.delete_keys(*np_profile_hashes)
        else:
            self.logger.info('No profile is found for category: {0}'.format(category_id))

        return True

    def delete_category(self, category_id):
        """
        Delete a category with all associated image information from database by category id.
        -1. delete from profile vector hash table
        -2. delete from profile category hash table
        -3. delete profile np hash table
        -4. delete profile category table
        :param category_id: The id of the category to delete
        :type category_id: basestring
        :return: True if deleted successfully (no matter it exist or not), False if delete failed
        """
        category_id = str(category_id)
        if not self.is_category_exists(category_id):
            self.logger.warning('Category does not exist in category table: {0}'.format(category_id))

        profile_ids = self.get_profile_ids_by_category(category_id)

        if profile_ids:
            cat_profile_ids = []
            np_profile_hashes = []
            for image_id in profile_ids:
                cat_profile_ids.append(category_id + ':' + image_id)
                np_profile_hashes.append(PROFILE_NP_PREFIX + image_id)

            # 1. delete from profile vector hash table
            self.delete_keys_from_hash(VECTOR_HASH_NAME, *cat_profile_ids)
            # 2. delete from profile category hash table
            self.delete_keys_from_hash(CATEGORY_HASH_NAME, *profile_ids)
            # 3. delete from profile np hash table
            self.delete_keys(*np_profile_hashes)
        else:
            self.logger.info('No profile is found for category: {0}'.format(category_id))

        # 4. delete from profile category table
        cat_key = CATEGORY_PREFIX + category_id
        delete_task = self.delete_keys(cat_key)
        return delete_task == 1 or delete_task == 0

    def add_image_to_profiles(self, image_id, category_id, np_bytes, axis0, axis1):
        """
        Add a new image with numpy array bytes, dimension information to the database, associate with a category.
        Add a category if the input category doesn't exist already.
        The image will be one of the profiles, a search will be against these profiles.
        i.e. {"profile:np:<image_id1>": {"matrix":"<numpy array bytes>", "axis0": "2", "axis1": "5"}}
        { "profile:category": {"id1": "00", "id3": "01", ......} }
        { "profile:category:<category_id1>":  "YN"}
        :param image_id: The id of the image to create
        :type image_id: basestring or UUID
        :param category_id: the 2 digits string represents the category that is associated with the image
        :type category_id: basestring
        :param np_bytes: the numpy array of the image in bytes. The image must be in mode 'BGR'!
        :type np_bytes: bytes
        :param axis0: numpy array dimension, the first element in the tuple
        :type axis0: int
        :param axis1: numpy array dimension, the second element in the tuple
        :type axis1: int
        :return: False if failed to add a new image; True if added successfully.
        """
        category_id = str(category_id)
        image_id = str(image_id)

        # If category does not exist, then add the category to the database. i.e. { "cslb:02":  "XJ"}
        if not self.is_category_exists(category_id):
            if not self.add_category(category_id, category_id)[0]:
                return False

        np_hash_name = PROFILE_NP_PREFIX + image_id

        if self.is_key_exists(np_hash_name):
            self.logger.warning('Image already exists: ' + np_hash_name)
            return False
        if self.is_key_exists_in_hash(CATEGORY_HASH_NAME, image_id):
            self.logger.warning('Image already exists in category hash table: ' + image_id)
            return False

        hash_mapping = {'matrix': np_bytes, 'axis0': axis0, 'axis1': axis1}
        set_np = self.set_mkv_to_hash(np_hash_name, hash_mapping)
        set_category = self.set_kv_to_hash(CATEGORY_HASH_NAME, image_id, category_id)
        return set_np == 1 and set_category == 1

    def add_image_to_targets(self, image_id, np_bytes, axis0, axis1):
        """
        Add a new image with numpy array bytes, dimension information to the database, without category information.
        The image will be the target image to search against the profile database.
        i.e. { "target:np:id1": {"matrix":"<matrix bytes>", "axis0": "34", "axis1": "54"} }
        :param image_id: the id of the image to create
        :type image_id: basestring or UUID
        :param np_bytes: the numpy array of the image in bytes. The image must be in mode 'BGR'!
        :type np_bytes: bytes
        :param axis0: numpy array dimension, the first element in the tuple
        :type axis0: int
        :param axis1: numpy array dimension, the second element in the tuple
        :type axis1: int
        :return: False if image already exists; True if add image succeed.
        """
        image_id = str(image_id)
        hash_name = TARGET_NP_PREFIX + image_id

        if self.is_key_exists(hash_name):
            self.logger.warning('Image already exists in target image hash table: ' + hash_name)
            return False

        hash_mapping = {'matrix': np_bytes, 'axis0': axis0, 'axis1': axis1}
        set_target_zp = self.set_mkv_to_hash(hash_name, hash_mapping)
        return set_target_zp == 1

    def add_vector_to_profile(self, image_id, vector):
        """
        Add image vector information to an image in profiles database.
        i.e. { "profile:vector": {"00:id1": "vector2", "01:id3": "vector3", ......} }
        :param image_id: the id of the image to add vector information
        :type image_id: basestring or UUID
        :param vector: the vector information of the face image
        :type vector: bytes
        :return: False if failed to add vector to profile; True if succeed.
        """
        image_id = str(image_id)
        category_id = self.get_category_id(image_id)
        if not category_id:
            self.logger.warning('Image does not exist: ' + image_id)
            return False

        vector_key = str(category_id) + ':' + image_id
        if self.is_key_exists_in_hash(VECTOR_HASH_NAME, vector_key):
            self.logger.warning('Vector already exists: ' + vector_key)
            return False
        set_vector = self.set_kv_to_hash(VECTOR_HASH_NAME, vector_key, vector)
        return set_vector == 1

    def add_vector_to_target(self, image_id, vector):
        """
        Add image vector information to an image in targets database.
        i.e. { "target:vector": {"id1": "vector2", "id3": "vector3", ......} }
        :param image_id: the id of the image to add vector information
        :type image_id: basestring or UUID
        :param vector: the vector information of the face image
        :type vector: bytes
        :return: False if failed to add vector to target; True if succeed.
        """
        image_id = str(image_id)

        if self.is_key_exists_in_hash(TARGET_VECTOR_HASH_NAME, image_id):
            self.logger.warning('Vector already exists: ' + image_id)
            return False
        set_vector = self.set_kv_to_hash(TARGET_VECTOR_HASH_NAME, image_id, vector)
        return set_vector == 1

    def get_vector_from_profiles(self, image_id):
        """
        Get vector information of an image from the profile database.
        :param image_id: the id of the image used to get the vector information
        :type image_id: basestring or UUID
        :return: vector information if there's one
        """
        image_id = str(image_id)
        category_id = self.get_category_id(image_id)
        if not category_id:
            self.logger.warning('Image does not exist: ' + image_id)
            return None

        vector_key = category_id + ':' + image_id
        value = self.get_kv_by_hash_name(VECTOR_HASH_NAME, vector_key)
        if not value:
            self.logger.warning('Vector information does not exist.')
            return None
        return value

    def get_vector_from_targets(self, image_id):
        """
        Get vector information of an image from the targets database.
        :param image_id: the id of the image used to get the vector information
        :type image_id: basestring or UUID
        :return: vector information if there's one
        """
        image_id = str(image_id)
        value = self.get_kv_by_hash_name(TARGET_VECTOR_HASH_NAME, image_id)
        if not value:
            self.logger.warning('Vector information does not exist.')
            return None
        return value

    def get_np_image_by_id(self, image_id, usage='profile'):
        """
        Read the image object from targets database by image_id, reshape the one dimensional array to
         mutli-dimension array using the `axis0` and `axis1`. Return the image in np.ndarray format.
        :param image_id: image id
        :type image_id: basestring or uuid
        :param usage: The usage passed in from engine. Default to 'profile', anything else goes to targets db
        :type usage: basestring
        :return: on success - reshaped image in ndarray (The image is in mode 'BGR'!); on failure - None
        """
        try:
            if usage == 'profile':
                img_obj = self.get_np_from_profiles(image_id)
            else:
                img_obj = self.get_np_from_targets(image_id)
            image = numpy.frombuffer(img_obj.get('matrix'), dtype=numpy.uint8)\
                .reshape(int(img_obj.get('axis0')), int(img_obj.get('axis1')), 3)
            return numpy.copy(image)
        except AttributeError as e:
            self.logger.error("Failed to reshape image. msg={0}".format(str(e)))
            return None

    def get_np_from_profiles(self, image_id):
        """
        Get image numpy array in bytes information of an image from the profiles database.
        :param image_id: the id of the image used to get the numpy array bytes information
        :type image_id: basestring or UUID
        :return: dictionary object, image numpy array bytes with dimension information if there's one.
        Note: The image is in mode 'BGR'!
        i.e.  {'matrix': 'np bytes', 'axis0': '23', 'axis1': '32'}
        Return None if not found.
        """
        image_id = str(image_id)
        hash_name = PROFILE_NP_PREFIX + image_id
        obj = self.get_all_by_hash_name(hash_name)
        if not obj:
            self.logger.warning('Image numpy array information does not exist.')
            return None
        return obj

    def delete_profile(self, image_id):
        """
        Remove an image (np data, vector data, categroy data) in profiles database.
        The three data structures to operate on:
        { "profile:vector": {"<category_id1>:<image_id1>": "vector2", "<category_id2>:<image_id3>": "vector3", ......} }
        { "profile:np:<image_id1>": {"matrix":"<numpy array bytes>", "axis0": "2", "axis1": "5"} }
        { "profile:category": {"<image_id1>": "00", "<image_id3>": "01", ......} }
        :param image_id: the id of the image to delete
        :type image_id: basestring or uuid
        :return: (True, 204) if deleted; (False, 404) if image does not exist in profiles database
        :rtype: tuple
        """
        image_id = str(image_id)

        category_id = self.get_category_id(image_id)
        vector_key = str(category_id) + ':' + image_id
        np_hash_name = PROFILE_NP_PREFIX + image_id

        del_vector = self.delete_keys_from_hash(VECTOR_HASH_NAME, vector_key)
        del_np = self.delete_keys(np_hash_name)
        del_cat = self.delete_keys_from_hash(CATEGORY_HASH_NAME, image_id)

        if not del_np and not del_vector and not del_cat:
            self.logger.warning('Image does not exist in profiles database.')
            return False, 404
        return True, 204

    def get_np_from_targets(self, image_id):
        """
        Get image numpy array in bytes information of an image from the targets database.
        :param image_id: the id of the image used to get the numpy array bytes information
        :type image_id: basestring or UUID
        :return: dictionary object, image numpy array bytes with dimension information if there's one.
        Note: The image is in mode 'BGR'!
        i.e.  {'matrix': 'np bytes', 'axis0': '23', 'axis1': '32'}
        Return None if not found.
        """
        image_id = str(image_id)
        hash_name = TARGET_NP_PREFIX + image_id
        obj = self.get_all_by_hash_name(hash_name)
        if not obj:
            self.logger.warning('Image numpy array information does not exist.')
            return None
        return obj

    def delete_target(self, image_id):
        """
        Remove an image (np data and vector data) in targets database.
        The two data structures to operate on:
        { "target:vector": {"<image_id1>": "vector2", "<image_id3>": "vector3", ......} }
        { "target:np:<image_id1>":  {"matrix":"<numpy array bytes>", "axis0": "34", "axis1": "54"} }
        :param image_id: the id of the image to delete
        :type image_id: basestring or uuid
        :return: True if deleted; False if image does not exist in targets database.
        """
        image_id = str(image_id)
        del_vector = None
        del_np = None

        if not self.is_key_exists_in_hash(TARGET_VECTOR_HASH_NAME, image_id):
            self.logger.warning('Image does not exist in target vector hash table: {0}'.format(image_id))
        else:
            del_vector = self.delete_keys_from_hash(TARGET_VECTOR_HASH_NAME, image_id)

        np_hash_name = TARGET_NP_PREFIX + image_id
        if not self.is_key_exists(np_hash_name):
            self.logger.warning('Image does not exist in target np hash table: {0}'.format(image_id))
        else:
            del_np = self.delete_keys(np_hash_name)

        if not del_np and not del_vector:
            self.logger.warning('Image does not exist in targets database.')
            return False
        return True

    def get_all_profile_vectors(self, use_float16=False):
        """
        Return a tuple with two elements: array of profile ids, array of profile vectors.
        :return: a tuple with two elements: array of profile ids with category data, array of profile vectors.
        ['01:image_id_1', '04:image_id_2'], ['vector1', 'vector2']
        Return empty arrays if no result is found.
        """
        profile_ids = []
        profile_vectors = []
        for k, v in self.redis.hscan_iter(VECTOR_HASH_NAME):
            # get the second part of the key (image id)
            profile_ids.append(k)
            vec_32 = numpy.frombuffer(v, dtype=numpy.float32)

            if use_float16 is True:
                vec_16 = numpy.array(vec_32, dtype=numpy.float32)
                profile_vectors.append(vec_16)
            else:
                profile_vectors.append(vec_32)

        if use_float16 is True:
            np_profile_vectors = numpy.asarray(profile_vectors, dtype=numpy.float16)
        else:
            np_profile_vectors = numpy.asarray(profile_vectors, dtype=numpy.float32)

        # return empty python list, not np list if np list is empty
        if np_profile_vectors.size == 0:
            return profile_ids, []
        else:
            return profile_ids, np_profile_vectors

    def get_all_profile_ids(self):
        """
        Return a full list of image ids from the profiles database.
        :return: a full list of image ids in the profiles database; empty array if there's none
        """
        return self.get_keys_by_hash_name(CATEGORY_HASH_NAME)

    def get_profile_ids_by_category(self, category_id):
        """
        Return a list of image ids that are associated with input category from the profile database
        :param category_id: the id of the category as a filter to query the image ids
        :type category_id: basestring
        :return: a list of image ids that are associated with input category from the profile database; empty array if there's none
        """
        results = []
        category_id = str(category_id)
        if not self.is_category_exists(category_id):
            self.logger.warning('Category does not exist: ' + category_id)
            return None

        # assume "profile:vector" hash table consists all images with vector info
        for k, v in self.redis.hscan_iter(name=VECTOR_HASH_NAME, match=category_id + ':*'):
            # get the second part of the key (image id)
            image_id = k.split(':')[-1]
            results.append(image_id)
        return results

    def set_engine_search_task(self, task_id, status, result):
        """
        Set status and result to an engine search task.
        i.e. { "engine:search:<task_id>": {"status": 'success', "result": "json msg in str format"}
        :param task_id: the id of the task to set result and status
        :type task_id: basestring or uuid
        :param status: task status
        :type status: basestring
        :param result: face search result
        :type result: json in string format
        :return: True if set successfully, False if set failed
        """
        task_id = str(task_id)
        hash_name = ENGINE_SEARCH_HASH_NAME_PREFIX + task_id
        hash_mapping = {'result': result, 'status': status}
        set_obj = self.set_mkv_to_hash(hash_name, hash_mapping)
        return set_obj == 1 or set_obj == 0

    def get_engine_search_task(self, task_id):
        """
        Get status and result of an engine search task
        :param task_id: the id of the task to set result and status
        :type task_id: basestring or uuid
        :return: a dictionary contains task's status, result. None if no record is found
        i.e. {"status": 'success', "result": "json msg in str format"}
        """
        task_id = str(task_id)
        hash_name = ENGINE_SEARCH_HASH_NAME_PREFIX + task_id
        obj = self.get_all_by_hash_name(hash_name)
        if not obj:
            self.logger.warning('Engine search task information does not exist: {0}'.format(task_id))
            return None
        return obj

    def delete_engine_search_task(self, task_id):
        """
        Delete an engine search task from database
        :param task_id: the id of the task to remove
        :type task_id: basestring or uuid
        :return: True if deleted (no matter the task id exists or not), False if failed to delete
        """
        task_id = str(task_id)
        hash_name = ENGINE_SEARCH_HASH_NAME_PREFIX + task_id
        if not self.is_key_exists(hash_name):
            self.logger.warning('Engine search task does not exist: {0}'.format(task_id))
        delete_task = self.delete_keys(hash_name)
        return delete_task == 1 or delete_task == 0

    def set_engine_detection_task(self, task_id, error_code, results):
        """
        Set error code and results number to an engine detection task.
        i.e.  { "engine:detection:<task_id>": {"error": '0', "results": '3'} }
        :param task_id: the id of the task to set result and status
        :type task_id: basestring or uuid
        :param error_code: task error code, follow the error code in kafka interface.
        :type error_code: int
        :param results: detected face numbers
        :type results: int
        :return: True if set successfully, False if set failed
        """
        task_id = str(task_id)
        hash_name = ENGINE_DETECTION_HASH_NAME_PREFIX + task_id
        hash_mapping = {'results': results, 'error': error_code}
        set_obj = self.set_mkv_to_hash(hash_name, hash_mapping)
        return set_obj == 1 or set_obj == 0

    def get_engine_detection_task(self, task_id):
        """
        Get error code and results number of an engine detection task
        :param task_id: the id of the task to set result and status
        :type task_id: basestring or uuid
        :return: a dictionary contains task's error code, results number. None if no record is found
        i.e. {"error": '0', "results": '3'}
        """
        task_id = str(task_id)
        hash_name = ENGINE_DETECTION_HASH_NAME_PREFIX + task_id
        obj = self.get_all_by_hash_name(hash_name)
        if not obj:
            self.logger.warning('Engine detection task information does not exist: {0}'.format(task_id))
            return None
        return obj

    def delete_engine_detection_task(self, task_id):
        """
        Delete an engine detection task from database
        :param task_id: the id of the task to remove
        :type task_id: basestring or uuid
        :return: True if deleted (no matter the task id exists or not), False if failed to delete
        """
        task_id = str(task_id)
        hash_name = ENGINE_DETECTION_HASH_NAME_PREFIX + task_id
        if not self.is_key_exists(hash_name):
            self.logger.warning('Engine detection task does not exist: {0}'.format(task_id))
        delete_task = self.delete_keys(hash_name)
        return delete_task == 1 or delete_task == 0

    def set_engine_recognition_task(self, task_id, face_id, result):
        """
        Set a face result to an engine recognition task.
        i.e.  { "engine:recognition:<task_id>": {"<face_id1>": 'recognition result as a json object in string format',
        "<face_id2>": 'recognition result as a json object in string format', ...} }
        :param task_id: the id of the task to set result and status
        :type task_id: basestring or uuid
        :param face_id: the id of the recognized face
        :type face_id: basestring or uuid
        :param result: result contains face information such as bounding box, vector.
            result = {"x": x,
                      "y": y,
                      "w": width,
                      "h": height,
                      "vector": vec}
            result = json.dumps(result)
        :type result: basestring
        :return: True if set successfully, False if set failed
        """
        task_id = str(task_id)
        face_id = str(face_id)
        hash_name = ENGINE_RECOGNITION_HASH_NAME_PREFIX + task_id
        set_obj = self.set_kv_to_hash(hash_name, face_id, result)
        return set_obj == 1 or set_obj == 0

    def get_engine_recognition_task(self, task_id):
        """
        Get results of an engine recognition task
        :param task_id: the id of the task to set result and status
        :type task_id: basestring or uuid
        :return: a dictionary contains one or more faces with bounding box and vector information of a task.
        None if no record is found.
        i.e.  {"<face_id1>": 'recognition result as a json object in string format'}
        """
        task_id = str(task_id)
        hash_name = ENGINE_RECOGNITION_HASH_NAME_PREFIX + task_id
        obj = self.get_all_by_hash_name(hash_name)
        if not obj:
            self.logger.warning('Engine recognition task information does not exist: {0}'.format(task_id))
            return None
        return obj

    def delete_engine_recognition_task(self, task_id):
        """
        Delete an engine recognition task from database
        :param task_id: the id of the task to remove
        :type task_id: basestring or uuid
        :return: True if deleted (no matter the task id exists or not), False if failed to delete
        """
        task_id = str(task_id)
        hash_name = ENGINE_RECOGNITION_HASH_NAME_PREFIX + task_id
        if not self.is_key_exists(hash_name):
            self.logger.warning('Engine recognition task does not exist: {0}'.format(task_id))
        delete_task = self.delete_keys(hash_name)
        return delete_task == 1 or delete_task == 0

    def set_data_import_stats(self, status, count):
        """
        Update the processed stats for data import service, including the counts for success, fail, and total number of records.
        :param status: the key in the hash mapping: 'success', 'error', 'total'
        :type status: basestring
        :param count: the number of records being processed for the specified status
        :type count: int
        :return: True if set successfully, False if set failed.
        """
        status_list = [DB_IMPORT_ERROR, DB_IMPORT_SUCCESS, DB_IMPORT_TOTAL]
        if status not in status_list:
            self.logger.error('Failed to set data import stats, the input status does not exist: {0}'.format(status))
            raise IOError('Unrecognized input status value.')
        count = int(count)
        # create or update the count for status
        set_count = self.set_kv_to_hash(DATA_IMPORT_HASH_NAME, status, count)
        return set_count == 1 or set_count == 0

    def get_data_import_stats(self, status=None):
        """
        Get the stats for data import service.
        :param status Default to None.
        :type status basestring
        :return:
        - If input status is None: return a dictionary contains all status.
        i.e.  {"success": "0", "error": "0", "total": "0"}
        - If input status is in status list: return an integer represent the count of the input status.
        i.e. 3
        - If no result found for status that is in status_list, return 0.
        - If input status is not in status_list,
        """
        status_list = [DB_IMPORT_ERROR, DB_IMPORT_SUCCESS, DB_IMPORT_TOTAL]
        if not status:
            obj = self.get_all_by_hash_name(DATA_IMPORT_HASH_NAME)
            if not obj:
                self.logger.warning('Data import stats does not exist.')
                return None
            return obj
        if status and status in status_list:
            count = self.get_kv_by_hash_name(DATA_IMPORT_HASH_NAME, status)
            if not count:
                return 0
            return int(count)
        if status and status not in status_list:
            self.logger.error('Input status is not a part of the data import stats status: {0}'.format(status))
            raise IOError('Unrecognized input status value.')
